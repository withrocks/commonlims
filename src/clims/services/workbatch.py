from __future__ import absolute_import


class WorkbatchService:
    def __init__(self, app):
        self._app = app
        self.step_templates = list()

    def register_step_template(self, step_template_cls):
        self.step_templates.append(step_template_cls)

    def get_step_template(self, name):
        from clims.utils import single
        return single([step for step in self.step_templates if step.name == name])


class WorkbatchBase:
    pass
