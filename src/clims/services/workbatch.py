from __future__ import absolute_import
from sentry.models.file import File
from clims.services.file_handling.file_service import FILENAME_RE, FileNameValidationError
from clims.services.extensible import ExtensibleBase
from clims.services.base_extensible_service import BaseExtensibleService
from clims.models.workbatchfile import WorkBatchFile as WorkBatchFileModel
from clims.models.work_batch import WorkBatch, WorkBatchVersion


class WorkbatchService(BaseExtensibleService):
    def __init__(self, app):
        self._app = app


class WorkBatchBase(ExtensibleBase):
    WrappedArchetype = WorkBatch
    WrappedVersion = WorkBatchVersion

    def add_file(self, file_stream, name, file_handle):
        if FILENAME_RE.search(name):
            raise FileNameValidationError('File name must not contain special whitespace characters')
        file_model = File()
        file_model.save()
        file_stream.seek(0)
        file_model.putfile(file_stream)
        work_batch_file = WorkBatchFileModel(
            organization=self.organization, work_batch=self._archetype,
            name=name, file=file_model, file_handle=file_handle
        )
        work_batch_file.save()
        self._archetype.files.add(work_batch_file)
        self.save()

    def get_single_file(self, file_handle=None):
        from clims.utils import single_or_default, UnexpectedLengthError
        try:
            file_model = single_or_default(
                [f for f in self._archetype.files.all() if f.file_handle == file_handle]
            )
        except UnexpectedLengthError:
            raise ValueError(
                "There were more than one file in this workbatch, "
                "when it's expected to be only one! "
                "file-handle : {}".format(file_handle))
        if not file_model:
            raise ValueError(
                "There were no file in this workbatch, "
                "file-handle: {}".format(file_handle))
        return WorkBatchFile(file_model)

    @property
    def status(self):
        return self._archetype.status

    @status.setter
    def status(self, value):
        self._archetype.status = value


class WorkBatchFile(object):
    def __init__(self, work_batch_file_model):
        self.archetype = work_batch_file_model

    @property
    def contents(self):
        with self.archetype.file.getfile() as fp:
            c = fp.read()
        return c

    @property
    def file_stream(self):
        return self.archetype.file.getfile()

    @property
    def name(self):
        return self.archetype.name
