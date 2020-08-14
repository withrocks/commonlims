from __future__ import absolute_import, print_function

from django.conf.urls import patterns
from django.conf import urls

from .endpoints.work_batch import WorkBatchEndpoint

from .endpoints.step import StepEndpoint
from .endpoints.trigger_script import TriggerScriptEndpoint

from .endpoints.substance import SubstanceEndpoint
from .endpoints.substance_details import SubstanceDetailsEndpoint
from .endpoints.substance_property import SubstancePropertyEndpoint

from .endpoints.project import ProjectEndpoint
from .endpoints.project_property import ProjectPropertyEndpoint

from .endpoints.container import ContainerEndpoint
from .endpoints.container_property import ContainerPropertyEndpoint
from .endpoints.process_definitions import ProcessDefinitionsEndpoint

from .endpoints.user_files import UserFilesEndpoint

from .endpoints.work_batch_files import WorkBatchFilesEndpoint
from .endpoints.work_batch_file_details import WorkBatchFileDetailsEndpoint

from .endpoints.work_batch_settings import (WorkBatchSettingsEndpoint,
                                            WorkBatchSettingsDetailsEndpoint)

from .endpoints.work_batch_notes import WorkBatchNotesEndpoint
from .endpoints.work_batch_notes_details import WorkBatchNotesDetailsEndpoint

from .endpoints.plugin_actions import PluginActionsEndpoint

from .endpoints.workflow import WorkflowEndpoint
from .endpoints.task_definition import TaskDefinitionEndpoint
from .endpoints.task_definition_details import TaskDefinitionDetailsEndpoint

from .endpoints.substance_file import SubstanceFileEndpoint
from .endpoints.substance_file_details import (SubstanceFileDetailsEndpoint,
                                               SubstanceFileDemoDetailsEndpoint
                                               )

from .endpoints.organization_searches import OrganizationSearchesEndpoint

from .endpoints.process_assignments import ProcessAssignmentsEndpoint
from .endpoints.tasks import TasksEndpoint


def fmt(s):
    """Formats rules with common patterns"""
    s = s.replace('{org}', r'(?P<organization_slug>[^\/]+)')
    return s


def url(endpoint, *args, **kwargs):
    return urls.url(fmt(endpoint), *args, **kwargs)


urlpatterns = patterns(
    '',
    # Workflow
    url(r'^organizations/{org}/task-definitions/', TaskDefinitionEndpoint.as_view(),
        name='clims-api-0-task-definitions'),
    url(r'^task-definitions/(?P<process_definition_key>[^\/]+)/(?P<task_definition_key>[^\/]+)/$',
        TaskDefinitionDetailsEndpoint.as_view(),
        name='clims-api-0-task-definition-details'),
    url(r'^organizations/{org}/workflow/(?P<workflow_endpoint>[^\/]+)/$',
        WorkflowEndpoint.as_view(),
        name='clims-api-0-workflow-root'),
    url(r'^organizations/{org}/process-assignments/$',
        ProcessAssignmentsEndpoint.as_view(),
        name='clims-api-0-process-assignments'),
    url(r'^organizations/{org}/tasks/$',
        TasksEndpoint.as_view(),
        name='clims-api-0-tasks'),
    # Steps
    url(r'^organizations/{org}/steps/$',
        StepEndpoint.as_view(),
        name='clims-api-0-steps'),
    url(r'^organizations/{org}/scripts/$',
        TriggerScriptEndpoint.as_view(),
        name='clims-api-0-script-trigger'),

    # Substances
    url(r'^substances/(?P<substance_id>[^\/]+)/$',
        SubstanceDetailsEndpoint.as_view(),
        name='clims-api-0-substance-details'),
    url(r'^organizations/{org}/substances/$',
        SubstanceEndpoint.as_view(),
        name='clims-api-0-substances'),
    url(r'^organizations/{org}/substances/property/(?P<prop>[^\/]+)/$',
        SubstancePropertyEndpoint.as_view(),
        name='clims-api-0-substance-property'),
    url(r'^organizations/{org}/containers/$',
        ContainerEndpoint.as_view(),
        name='clims-api-0-containers'),
    url(r'^organizations/{org}/containers/property/(?P<prop>[^\/]+)/$',
        ContainerPropertyEndpoint.as_view(),
        name='clims-api-0-container-property'),
    url(r'^organizations/{org}/projects/$',
        ProjectEndpoint.as_view(),
        name='clims-api-0-projects'),
    url(r'^organizations/{org}/projects/property/(?P<prop>[^\/]+)/$',
        ProjectPropertyEndpoint.as_view(),
        name='clims-api-0-project-property'),
    url(r'^organizations/{org}/substances/files/$',
        SubstanceFileEndpoint.as_view(),
        name='clims-api-0-organization-substances-files'),
    url(r'^organizations/{org}/substances/files/demo/$',
        SubstanceFileDemoDetailsEndpoint.as_view(),
        name='clims-api-0-organization-substances-files'),
    url(r'^organizations/{org}/substances/files/(?P<file_id>[^\/]+)/$',
        SubstanceFileDetailsEndpoint.as_view(),
        name='clims-api-0-organization-substances-file-details'),

    # work-batches: user task activities that have been grouped together in 1..n sized batches
    url(r'^organizations/{org}/work-batches/$',
        WorkBatchEndpoint.as_view(),
        name='clims-api-0-work-batches'),
    url(r'^work-batches/(?P<work_batch_id>[^\/]+)/files/$',
        WorkBatchFilesEndpoint.as_view(),
        name='clims-api-0-user-task-files'),
    url(r'^work-batches/(?P<work_batch_id>[^\/]+)/files/(?P<file_id>[^\/]+)/$',
        WorkBatchFileDetailsEndpoint.as_view(),
        name='clims-api-0-user-task-file-details'),
    url(r'^work-batches/(?P<work_batch_id>[^\/]+)/comments/$',
        WorkBatchNotesEndpoint.as_view(),
        name='clims-api-0-group-notes'),
    url(r'^work-batches/(?P<work_batch_id>[^\/]+)/comments/$(?P<note_id>[^\/]+)/',
        WorkBatchNotesDetailsEndpoint.as_view(),
        name='clims-api-0-group-notes-details'),
    url(r'^work-batch-settings/(?P<organization_slug>[^\/]+)/$',
        WorkBatchSettingsEndpoint.as_view(),
        name='clims-api-0-work-batch-settings'),
    url(r'^work-batch-settings/(?P<work_batch_type>[^\/]+)/$',
        WorkBatchSettingsDetailsEndpoint.as_view(),
        name='clims-api-0-work-batch-settings-details'),

    # Processes and Tasks
    url(r'^process-definitions/$',
        ProcessDefinitionsEndpoint.as_view(),
        name='clims-api-0-process-definitions'),
    url(r'^user-files/$',
        UserFilesEndpoint.as_view(),
        name='clims-api-0-user-files'),

    # Work batches:
    url(r'^organizations/{org}/work-batches/$',
        WorkBatchEndpoint.as_view(),
        name='clims-api-0-work-batches'),
    url(r'^user-tasks/(?P<user_task_id>[^\/]+)/files/$',
        WorkBatchFilesEndpoint.as_view(),
        name='clims-api-0-work-batch-files'),
    url(r'^work-batches/(?P<work_batch_id>[^\/]+)/files/(?P<file_id>[^\/]+)/$',
        WorkBatchFileDetailsEndpoint.as_view(),
        name='clims-api-0-work-batches-file-details'),

    # Plugins
    url(r'^plugins/{org}/(?P<plugin_id>[^\/]+)/actions/$',
        PluginActionsEndpoint.as_view(),
        name='clims-api-0-plugin-actions'),

    # Saved searches
    url(r'^organizations/{org}/saved-searches/$',
        OrganizationSearchesEndpoint.as_view(),
        name='clims-api-0-organization-saved-searches'),
)
