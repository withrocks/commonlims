from __future__ import absolute_import

from django.utils import timezone

from sentry.models import (
    OnboardingTask, OnboardingTaskStatus, OrganizationOnboardingTask
)
from sentry.signals import (
    project_created,
    first_event_pending,
    first_event_received,
    member_invited,
    member_joined,
    plugin_enabled,
    issue_tracker_used,
)
from sentry.plugins import IssueTrackingPlugin, NotificationPlugin
from sentry.testutils import TestCase


class OrganizationOnboardingTaskTest(TestCase):
    def test_no_existing_task(self):
        # Drop microsecond value for MySQL
        now = timezone.now().replace(microsecond=0)
        project = self.create_project(first_event=now)
        first_event_received.send(project=project, group=self.group, sender=type(project))

        task = OrganizationOnboardingTask.objects.get(
            organization=project.organization, task=OnboardingTask.FIRST_EVENT
        )
        assert task.status == OnboardingTaskStatus.COMPLETE
        assert task.project_id == project.id
        assert task.date_completed == project.first_event

    def test_existing_pending_task(self):
        # Drop microsecond value for MySQL
        now = timezone.now().replace(microsecond=0)
        project = self.create_project(first_event=now)

        first_event_pending.send(project=project, user=self.user, sender=type(project))

        task = OrganizationOnboardingTask.objects.get(
            organization=project.organization,
            task=OnboardingTask.FIRST_EVENT,
        )

        assert task.status == OnboardingTaskStatus.PENDING
        assert task.project_id == project.id

        first_event_received.send(project=project, group=self.group, sender=type(project))

        task = OrganizationOnboardingTask.objects.get(
            organization=project.organization,
            task=OnboardingTask.FIRST_EVENT,
        )

        assert task.status == OnboardingTaskStatus.COMPLETE
        assert task.project_id == project.id
        assert task.date_completed == project.first_event

    def test_existing_complete_task(self):
        # Drop microsecond value for MySQL
        now = timezone.now().replace(microsecond=0)
        project = self.create_project(first_event=now)
        task = OrganizationOnboardingTask.objects.create(
            organization=project.organization,
            task=OnboardingTask.FIRST_PROJECT,
            status=OnboardingTaskStatus.COMPLETE,
        )

        first_event_received.send(project=project, group=self.group, sender=type(project))

        task = OrganizationOnboardingTask.objects.get(id=task.id)
        assert task.status == OnboardingTaskStatus.COMPLETE
        assert not task.project_id

    def test_project_created(self):
        # Drop microsecond value for MySQL
        now = timezone.now().replace(microsecond=0)
        project = self.create_project(first_event=now)
        project_created.send(project=project, user=self.user, sender=type(project))

        task = OrganizationOnboardingTask.objects.get(
            organization=project.organization,
            task=OnboardingTask.FIRST_PROJECT,
            status=OnboardingTaskStatus.COMPLETE,
        )
        assert task is not None

    def test_first_event_pending(self):
        # Drop microsecond value for MySQL
        now = timezone.now().replace(microsecond=0)
        project = self.create_project(first_event=now)
        first_event_pending.send(project=project, user=self.user, sender=type(project))

        task = OrganizationOnboardingTask.objects.get(
            organization=project.organization,
            task=OnboardingTask.FIRST_EVENT,
            status=OnboardingTaskStatus.PENDING,
        )
        assert task is not None

    def test_first_event_received(self):
        # Drop microsecond value for MySQL
        now = timezone.now().replace(microsecond=0)
        project = self.create_project(first_event=now)
        project_created.send(project=project, user=self.user, sender=type(project))
        group = self.create_group(
            project=project, platform='javascript', message='javascript error message'
        )
        first_event_received.send(project=project, group=group, sender=type(project))

        task = OrganizationOnboardingTask.objects.get(
            organization=project.organization,
            task=OnboardingTask.FIRST_EVENT,
            status=OnboardingTaskStatus.COMPLETE,
        )
        assert task is not None
        assert 'platform' in task.data
        assert task.data['platform'] == 'javascript'

        second_project = self.create_project(first_event=now)
        project_created.send(project=second_project, user=self.user, sender=type(second_project))
        second_task = OrganizationOnboardingTask.objects.get(
            organization=second_project.organization,
            task=OnboardingTask.SECOND_PLATFORM,
            status=OnboardingTaskStatus.PENDING,
        )
        assert second_task is not None

        second_group = self.create_group(
            project=second_project, platform='python', message='python error message'
        )
        first_event_received.send(
            project=second_project, group=second_group, sender=type(second_project)
        )
        second_task = OrganizationOnboardingTask.objects.get(
            organization=second_project.organization,
            task=OnboardingTask.SECOND_PLATFORM,
            status=OnboardingTaskStatus.COMPLETE,
        )
        assert second_task is not None
        assert 'platform' in second_task.data
        assert second_task.data['platform'] == 'python'
        assert task.data['platform'] != second_task.data['platform']

    def test_member_invited(self):
        user = self.create_user(email='test@example.org')
        member = self.create_member(organization=self.organization, teams=[self.team], user=user)
        member_invited.send(member=member, user=user, sender=type(member))

        task = OrganizationOnboardingTask.objects.get(
            organization=self.organization,
            task=OnboardingTask.INVITE_MEMBER,
            status=OnboardingTaskStatus.PENDING,
        )
        assert task is not None

    def test_member_joined(self):
        user = self.create_user(email='test@example.org')
        member = self.create_member(organization=self.organization, teams=[self.team], user=user)
        member_joined.send(member=member, organization=self.organization, sender=type(member))

        task = OrganizationOnboardingTask.objects.get(
            organization=self.organization,
            task=OnboardingTask.INVITE_MEMBER,
            status=OnboardingTaskStatus.COMPLETE,
        )
        assert task is not None

        user2 = self.create_user(email='test@example.com')
        member2 = self.create_member(organization=self.organization, teams=[self.team], user=user2)
        member_joined.send(member=member2, organization=self.organization, sender=type(member2))

        task = OrganizationOnboardingTask.objects.get(
            organization=self.organization,
            task=OnboardingTask.INVITE_MEMBER,
            status=OnboardingTaskStatus.COMPLETE,
        )
        assert task.data['invited_member_id'] == member.id

    def test_issue_tracker_onboarding(self):
        plugin_enabled.send(
            plugin=IssueTrackingPlugin(),
            project=self.project,
            user=self.user,
            sender=type(IssueTrackingPlugin)
        )
        task = OrganizationOnboardingTask.objects.get(
            organization=self.organization,
            task=OnboardingTask.ISSUE_TRACKER,
            status=OnboardingTaskStatus.PENDING,
        )
        assert task is not None

        issue_tracker_used.send(
            plugin=IssueTrackingPlugin(),
            project=self.project,
            user=self.user,
            sender=type(IssueTrackingPlugin)
        )
        task = OrganizationOnboardingTask.objects.get(
            organization=self.organization,
            task=OnboardingTask.ISSUE_TRACKER,
            status=OnboardingTaskStatus.COMPLETE,
        )
        assert task is not None

    def test_notification_added(self):
        plugin_enabled.send(
            plugin=NotificationPlugin(),
            project=self.project,
            user=self.user,
            sender=type(NotificationPlugin)
        )
        task = OrganizationOnboardingTask.objects.get(
            organization=self.organization,
            task=OnboardingTask.NOTIFICATION_SERVICE,
            status=OnboardingTaskStatus.COMPLETE,
        )
        assert task is not None
