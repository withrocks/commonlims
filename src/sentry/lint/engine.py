"""
Our linter engine needs to run in 3 different scenarios:
 * Linting all files (python, js, less)
 * Linting only python files (--python) [NOTICE: moved to pre-commit]
 * Linting only js files (--js)

For the js only path, we should not depend on any packages outside the
python stdlib to prevent the need to install the world just to run eslint.
"""
from __future__ import absolute_import, print_function


import os
import logging
import sys
import subprocess
import json
from distutils.spawn import find_executable

from subprocess import check_output, Popen
logger = logging.getLogger("lint")

os.environ['PYFLAKES_NODOCTEST'] = '1'
os.environ['SENTRY_PRECOMMIT'] = '1'


class ToolNotFoundException(Exception):
    pass


class IncorrectVersion(Exception):
    pass


def execute_subprocess(cmd, args):
    logger.info("Begin subprocess {} with {} args".format(cmd, len(args)))
    ret = Popen(cmd + args).wait()
    logger.info("End subprocess")
    return ret


def get_project_root():
    return os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)


def get_bin(path, name):
    path = os.path.abspath(os.path.join(path, name))
    if not os.path.exists(path):
        raise ToolNotFoundException('Tool not found: {}'.format(path))
    return path


def get_sentry_bin(name):
    return get_bin(os.path.join(get_project_root(), 'bin'), name)


def get_node_modules_bin(name):
    return get_bin(os.path.join(get_project_root(), 'node_modules', '.bin'), name)


def get_prettier_path():
    path = get_node_modules_bin('prettier')
    version = subprocess.check_output([path, '--version']).rstrip()

    # Make sure that the prettier tool is using the same version as in package.json:
    require_package_json_version(get_project_root(), 'prettier', version)
    return path


def require_tool_module(module_name):
    try:
        __import__(module_name)
    except ImportError:
        raise ToolNotFoundException('Tool not pip installed: {}'.format(module_name))


def require_exe(exe):
    if not find_executable(exe):
        raise ToolNotFoundException('Tool not available: {}'.format(exe))


def require_git_hooks():
    require_exe('pre-commit')

    # We still have a legacy commit hook file:
    return get_bin(os.path.join(get_project_root(), '.git', 'hooks'), 'pre-commit.legacy')


def get_files(path):
    results = []
    for root, _, files in os.walk(path):
        for name in files:
            results.append(os.path.join(root, name))
    return results


def get_modified_files(path):
    return [
        s
        for s in check_output(['git', 'diff-index', '--cached', '--name-only', 'HEAD']).split('\n')
        if s
    ]


def get_files_for_list(file_list):
    if file_list is None:
        files_to_check = get_files('.')

    else:
        files_to_check = []
        for path in file_list:
            if os.path.isdir(path):
                files_to_check.extend(get_files(path))
            else:
                files_to_check.append(os.path.abspath(path))
    return sorted(set(files_to_check))


def get_js_files(file_list=None, snapshots=False):
    if snapshots:
        extensions = ('.js', '.jsx', '.jsx.snap', '.js.snap')
    else:
        extensions = ('.js', '.jsx')

    if file_list is None:
        file_list = ['tests/js', 'src/sentry/static/sentry/app']
    return [
        x for x in get_files_for_list(file_list)
        if x.endswith(extensions)
    ]


def get_less_files(file_list=None):
    if file_list is None:
        file_list = ['src/sentry/static/sentry/less', 'src/sentry/static/sentry/app']
    return [x for x in get_files_for_list(file_list) if x.endswith(('.less'))]


def get_python_files(file_list=None):
    if file_list is None:
        file_list = ['src', 'tests']
    return [
        x for x in get_files_for_list(file_list)
        if x.endswith('.py')
    ]


def js_lint(file_list=None, parseable=False, format=False, cache=False):
    # We require eslint in path but we actually call an eslint wrapper
    eslint_path = get_node_modules_bin('eslint')
    eslint_wrapper_path = get_sentry_bin('eslint-travis-wrapper')

    js_file_list = get_js_files(file_list, snapshots=True)

    has_errors = False
    if js_file_list:
        if os.environ.get('CI'):
            cmd = [eslint_wrapper_path, '--ext', '.js,.jsx']
        else:
            cmd = [eslint_path, '--ext', '.js,.jsx']

        if format:
            cmd.append('--fix')
        if parseable:
            cmd.append('--format=checkstyle')
        if cache and not os.environ.get('CI'):
            # TODO: It would be possible to cache here to speed up the build, but it requires
            # changing the wrapper script, so waiting with it for now
            cmd.append("--cache")
        status = execute_subprocess(cmd, js_file_list)
        has_errors = status != 0

    return has_errors


def js_stylelint(file_list=None, parseable=False, format=False, cache=False):
    """
    stylelint for styled-components
    """

    # TODO-easy create a decorator for this logging pattern
    logger.info("Begin js_stylelint")
    stylelint_path = get_node_modules_bin('stylelint')

    js_file_list = get_js_files(file_list, snapshots=False)

    has_errors = False
    if js_file_list:
        cmd = [stylelint_path]
        if cache:
            cmd.append("--cache")
        status = execute_subprocess(cmd, js_file_list)
        has_errors = status != 0

    logger.info("End js_stylelint")
    return has_errors


def yarn_check(file_list):
    """
    Checks if package.json was modified WITHOUT a corresponding change in the Yarn
    lockfile. This can happen if a user manually edited package.json without running Yarn.

    This is a user prompt right now because there ARE cases where you can touch package.json
    without a Yarn lockfile change, e.g. Jest config changes, license changes, etc.
    """
    logger.info("Begin yarn_check")
    if file_list is None or os.environ.get('SKIP_YARN_CHECK'):
        return False

    if 'package.json' in file_list and 'yarn.lock' not in file_list:
        print(    # noqa: B314
            '\033[33m' + """Warning: package.json modified without accompanying yarn.lock modifications.

If you updated a dependency/devDependency in package.json, you must run `yarn install` to update the lockfile.

To skip this check, run `SKIP_YARN_CHECK=1 git commit [options]`""" + '\033[0m')
        logger.info("End yarn_check, issues found")
        return True

    logger.info("End yarn_check, no issues found")
    return False


def require_package_json_version(project_root, package, version, section='devDependencies'):
    package_version = None
    package_json_path = os.path.abspath(os.path.join(project_root, 'package.json'))
    with open(package_json_path) as package_json:
        package_version = json.load(package_json)[section][package]

    if version != package_version:
        raise IncorrectVersion('Expected version "{}" of "{}" but got "{}"'.format(version,
            package, package_version))


def js_lint_format(file_list=None):
    """
    We only format JavaScript code as part of this pre-commit hook. It is not part
    of the lint engine. This uses eslint's `--fix` formatting feature.
    """
    logger.info("Begin js_lint_format")
    eslint_path = get_node_modules_bin('eslint')
    get_prettier_path()  # Only checking for the dependency

    js_file_list = get_js_files(file_list)

    # manually exclude some bad files
    js_file_list = [x for x in js_file_list if '/javascript/example-project/' not in x]

    results = run_formatter([eslint_path, '--fix', ],
                         js_file_list)
    logger.info("End js_lint_format")
    return results


def js_test(file_list=None):
    """
    Run JavaScript unit tests on relevant files ONLY as part of pre-commit hook
    """
    logger.info("Begin js_test")
    jest_path = get_node_modules_bin('jest')

    if not os.path.exists(jest_path):
        print('[sentry.test] Skipping JavaScript testing because jest is not installed.')  # noqa: B314
        return False

    js_file_list = get_js_files(file_list)

    has_errors = False
    if js_file_list:
        status = execute_subprocess(['yarn', 'test-precommit'], js_file_list)
        has_errors = status != 0

    logger.info("End js_test")
    return has_errors


def less_format(file_list=None):
    """
    We only format less code as part of this pre-commit hook. It is not part
    of the lint engine.
    """
    logger.info("Begin less_format")
    prettier_path = get_prettier_path()

    less_file_list = get_less_files(file_list)
    result = run_formatter(
        [
            prettier_path,
            '--write',
        ], less_file_list
    )
    logger.info("End less_format")
    return result


def py_format(file_list=None):
    logger.info("Begin py_format")

    require_tool_module('autopep8')

    py_file_list = get_python_files(file_list)

    result = run_formatter([
        'autopep8',
        '--in-place',
        '-j0',
    ], py_file_list)
    logger.info("End py_format")
    return result


def run_formatter(cmd, file_list, prompt_on_changes=True):
    logger.info("Start running formatter: {}".format(cmd))
    if not file_list:
        return False

    has_errors = False

    status = execute_subprocess(cmd, file_list)
    has_errors = status != 0
    if has_errors:
        logger.info("End running formatter: {}".format(cmd))
        return True

    # this is not quite correct, but it at least represents what would be staged
    output = subprocess.check_output(['git', 'diff', '--color'] + file_list)
    if output:
        print('[sentry.lint] applied changes from autoformatting')  # noqa: B314
        print(output)  # noqa: B314
        if prompt_on_changes:
            with open('/dev/tty') as fp:
                print('\033[1m' + 'Stage this patch and continue? [Y/n] ' + '\033[0m')  # noqa: B314
                if fp.readline().strip() not in ('Y', 'y', ''):
                    print(  # noqa: B314
                        '[sentry.lint] Unstaged changes have not been staged.', file=sys.stderr)
                    if not os.environ.get('SENTRY_SKIP_FORCE_PATCH'):
                        print('[sentry.lint] Aborted!', file=sys.stderr)  # noqa: B314
                        sys.exit(1)
                else:
                    status = execute_subprocess(['git', 'update-index', '--add'], file_list)
        has_errors = status != 0
    return has_errors


def run(file_list=None, format=True, lint=True, js=True, py=True,
        less=True, yarn=True, test=False, cache=False):
    # pep8.py uses sys.argv to find setup.cfg
    old_sysargv = sys.argv

    is_ci = os.environ.get('CI')

    try:
        sys.argv = [
            os.path.join(os.path.dirname(__file__),
                         os.pardir, os.pardir, os.pardir)
        ]
        results = []

        # packages
        if yarn:
            results.append(yarn_check(file_list))

        # bail early if a deps failed
        if any(results):
            return 1

        if format:
            if py:
                results.append(py_format(file_list))
            if js:
                # run eslint with --fix and skip these linters down below
                results.append(js_lint_format(file_list))
            if less:
                results.append(less_format(file_list))

        # bail early if a formatter failed
        if any(results):
            return 1

        if lint:
            if py:
                pass  # flake8 linting was moved to pre-commit
            if js:
                # stylelint `--fix` doesn't work well
                results.append(js_stylelint(file_list, parseable=is_ci, format=format, cache=cache))

                if not format:
                    # these tasks are called when we need to format, so skip it here
                    results.append(js_lint(file_list, parseable=is_ci, format=format, cache=cache))

        if test:
            if js:
                results.append(js_test(file_list))

        if any(results):
            return 1
        return 0
    finally:
        sys.argv = old_sysargv


def check_dependencies():
    # Checks if all dependencies are correctly setup for linting locally
    try:
        get_node_modules_bin('eslint')
        get_sentry_bin('eslint-travis-wrapper')
        get_node_modules_bin('stylelint')
        get_prettier_path()
        require_tool_module('autopep8')
        require_git_hooks()
    except ToolNotFoundException as ex:
        print(ex)
        sys.exit(1)
