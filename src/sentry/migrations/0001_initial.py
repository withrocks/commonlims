# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import bitfield.models
import sentry.models.rawevent
import sentry.models.scheduledeletion
import sentry.models.groupshare
import sentry.utils.canonical
import sentry.db.models.fields.uuid
import django.utils.timezone
import sentry.db.models.fields.citext
from django.conf import settings
import sentry.models.sentryappinstallation
import sentry.models.apigrant
import sentry.db.models.fields.gzippeddict
import sentry.models.apitoken
import sentry.models.apiapplication
import sentry.models.sentryapp
import sentry.db.models.fields.node
import sentry.models.useremail
import sentry.db.models.fields.bounded
import sentry.models.broadcast
import sentry.db.models.fields.array
import jsonfield.fields
import sentry.models.servicehook
import sentry.db.models.fields.foreignkey
import django.db.models.deletion
import sentry.models.event
import sentry.db.models.fields.encrypted


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='last login')),
                ('id', sentry.db.models.fields.bounded.BoundedAutoField(serialize=False, primary_key=True)),
                ('username', models.CharField(unique=True, max_length=128, verbose_name='username')),
                ('name', models.CharField(max_length=200, verbose_name='name', db_column=b'first_name', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_managed', models.BooleanField(default=False, help_text='Designates whether this user should be treated as managed. Select this to disallow the user from modifying their account (username, password, etc).', verbose_name='managed')),
                ('is_sentry_app', models.NullBooleanField(default=None, help_text='Designates whether this user is the entity used for Permissionson behalf of a Sentry App. Cannot login or use Sentry like anormal User would.', verbose_name='is sentry app')),
                ('is_password_expired', models.BooleanField(default=False, help_text='If set to true then the user needs to change the password on next sign in.', verbose_name='password expired')),
                ('last_password_change', models.DateTimeField(help_text='The date the password was changed last.', null=True, verbose_name='date of last password change')),
                ('flags', bitfield.models.BitField(default=0, null=True, flags=((b'newsletter_consent_prompt', b'Do we need to ask this user for newsletter consent?'),))),
                ('session_nonce', models.CharField(max_length=12, null=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('last_active', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='last active')),
            ],
            options={
                'db_table': 'auth_user',
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('type', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(choices=[(1, b'set_resolved'), (15, b'set_resolved_by_age'), (13, b'set_resolved_in_release'), (16, b'set_resolved_in_commit'), (21, b'set_resolved_in_pull_request'), (2, b'set_unresolved'), (3, b'set_ignored'), (4, b'set_public'), (5, b'set_private'), (6, b'set_regression'), (7, b'create_issue'), (8, b'note'), (9, b'first_seen'), (10, b'release'), (11, b'assigned'), (12, b'unassigned'), (14, b'merge'), (17, b'deploy'), (18, b'new_processing_issues'), (19, b'unmerge_source'), (20, b'unmerge_destination')])),
                ('ident', models.CharField(max_length=64, null=True)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('data', sentry.db.models.fields.gzippeddict.GzippedDictField(null=True)),
            ],
            options={
                'db_table': 'sentry_activity',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApiApplication',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('client_id', models.CharField(default=sentry.models.apiapplication.generate_token, unique=True, max_length=64)),
                ('client_secret', sentry.db.models.fields.encrypted.EncryptedTextField(default=sentry.models.apiapplication.generate_token)),
                ('name', models.CharField(default=sentry.models.apiapplication.generate_name, max_length=64, blank=True)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, db_index=True, choices=[(0, 'Active'), (1, 'Inactive')])),
                ('allowed_origins', models.TextField(null=True, blank=True)),
                ('redirect_uris', models.TextField()),
                ('homepage_url', models.URLField(null=True)),
                ('privacy_url', models.URLField(null=True)),
                ('terms_url', models.URLField(null=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('owner', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sentry_apiapplication',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApiAuthorization',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('scopes', bitfield.models.BitField(default=None, flags=((b'project:read', b'project:read'), (b'project:write', b'project:write'), (b'project:admin', b'project:admin'), (b'project:releases', b'project:releases'), (b'team:read', b'team:read'), (b'team:write', b'team:write'), (b'team:admin', b'team:admin'), (b'event:read', b'event:read'), (b'event:write', b'event:write'), (b'event:admin', b'event:admin'), (b'org:read', b'org:read'), (b'org:write', b'org:write'), (b'org:admin', b'org:admin'), (b'member:read', b'member:read'), (b'member:write', b'member:write'), (b'member:admin', b'member:admin')))),
                ('scope_list', sentry.db.models.fields.array.ArrayField(null=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('application', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.ApiApplication', null=True)),
                ('user', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sentry_apiauthorization',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApiGrant',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('code', models.CharField(default=sentry.models.apigrant.generate_code, max_length=64, db_index=True)),
                ('expires_at', models.DateTimeField(default=sentry.models.apigrant.default_expiration, db_index=True)),
                ('redirect_uri', models.CharField(max_length=255)),
                ('scopes', bitfield.models.BitField(default=None, flags=((b'project:read', b'project:read'), (b'project:write', b'project:write'), (b'project:admin', b'project:admin'), (b'project:releases', b'project:releases'), (b'team:read', b'team:read'), (b'team:write', b'team:write'), (b'team:admin', b'team:admin'), (b'event:read', b'event:read'), (b'event:write', b'event:write'), (b'event:admin', b'event:admin'), (b'org:read', b'org:read'), (b'org:write', b'org:write'), (b'org:admin', b'org:admin'), (b'member:read', b'member:read'), (b'member:write', b'member:write'), (b'member:admin', b'member:admin')))),
                ('scope_list', sentry.db.models.fields.array.ArrayField(null=True)),
                ('application', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.ApiApplication')),
                ('user', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sentry_apigrant',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApiKey',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('label', models.CharField(default=b'Default', max_length=64, blank=True)),
                ('key', models.CharField(unique=True, max_length=32)),
                ('scopes', bitfield.models.BitField(default=None, flags=((b'project:read', b'project:read'), (b'project:write', b'project:write'), (b'project:admin', b'project:admin'), (b'project:releases', b'project:releases'), (b'team:read', b'team:read'), (b'team:write', b'team:write'), (b'team:admin', b'team:admin'), (b'event:read', b'event:read'), (b'event:write', b'event:write'), (b'event:admin', b'event:admin'), (b'org:read', b'org:read'), (b'org:write', b'org:write'), (b'org:admin', b'org:admin'), (b'member:read', b'member:read'), (b'member:write', b'member:write'), (b'member:admin', b'member:admin')))),
                ('scope_list', sentry.db.models.fields.array.ArrayField(null=True)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, db_index=True, choices=[(0, 'Active'), (1, 'Inactive')])),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('allowed_origins', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'sentry_apikey',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApiToken',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('scopes', bitfield.models.BitField(default=None, flags=((b'project:read', b'project:read'), (b'project:write', b'project:write'), (b'project:admin', b'project:admin'), (b'project:releases', b'project:releases'), (b'team:read', b'team:read'), (b'team:write', b'team:write'), (b'team:admin', b'team:admin'), (b'event:read', b'event:read'), (b'event:write', b'event:write'), (b'event:admin', b'event:admin'), (b'org:read', b'org:read'), (b'org:write', b'org:write'), (b'org:admin', b'org:admin'), (b'member:read', b'member:read'), (b'member:write', b'member:write'), (b'member:admin', b'member:admin')))),
                ('scope_list', sentry.db.models.fields.array.ArrayField(null=True)),
                ('token', models.CharField(default=sentry.models.apitoken.generate_token, unique=True, max_length=64)),
                ('refresh_token', models.CharField(default=sentry.models.apitoken.generate_token, max_length=64, unique=True, null=True)),
                ('expires_at', models.DateTimeField(default=sentry.models.apitoken.default_expiration, null=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('application', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.ApiApplication', null=True)),
                ('user', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sentry_apitoken',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AssistantActivity',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('guide_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('viewed_ts', models.DateTimeField(null=True)),
                ('dismissed_ts', models.DateTimeField(null=True)),
                ('useful', models.NullBooleanField()),
                ('user', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sentry_assistant_activity',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AuditLogEntry',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('actor_label', models.CharField(max_length=64, null=True, blank=True)),
                ('target_object', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('event', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(choices=[(1, b'member.invite'), (2, b'member.add'), (3, b'member.accept-invite'), (5, b'member.remove'), (4, b'member.edit'), (6, b'member.join-team'), (7, b'member.leave-team'), (8, b'member.pending'), (20, b'team.create'), (21, b'team.edit'), (22, b'team.remove'), (30, b'project.create'), (31, b'project.edit'), (32, b'project.remove'), (33, b'project.set-public'), (34, b'project.set-private'), (35, b'project.request-transfer'), (36, b'project.accept-transfer'), (10, b'org.create'), (11, b'org.edit'), (12, b'org.remove'), (13, b'org.restore'), (40, b'tagkey.remove'), (50, b'projectkey.create'), (51, b'projectkey.edit'), (52, b'projectkey.remove'), (53, b'projectkey.enable'), (53, b'projectkey.disable'), (60, b'sso.enable'), (61, b'sso.disable'), (62, b'sso.edit'), (63, b'sso-identity.link'), (70, b'api-key.create'), (71, b'api-key.edit'), (72, b'api-key.remove'), (80, b'rule.create'), (81, b'rule.edit'), (82, b'rule.remove'), (100, b'serivcehook.create'), (101, b'serivcehook.edit'), (102, b'serivcehook.remove'), (103, b'serivcehook.enable'), (104, b'serivcehook.disable'), (110, b'integration.add'), (111, b'integration.edit'), (112, b'integration.remove'), (90, b'ondemand.edit'), (91, b'trial.started'), (92, b'plan.changed')])),
                ('ip_address', models.GenericIPAddressField(null=True, unpack_ipv4=True)),
                ('data', sentry.db.models.fields.gzippeddict.GzippedDictField()),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('actor', sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='audit_actors', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('actor_key', sentry.db.models.fields.foreignkey.FlexibleForeignKey(blank=True, to='sentry.ApiKey', null=True)),
            ],
            options={
                'db_table': 'sentry_auditlogentry',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Authenticator',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedAutoField(serialize=False, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('last_used_at', models.DateTimeField(null=True, verbose_name='last used at')),
                ('type', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(choices=[(0, 'Recovery Codes'), (1, 'Authenticator App'), (2, 'Text Message'), (3, 'U2F (Universal 2nd Factor)')])),
                ('config', sentry.db.models.fields.encrypted.EncryptedPickledObjectField(editable=False)),
                ('user', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'auth_authenticator',
                'verbose_name': 'authenticator',
                'verbose_name_plural': 'authenticators',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AuthIdentity',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('ident', models.CharField(max_length=128)),
                ('data', sentry.db.models.fields.encrypted.EncryptedJsonField(default=dict)),
                ('last_verified', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_synced', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'sentry_authidentity',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AuthProvider',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('provider', models.CharField(max_length=128)),
                ('config', sentry.db.models.fields.encrypted.EncryptedJsonField(default=dict)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('sync_time', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('last_sync', models.DateTimeField(null=True)),
                ('default_role', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=50)),
                ('default_global_access', models.BooleanField(default=True)),
                ('flags', bitfield.models.BitField(default=0, flags=((b'allow_unlinked', b'Grant access to members who have not linked SSO accounts.'),))),
            ],
            options={
                'db_table': 'sentry_authprovider',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Broadcast',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('upstream_id', models.CharField(max_length=32, null=True, blank=True)),
                ('title', models.CharField(max_length=32)),
                ('message', models.CharField(max_length=256)),
                ('link', models.URLField(null=True, blank=True)),
                ('is_active', models.BooleanField(default=True, db_index=True)),
                ('date_expires', models.DateTimeField(default=sentry.models.broadcast.default_expiration, null=True, blank=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'sentry_broadcast',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BroadcastSeen',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('date_seen', models.DateTimeField(default=django.utils.timezone.now)),
                ('broadcast', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Broadcast')),
                ('user', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sentry_broadcastseen',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Commit',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('organization_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('repository_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('key', models.CharField(max_length=64)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('message', models.TextField(null=True)),
            ],
            options={
                'db_table': 'sentry_commit',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CommitAuthor',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('organization_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('name', models.CharField(max_length=128, null=True)),
                ('email', models.EmailField(max_length=75)),
                ('external_id', models.CharField(max_length=164, null=True)),
            ],
            options={
                'db_table': 'sentry_commitauthor',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CommitFileChange',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('organization_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('filename', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=1, choices=[(b'A', b'Added'), (b'D', b'Deleted'), (b'M', b'Modified')])),
                ('commit', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Commit')),
            ],
            options={
                'db_table': 'sentry_commitfilechange',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Counter',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('value', sentry.db.models.fields.bounded.BoundedBigIntegerField()),
            ],
            options={
                'db_table': 'sentry_projectcounter',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, choices=[(0, b'active'), (1, b'disabled'), (2, b'pending_deletion'), (3, b'deletion_in_progress')])),
                ('created_by', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sentry_dashboard',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeletedOrganization',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('actor_label', models.CharField(max_length=64, null=True)),
                ('actor_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(null=True)),
                ('actor_key', models.CharField(max_length=32, null=True)),
                ('ip_address', models.GenericIPAddressField(null=True, unpack_ipv4=True)),
                ('date_deleted', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_created', models.DateTimeField(null=True)),
                ('reason', models.TextField(null=True, blank=True)),
                ('name', models.CharField(max_length=64, null=True)),
                ('slug', models.CharField(max_length=50, null=True)),
            ],
            options={
                'db_table': 'sentry_deletedorganization',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeletedProject',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('actor_label', models.CharField(max_length=64, null=True)),
                ('actor_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(null=True)),
                ('actor_key', models.CharField(max_length=32, null=True)),
                ('ip_address', models.GenericIPAddressField(null=True, unpack_ipv4=True)),
                ('date_deleted', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_created', models.DateTimeField(null=True)),
                ('reason', models.TextField(null=True, blank=True)),
                ('slug', models.CharField(max_length=50, null=True)),
                ('name', models.CharField(max_length=200, null=True)),
                ('organization_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(null=True)),
                ('organization_name', models.CharField(max_length=64, null=True)),
                ('organization_slug', models.CharField(max_length=50, null=True)),
                ('platform', models.CharField(max_length=64, null=True)),
            ],
            options={
                'db_table': 'sentry_deletedproject',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeletedTeam',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('actor_label', models.CharField(max_length=64, null=True)),
                ('actor_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(null=True)),
                ('actor_key', models.CharField(max_length=32, null=True)),
                ('ip_address', models.GenericIPAddressField(null=True, unpack_ipv4=True)),
                ('date_deleted', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_created', models.DateTimeField(null=True)),
                ('reason', models.TextField(null=True, blank=True)),
                ('name', models.CharField(max_length=64, null=True)),
                ('slug', models.CharField(max_length=50, null=True)),
                ('organization_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(null=True)),
                ('organization_name', models.CharField(max_length=64, null=True)),
                ('organization_slug', models.CharField(max_length=50, null=True)),
            ],
            options={
                'db_table': 'sentry_deletedteam',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Deploy',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('organization_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('environment_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('date_finished', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_started', models.DateTimeField(null=True, blank=True)),
                ('name', models.CharField(max_length=64, null=True, blank=True)),
                ('url', models.URLField(null=True, blank=True)),
                ('notified', models.NullBooleanField(default=False, db_index=True)),
            ],
            options={
                'db_table': 'sentry_deploy',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DiscoverSavedQuery',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('query', jsonfield.fields.JSONField(default=dict)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('created_by', sentry.db.models.fields.foreignkey.FlexibleForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'db_table': 'sentry_discoversavedquery',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DiscoverSavedQueryProject',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('discover_saved_query', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.DiscoverSavedQuery')),
            ],
            options={
                'db_table': 'sentry_discoversavedqueryproject',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('organization_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('name', models.CharField(max_length=64)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'sentry_distribution',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('email', sentry.db.models.fields.citext.CIEmailField(unique=True, max_length=75, verbose_name='email address')),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'sentry_email',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('organization_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('project_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('name', models.CharField(max_length=64)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'sentry_environment',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnvironmentProject',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('is_hidden', models.NullBooleanField()),
                ('environment', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Environment')),
            ],
            options={
                'db_table': 'sentry_environmentproject',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('group_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(null=True, blank=True)),
                ('event_id', models.CharField(max_length=32, null=True, db_column=b'message_id')),
                ('project_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(null=True, blank=True)),
                ('message', models.TextField()),
                ('platform', models.CharField(max_length=64, null=True)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('time_spent', sentry.db.models.fields.bounded.BoundedIntegerField(null=True)),
                ('data', sentry.db.models.fields.node.NodeField(ref_func=sentry.models.event.ref_func, null=True, ref_version=2, wrapper=sentry.utils.canonical.CanonicalKeyDict, blank=True)),
            ],
            options={
                'db_table': 'sentry_message',
                'verbose_name': 'message',
                'verbose_name_plural': 'messages',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventAttachment',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('project_id', sentry.db.models.fields.bounded.BoundedBigIntegerField()),
                ('group_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(null=True)),
                ('event_id', models.CharField(max_length=32)),
                ('name', models.TextField()),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
            ],
            options={
                'db_table': 'sentry_eventattachment',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventMapping',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('project_id', sentry.db.models.fields.bounded.BoundedBigIntegerField()),
                ('group_id', sentry.db.models.fields.bounded.BoundedBigIntegerField()),
                ('event_id', models.CharField(max_length=32)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'sentry_eventmapping',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventProcessingIssue',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'sentry_eventprocessingissue',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventTag',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('project_id', sentry.db.models.fields.bounded.BoundedBigIntegerField()),
                ('group_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(null=True)),
                ('event_id', sentry.db.models.fields.bounded.BoundedBigIntegerField()),
                ('key_id', sentry.db.models.fields.bounded.BoundedBigIntegerField()),
                ('value_id', sentry.db.models.fields.bounded.BoundedBigIntegerField()),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
            ],
            options={
                'db_table': 'sentry_eventtag',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventUser',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('project_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('hash', models.CharField(max_length=32)),
                ('ident', models.CharField(max_length=128, null=True)),
                ('email', models.EmailField(max_length=75, null=True)),
                ('username', models.CharField(max_length=128, null=True)),
                ('name', models.CharField(max_length=128, null=True)),
                ('ip_address', models.GenericIPAddressField(null=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
            ],
            options={
                'db_table': 'sentry_eventuser',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExternalIssue',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('organization_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('integration_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('key', models.CharField(max_length=128)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('title', models.TextField(null=True)),
                ('description', models.TextField(null=True)),
                ('metadata', jsonfield.fields.JSONField(null=True)),
            ],
            options={
                'db_table': 'sentry_externalissue',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeatureAdoption',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('feature_id', models.PositiveIntegerField(choices=[(0, b'Python'), (1, b'JavaScript'), (2, b'Node.js'), (3, b'Ruby'), (4, b'Java'), (5, b'Cocoa'), (6, b'Objective-C'), (7, b'PHP'), (8, b'Go'), (9, b'C#'), (10, b'Perl'), (11, b'Elixir'), (12, b'CFML'), (13, b'Groovy'), (14, b'CSP Reports'), (20, b'Flask'), (21, b'Django'), (22, b'Celery'), (23, b'Bottle'), (24, b'Pylons'), (25, b'Tornado'), (26, b'web.py'), (27, b'Zope'), (40, b'First Event'), (41, b'Release Tracking'), (42, b'Environment Tracking'), (43, b'User Tracking'), (44, b'Custom Tags'), (45, b'Source Maps'), (46, b'User Feedback'), (48, b'Breadcrumbs'), (49, b'Resolve with Commit'), (60, b'First Project'), (61, b'Invite Team'), (62, b'Assign Issue'), (63, b'Resolve in Next Release'), (64, b'Advanced Search'), (65, b'Saved Search'), (66, b'Inbound Filters'), (67, b'Alert Rules'), (68, b'Issue Tracker Integration'), (69, b'Notification Integration'), (70, b'Delete and Discard Future Events'), (71, b'Link a Repository'), (72, b'Ownership Rules'), (73, b'Ignore Issue'), (80, b'SSO'), (81, b'Data Scrubbers'), (90, b'Create Release Using API'), (91, b'Create Deploy Using API')])),
                ('date_completed', models.DateTimeField(default=django.utils.timezone.now)),
                ('complete', models.BooleanField(default=False)),
                ('applicable', models.BooleanField(default=True)),
                ('data', jsonfield.fields.JSONField(default=dict)),
            ],
            options={
                'db_table': 'sentry_featureadoption',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('name', models.TextField()),
                ('type', models.CharField(max_length=64)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('headers', jsonfield.fields.JSONField(default=dict)),
                ('size', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('checksum', models.CharField(max_length=40, null=True, db_index=True)),
                ('path', models.TextField(null=True)),
            ],
            options={
                'db_table': 'sentry_file',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FileBlob',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('path', models.TextField(null=True)),
                ('size', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('checksum', models.CharField(unique=True, max_length=40)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
            ],
            options={
                'db_table': 'sentry_fileblob',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FileBlobIndex',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('offset', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('blob', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.FileBlob')),
                ('file', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.File')),
            ],
            options={
                'db_table': 'sentry_fileblobindex',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FileBlobOwner',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('blob', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.FileBlob')),
            ],
            options={
                'db_table': 'sentry_fileblobowner',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('logger', models.CharField(default=b'', max_length=64, db_index=True, blank=True)),
                ('level', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=40, blank=True, db_index=True, choices=[(0, b'sample'), (40, b'error'), (10, b'debug'), (50, b'fatal'), (20, b'info'), (30, b'warning')])),
                ('message', models.TextField()),
                ('culprit', models.CharField(max_length=200, null=True, db_column=b'view', blank=True)),
                ('num_comments', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, null=True)),
                ('platform', models.CharField(max_length=64, null=True)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, db_index=True, choices=[(0, 'Unresolved'), (1, 'Resolved'), (2, 'Ignored')])),
                ('times_seen', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=1, db_index=True)),
                ('last_seen', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('first_seen', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('resolved_at', models.DateTimeField(null=True, db_index=True)),
                ('active_at', models.DateTimeField(null=True, db_index=True)),
                ('time_spent_total', sentry.db.models.fields.bounded.BoundedIntegerField(default=0)),
                ('time_spent_count', sentry.db.models.fields.bounded.BoundedIntegerField(default=0)),
                ('score', sentry.db.models.fields.bounded.BoundedIntegerField(default=0)),
                ('is_public', models.NullBooleanField(default=False)),
                ('data', sentry.db.models.fields.gzippeddict.GzippedDictField(null=True, blank=True)),
                ('short_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(null=True)),
            ],
            options={
                'verbose_name_plural': 'grouped messages',
                'db_table': 'sentry_groupedmessage',
                'verbose_name': 'grouped message',
                'permissions': (('can_view', 'Can view'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupAssignee',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('group', sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='assignee_set1', to='sentry.Group', unique=True)),
            ],
            options={
                'db_table': 'sentry_groupasignee',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupBookmark',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('group', sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='bookmark_set', to='sentry.Group')),
            ],
            options={
                'db_table': 'sentry_groupbookmark',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupCommitResolution',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('group_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('commit_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
            ],
            options={
                'db_table': 'sentry_groupcommitresolution',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupEmailThread',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('email', models.EmailField(max_length=75)),
                ('msgid', models.CharField(max_length=100)),
                ('date', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('group', sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='groupemail_set', to='sentry.Group')),
            ],
            options={
                'db_table': 'sentry_groupemailthread',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupEnvironment',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('group_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('environment_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('first_release_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('first_seen', models.DateTimeField(default=django.utils.timezone.now, null=True, db_index=True)),
            ],
            options={
                'db_table': 'sentry_groupenvironment',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupHash',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('hash', models.CharField(max_length=32)),
                ('group_tombstone_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True, db_index=True)),
                ('state', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True, choices=[(1, 'Locked (Migration in Progress)')])),
                ('group', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Group', null=True)),
            ],
            options={
                'db_table': 'sentry_grouphash',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupLink',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('group_id', sentry.db.models.fields.bounded.BoundedBigIntegerField()),
                ('project_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(db_index=True)),
                ('linked_type', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=1, choices=[(1, 'Commit'), (2, 'Pull Request'), (3, 'Tracker Issue')])),
                ('linked_id', sentry.db.models.fields.bounded.BoundedBigIntegerField()),
                ('relationship', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=2, choices=[(1, 'Resolves'), (2, 'Linked')])),
                ('data', jsonfield.fields.JSONField(default=dict)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
            ],
            options={
                'db_table': 'sentry_grouplink',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupMeta',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('key', models.CharField(max_length=64)),
                ('value', models.TextField()),
                ('group', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Group')),
            ],
            options={
                'db_table': 'sentry_groupmeta',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupRedirect',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('group_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(db_index=True)),
                ('previous_group_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(unique=True)),
            ],
            options={
                'db_table': 'sentry_groupredirect',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupRelease',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('project_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('group_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('release_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('environment', models.CharField(default=b'', max_length=64)),
                ('first_seen', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_seen', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
            ],
            options={
                'db_table': 'sentry_grouprelease',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupResolution',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('type', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True, choices=[(1, b'in_next_release'), (0, b'in_release')])),
                ('actor_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, choices=[(0, 'Pending'), (1, 'Resolved')])),
                ('group', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Group', unique=True)),
            ],
            options={
                'db_table': 'sentry_groupresolution',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupRuleStatus',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('status', models.PositiveSmallIntegerField(default=0)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_active', models.DateTimeField(null=True)),
                ('group', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Group')),
            ],
            options={
                'db_table': 'sentry_grouprulestatus',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupSeen',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('last_seen', models.DateTimeField(default=django.utils.timezone.now)),
                ('group', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Group')),
            ],
            options={
                'db_table': 'sentry_groupseen',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupShare',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('uuid', models.CharField(default=sentry.models.groupshare.default_uuid, unique=True, max_length=32)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('group', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Group', unique=True)),
            ],
            options={
                'db_table': 'sentry_groupshare',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupSnooze',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('until', models.DateTimeField(null=True)),
                ('count', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('window', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('user_count', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('user_window', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('state', jsonfield.fields.JSONField(null=True)),
                ('actor_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('group', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Group', unique=True)),
            ],
            options={
                'db_table': 'sentry_groupsnooze',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupSubscription',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('is_active', models.BooleanField(default=True)),
                ('reason', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('group', sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='subscription_set', to='sentry.Group')),
            ],
            options={
                'db_table': 'sentry_groupsubscription',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupTagKey',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('project_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True, db_index=True)),
                ('group_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('key', models.CharField(max_length=32)),
                ('values_seen', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0)),
            ],
            options={
                'db_table': 'sentry_grouptagkey',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupTagValue',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('project_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True, db_index=True)),
                ('group_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('times_seen', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0)),
                ('key', models.CharField(max_length=32)),
                ('value', models.CharField(max_length=200)),
                ('last_seen', models.DateTimeField(default=django.utils.timezone.now, null=True, db_index=True)),
                ('first_seen', models.DateTimeField(default=django.utils.timezone.now, null=True, db_index=True)),
            ],
            options={
                'db_table': 'sentry_messagefiltervalue',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupTombstone',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('previous_group_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(unique=True)),
                ('level', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=40, blank=True, choices=[(0, b'sample'), (40, b'error'), (10, b'debug'), (50, b'fatal'), (20, b'info'), (30, b'warning')])),
                ('message', models.TextField()),
                ('culprit', models.CharField(max_length=200, null=True, blank=True)),
                ('data', sentry.db.models.fields.gzippeddict.GzippedDictField(null=True, blank=True)),
                ('actor_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
            ],
            options={
                'db_table': 'sentry_grouptombstone',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Identity',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('external_id', models.CharField(max_length=64)),
                ('data', sentry.db.models.fields.encrypted.EncryptedJsonField(default=dict)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0)),
                ('scopes', sentry.db.models.fields.array.ArrayField(null=True)),
                ('date_verified', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'sentry_identity',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IdentityProvider',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('type', models.CharField(max_length=64)),
                ('config', sentry.db.models.fields.encrypted.EncryptedJsonField(default=dict)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('external_id', models.CharField(max_length=64, null=True)),
            ],
            options={
                'db_table': 'sentry_identityprovider',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Integration',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('provider', models.CharField(max_length=64)),
                ('external_id', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=200)),
                ('metadata', sentry.db.models.fields.encrypted.EncryptedJsonField(default=dict)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, null=True, choices=[(0, b'active'), (1, b'disabled'), (2, b'pending_deletion'), (3, b'deletion_in_progress')])),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now, null=True)),
            ],
            options={
                'db_table': 'sentry_integration',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IntegrationExternalProject',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('organization_integration_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', models.CharField(max_length=128)),
                ('external_id', models.CharField(max_length=64)),
                ('resolved_status', models.CharField(max_length=64)),
                ('unresolved_status', models.CharField(max_length=64)),
            ],
            options={
                'db_table': 'sentry_integrationexternalproject',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LatestRelease',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('repository_id', sentry.db.models.fields.bounded.BoundedBigIntegerField()),
                ('environment_id', sentry.db.models.fields.bounded.BoundedBigIntegerField()),
                ('release_id', sentry.db.models.fields.bounded.BoundedBigIntegerField()),
                ('deploy_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(null=True)),
                ('commit_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(null=True)),
            ],
            options={
                'db_table': 'sentry_latestrelease',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LostPasswordHash',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('hash', models.CharField(max_length=32)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
                'db_table': 'sentry_lostpasswordhash',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Monitor',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('guid', sentry.db.models.fields.uuid.UUIDField(auto_add=True, unique=True, max_length=32, editable=False)),
                ('organization_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('project_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('name', models.CharField(max_length=128)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, choices=[(0, b'active'), (1, b'disabled'), (2, b'pending_deletion'), (3, b'deletion_in_progress'), (4, b'ok'), (5, b'error')])),
                ('type', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, choices=[(0, b'unknown'), (1, b'health_check'), (2, b'heartbeat'), (3, b'cron_job')])),
                ('config', sentry.db.models.fields.encrypted.EncryptedJsonField(default=dict)),
                ('next_checkin', models.DateTimeField(null=True)),
                ('last_checkin', models.DateTimeField(null=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'sentry_monitor',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MonitorCheckIn',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('guid', sentry.db.models.fields.uuid.UUIDField(auto_add=True, unique=True, max_length=32, editable=False)),
                ('project_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, choices=[(0, b'unknown'), (1, b'success'), (2, b'failure'), (3, b'in_progress')])),
                ('config', sentry.db.models.fields.encrypted.EncryptedJsonField(default=dict)),
                ('duration', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'sentry_monitorcheckin',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MonitorLocation',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('guid', sentry.db.models.fields.uuid.UUIDField(auto_add=True, unique=True, max_length=32, editable=False)),
                ('name', models.CharField(max_length=128)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'sentry_monitorlocation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=64)),
                ('value', sentry.db.models.fields.encrypted.EncryptedPickledObjectField(editable=False)),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'sentry_option',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('slug', models.SlugField(unique=True)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, choices=[(0, b'active'), (1, b'pending deletion'), (2, b'deletion in progress')])),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('default_role', models.CharField(default=b'member', max_length=32, choices=[(b'member', b'Member'), (b'admin', b'Admin'), (b'manager', b'Manager'), (b'owner', b'Owner')])),
                ('flags', bitfield.models.BitField(default=1, flags=((b'allow_joinleave', b'Allow members to join and leave teams without requiring approval.'), (b'enhanced_privacy', b'Enable enhanced privacy controls to limit personally identifiable information (PII) as well as source code in things like notifications.'), (b'disable_shared_issues', b'Disable sharing of limited details on issues to anonymous users.'), (b'early_adopter', b'Enable early adopter status, gaining access to features prior to public release.'), (b'require_2fa', b'Require and enforce two-factor authentication for all members.')))),
            ],
            options={
                'db_table': 'sentry_organization',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganizationAccessRequest',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'sentry_organizationaccessrequest',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganizationAvatar',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('ident', models.CharField(unique=True, max_length=32, db_index=True)),
                ('avatar_type', models.PositiveSmallIntegerField(default=0, choices=[(0, b'letter_avatar'), (1, b'upload')])),
                ('file', sentry.db.models.fields.foreignkey.FlexibleForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sentry.File', unique=True)),
                ('organization', sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='avatar', to='sentry.Organization', unique=True)),
            ],
            options={
                'db_table': 'sentry_organizationavatar',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganizationIntegration',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('config', sentry.db.models.fields.encrypted.EncryptedJsonField(default=dict)),
                ('default_auth_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True, db_index=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, choices=[(0, b'active'), (1, b'disabled'), (2, b'pending_deletion'), (3, b'deletion_in_progress')])),
                ('integration', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Integration')),
                ('organization', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Organization')),
            ],
            options={
                'db_table': 'sentry_organizationintegration',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganizationMember',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('role', models.CharField(default=b'member', max_length=32, choices=[(b'member', b'Member'), (b'admin', b'Admin'), (b'manager', b'Manager'), (b'owner', b'Owner')])),
                ('flags', bitfield.models.BitField(default=0, flags=((b'sso:linked', b'sso:linked'), (b'sso:invalid', b'sso:invalid')))),
                ('token', models.CharField(max_length=64, unique=True, null=True, blank=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('token_expires_at', models.DateTimeField(default=None, null=True)),
                ('has_global_access', models.BooleanField(default=True)),
                ('type', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=50, blank=True)),
                ('organization', sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='member_set', to='sentry.Organization')),
            ],
            options={
                'db_table': 'sentry_organizationmember',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganizationMemberTeam',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedAutoField(serialize=False, primary_key=True)),
                ('is_active', models.BooleanField(default=True)),
                ('organizationmember', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.OrganizationMember')),
            ],
            options={
                'db_table': 'sentry_organizationmember_teams',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganizationOnboardingTask',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('task', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(choices=[(2, b'First event'), (3, b'Invite member'), (9, b'Issue tracker'), (10, b'Notification services'), (4, b'Second platform'), (5, b'User context'), (7, b'Upload sourcemaps'), (6, b'Release tracking'), (8, b'User reports')])),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(choices=[(1, b'Complete'), (2, b'Pending'), (3, b'Skipped')])),
                ('date_completed', models.DateTimeField(default=django.utils.timezone.now)),
                ('project_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(null=True, blank=True)),
                ('data', jsonfield.fields.JSONField(default=dict)),
                ('organization', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Organization')),
                ('user', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'db_table': 'sentry_organizationonboardingtask',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganizationOption',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('key', models.CharField(max_length=64)),
                ('value', sentry.db.models.fields.encrypted.EncryptedPickledObjectField(editable=False)),
                ('organization', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Organization')),
            ],
            options={
                'db_table': 'sentry_organizationoptions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProcessingIssue',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('checksum', models.CharField(max_length=40, db_index=True)),
                ('type', models.CharField(max_length=30)),
                ('data', sentry.db.models.fields.gzippeddict.GzippedDictField()),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'sentry_processingissue',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('slug', models.SlugField(null=True)),
                ('name', models.CharField(max_length=200)),
                ('forced_color', models.CharField(max_length=6, null=True, blank=True)),
                ('public', models.BooleanField(default=False)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, db_index=True, choices=[(0, 'Active'), (2, 'Pending Deletion'), (3, 'Deletion in Progress')])),
                ('first_event', models.DateTimeField(null=True)),
                ('flags', bitfield.models.BitField(default=0, null=True, flags=((b'has_releases', b'This Project has sent release data'),))),
                ('platform', models.CharField(max_length=64, null=True)),
                ('organization', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Organization')),
            ],
            options={
                'db_table': 'sentry_project',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectAvatar',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('ident', models.CharField(unique=True, max_length=32, db_index=True)),
                ('avatar_type', models.PositiveSmallIntegerField(default=0, choices=[(0, b'letter_avatar'), (1, b'upload')])),
                ('file', sentry.db.models.fields.foreignkey.FlexibleForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sentry.File', unique=True)),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='avatar', to='sentry.Project', unique=True)),
            ],
            options={
                'db_table': 'sentry_projectavatar',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectBookmark',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(db_constraint=False, blank=True, to='sentry.Project', null=True)),
                ('user', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sentry_projectbookmark',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectCfiCacheFile',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('checksum', models.CharField(max_length=40)),
                ('version', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('cache_file', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.File')),
            ],
            options={
                'abstract': False,
                'db_table': 'sentry_projectcficachefile',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectDebugFile',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('object_name', models.TextField()),
                ('cpu_name', models.CharField(max_length=40)),
                ('debug_id', models.CharField(max_length=64, db_column=b'uuid')),
                ('data', jsonfield.fields.JSONField(null=True)),
                ('file', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.File')),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project', null=True)),
            ],
            options={
                'db_table': 'sentry_projectdsymfile',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectIntegration',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('config', sentry.db.models.fields.encrypted.EncryptedJsonField(default=dict)),
                ('integration', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Integration')),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project')),
            ],
            options={
                'db_table': 'sentry_projectintegration',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectKey',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('label', models.CharField(max_length=64, null=True, blank=True)),
                ('public_key', models.CharField(max_length=32, unique=True, null=True)),
                ('secret_key', models.CharField(max_length=32, unique=True, null=True)),
                ('roles', bitfield.models.BitField(default=[b'store'], flags=((b'store', b'Event API access'), (b'api', b'Web API access')))),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, db_index=True, choices=[(0, 'Active'), (1, 'Inactive')])),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('rate_limit_count', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('rate_limit_window', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('data', jsonfield.fields.JSONField(default=dict)),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='key_set', to='sentry.Project')),
            ],
            options={
                'db_table': 'sentry_projectkey',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectOption',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('key', models.CharField(max_length=64)),
                ('value', sentry.db.models.fields.encrypted.EncryptedPickledObjectField(editable=False)),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project')),
            ],
            options={
                'db_table': 'sentry_projectoptions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectOwnership',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('raw', models.TextField(null=True)),
                ('schema', jsonfield.fields.JSONField(null=True)),
                ('fallthrough', models.BooleanField(default=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project', unique=True)),
            ],
            options={
                'db_table': 'sentry_projectownership',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectPlatform',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('project_id', sentry.db.models.fields.bounded.BoundedBigIntegerField()),
                ('platform', models.CharField(max_length=64)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_seen', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'sentry_projectplatform',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectRedirect',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('redirect_slug', models.SlugField()),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('organization', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Organization')),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project')),
            ],
            options={
                'db_table': 'sentry_projectredirect',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectSymCacheFile',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('checksum', models.CharField(max_length=40)),
                ('version', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('cache_file', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.File')),
                ('debug_file', sentry.db.models.fields.foreignkey.FlexibleForeignKey(db_column=b'dsym_file_id', on_delete=django.db.models.deletion.DO_NOTHING, to='sentry.ProjectDebugFile')),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project', null=True)),
            ],
            options={
                'abstract': False,
                'db_table': 'sentry_projectsymcachefile',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectTeam',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project')),
            ],
            options={
                'db_table': 'sentry_projectteam',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PromptsActivity',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('organization_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('project_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('feature', models.CharField(max_length=64)),
                ('data', jsonfield.fields.JSONField(default={})),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sentry_promptsactivity',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PullRequest',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('organization_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('repository_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('key', models.CharField(max_length=64)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('title', models.TextField(null=True)),
                ('message', models.TextField(null=True)),
                ('merge_commit_sha', models.CharField(max_length=64, null=True)),
                ('author', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.CommitAuthor', null=True)),
            ],
            options={
                'db_table': 'sentry_pull_request',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PullRequestCommit',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('commit', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Commit')),
                ('pull_request', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.PullRequest')),
            ],
            options={
                'db_table': 'sentry_pullrequest_commit',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RawEvent',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('event_id', models.CharField(max_length=32, null=True)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('data', sentry.db.models.fields.node.NodeField(ref_func=sentry.models.rawevent.ref_func, null=True, ref_version=1, wrapper=sentry.utils.canonical.CanonicalKeyView, blank=True)),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project')),
            ],
            options={
                'db_table': 'sentry_rawevent',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Relay',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('relay_id', models.CharField(unique=True, max_length=64)),
                ('public_key', models.CharField(max_length=200)),
                ('first_seen', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_seen', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_internal', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'sentry_relay',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('project_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('version', models.CharField(max_length=250)),
                ('ref', models.CharField(max_length=250, null=True, blank=True)),
                ('url', models.URLField(null=True, blank=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_started', models.DateTimeField(null=True, blank=True)),
                ('date_released', models.DateTimeField(null=True, blank=True)),
                ('data', jsonfield.fields.JSONField(default={})),
                ('new_groups', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0)),
                ('commit_count', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, null=True)),
                ('last_commit_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('authors', sentry.db.models.fields.array.ArrayField(null=True)),
                ('total_deploys', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, null=True)),
                ('last_deploy_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('organization', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Organization')),
                ('owner', sentry.db.models.fields.foreignkey.FlexibleForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'db_table': 'sentry_release',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReleaseCommit',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('organization_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('project_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('order', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('commit', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Commit')),
                ('release', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Release')),
            ],
            options={
                'db_table': 'sentry_releasecommit',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReleaseEnvironment',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('first_seen', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_seen', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('environment', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Environment', db_constraint=False)),
                ('organization', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Organization', db_constraint=False)),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project', null=True, db_constraint=False)),
                ('release', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Release', db_constraint=False)),
            ],
            options={
                'db_table': 'sentry_environmentrelease',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReleaseFile',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('project_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('ident', models.CharField(max_length=40)),
                ('name', models.TextField()),
                ('dist', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Distribution', null=True)),
                ('file', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.File')),
                ('organization', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Organization')),
                ('release', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Release')),
            ],
            options={
                'db_table': 'sentry_releasefile',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReleaseHeadCommit',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('organization_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('repository_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('commit', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Commit')),
                ('release', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Release')),
            ],
            options={
                'db_table': 'sentry_releaseheadcommit',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReleaseProject',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('new_groups', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, null=True)),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project')),
                ('release', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Release')),
            ],
            options={
                'db_table': 'sentry_release_project',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReleaseProjectEnvironment',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('new_issues_count', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0)),
                ('first_seen', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_seen', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('last_deploy_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True, db_index=True)),
                ('environment', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Environment')),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project')),
                ('release', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Release')),
            ],
            options={
                'db_table': 'sentry_releaseprojectenvironment',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('organization_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('name', models.CharField(max_length=200)),
                ('url', models.URLField(null=True)),
                ('provider', models.CharField(max_length=64, null=True)),
                ('external_id', models.CharField(max_length=64, null=True)),
                ('config', jsonfield.fields.JSONField(default=dict)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, db_index=True, choices=[(0, b'active'), (1, b'disabled'), (2, b'pending_deletion'), (3, b'deletion_in_progress')])),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('integration_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True, db_index=True)),
            ],
            options={
                'db_table': 'sentry_repository',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReprocessingReport',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('event_id', models.CharField(max_length=32, null=True)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project')),
            ],
            options={
                'db_table': 'sentry_reprocessingreport',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('environment_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True)),
                ('label', models.CharField(max_length=64)),
                ('data', sentry.db.models.fields.gzippeddict.GzippedDictField()),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, db_index=True, choices=[(0, b'Active'), (1, b'Inactive')])),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project')),
            ],
            options={
                'db_table': 'sentry_rule',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SavedSearch',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('query', models.TextField()),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_default', models.BooleanField(default=False)),
                ('is_global', models.NullBooleanField(default=False, db_index=True)),
                ('owner', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project', null=True)),
            ],
            options={
                'db_table': 'sentry_savedsearch',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SavedSearchUserDefault',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project')),
                ('savedsearch', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.SavedSearch')),
                ('user', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sentry_savedsearch_userdefault',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScheduledDeletion',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('guid', models.CharField(default=sentry.models.scheduledeletion.default_guid, unique=True, max_length=32)),
                ('app_label', models.CharField(max_length=64)),
                ('model_name', models.CharField(max_length=64)),
                ('object_id', sentry.db.models.fields.bounded.BoundedBigIntegerField()),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_scheduled', models.DateTimeField(default=sentry.models.scheduledeletion.default_date_schedule)),
                ('actor_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(null=True)),
                ('data', jsonfield.fields.JSONField(default={})),
                ('in_progress', models.BooleanField(default=False)),
                ('aborted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'sentry_scheduleddeletion',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScheduledJob',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('payload', jsonfield.fields.JSONField(default=dict)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_scheduled', models.DateTimeField()),
            ],
            options={
                'db_table': 'sentry_scheduledjob',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SentryApp',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('date_deleted', models.DateTimeField(null=True, blank=True)),
                ('scopes', bitfield.models.BitField(default=None, flags=((b'project:read', b'project:read'), (b'project:write', b'project:write'), (b'project:admin', b'project:admin'), (b'project:releases', b'project:releases'), (b'team:read', b'team:read'), (b'team:write', b'team:write'), (b'team:admin', b'team:admin'), (b'event:read', b'event:read'), (b'event:write', b'event:write'), (b'event:admin', b'event:admin'), (b'org:read', b'org:read'), (b'org:write', b'org:write'), (b'org:admin', b'org:admin'), (b'member:read', b'member:read'), (b'member:write', b'member:write'), (b'member:admin', b'member:admin')))),
                ('scope_list', sentry.db.models.fields.array.ArrayField(null=True)),
                ('name', models.TextField()),
                ('slug', models.CharField(unique=True, max_length=64)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, db_index=True, choices=[(0, b'unpublished'), (1, b'published')])),
                ('uuid', models.CharField(default=sentry.models.sentryapp.default_uuid, max_length=64)),
                ('redirect_url', models.URLField(null=True)),
                ('webhook_url', models.URLField()),
                ('is_alertable', models.BooleanField(default=False)),
                ('events', sentry.db.models.fields.array.ArrayField(null=True)),
                ('overview', models.TextField(null=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('application', models.OneToOneField(related_name='sentry_app', null=True, on_delete=django.db.models.deletion.SET_NULL, to='sentry.ApiApplication')),
                ('owner', sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='owned_sentry_apps', to='sentry.Organization')),
                ('proxy_user', models.OneToOneField(related_name='sentry_app', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sentry_sentryapp',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SentryAppAvatar',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('ident', models.CharField(unique=True, max_length=32, db_index=True)),
                ('avatar_type', models.PositiveSmallIntegerField(default=0, choices=[(0, b'letter_avatar'), (1, b'upload')])),
                ('file', sentry.db.models.fields.foreignkey.FlexibleForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sentry.File', unique=True)),
                ('sentry_app', sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='avatar', to='sentry.SentryApp', unique=True)),
            ],
            options={
                'db_table': 'sentry_sentryappavatar',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SentryAppInstallation',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('date_deleted', models.DateTimeField(null=True, blank=True)),
                ('uuid', models.CharField(default=sentry.models.sentryappinstallation.default_uuid, max_length=64)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('api_grant', models.OneToOneField(related_name='sentry_app_installation', null=True, on_delete=django.db.models.deletion.SET_NULL, to='sentry.ApiGrant')),
                ('authorization', models.OneToOneField(related_name='sentry_app_installation', null=True, on_delete=django.db.models.deletion.SET_NULL, to='sentry.ApiAuthorization')),
                ('organization', sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='sentry_app_installations', to='sentry.Organization')),
                ('sentry_app', sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='installations', to='sentry.SentryApp')),
            ],
            options={
                'db_table': 'sentry_sentryappinstallation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceHook',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('guid', models.CharField(max_length=32, unique=True, null=True)),
                ('actor_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('project_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('url', models.URLField(max_length=512)),
                ('secret', sentry.db.models.fields.encrypted.EncryptedTextField(default=sentry.models.servicehook.generate_secret)),
                ('events', sentry.db.models.fields.array.ArrayField(null=True)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, db_index=True, choices=[(0, b'active'), (1, b'disabled'), (2, b'pending_deletion'), (3, b'deletion_in_progress')])),
                ('version', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, choices=[(0, b'0')])),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('application', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.ApiApplication', null=True)),
            ],
            options={
                'db_table': 'sentry_servicehook',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TagKey',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('project_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(db_index=True)),
                ('key', models.CharField(max_length=32)),
                ('values_seen', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0)),
                ('label', models.CharField(max_length=64, null=True)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, choices=[(0, 'Visible'), (1, 'Pending Deletion'), (2, 'Deletion in Progress')])),
            ],
            options={
                'db_table': 'sentry_filterkey',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TagValue',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('project_id', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(null=True, db_index=True)),
                ('key', models.CharField(max_length=32)),
                ('value', models.CharField(max_length=200)),
                ('data', sentry.db.models.fields.gzippeddict.GzippedDictField(null=True, blank=True)),
                ('times_seen', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0)),
                ('last_seen', models.DateTimeField(default=django.utils.timezone.now, null=True, db_index=True)),
                ('first_seen', models.DateTimeField(default=django.utils.timezone.now, null=True, db_index=True)),
            ],
            options={
                'db_table': 'sentry_filtervalue',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=64)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, choices=[(0, 'Active'), (1, 'Pending Deletion'), (2, 'Deletion in Progress')])),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('organization', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Organization')),
            ],
            options={
                'db_table': 'sentry_team',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TeamAvatar',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('ident', models.CharField(unique=True, max_length=32, db_index=True)),
                ('avatar_type', models.PositiveSmallIntegerField(default=0, choices=[(0, b'letter_avatar'), (1, b'upload')])),
                ('file', sentry.db.models.fields.foreignkey.FlexibleForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sentry.File', unique=True)),
                ('team', sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='avatar', to='sentry.Team', unique=True)),
            ],
            options={
                'db_table': 'sentry_teamavatar',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserAvatar',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('ident', models.CharField(unique=True, max_length=32, db_index=True)),
                ('avatar_type', models.PositiveSmallIntegerField(default=0, choices=[(0, b'letter_avatar'), (1, b'upload'), (2, b'gravatar')])),
                ('file', sentry.db.models.fields.foreignkey.FlexibleForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sentry.File', unique=True)),
                ('user', sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='avatar', to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
                'db_table': 'sentry_useravatar',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserEmail',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('email', models.EmailField(max_length=75, verbose_name='email address')),
                ('validation_hash', models.CharField(default=sentry.models.useremail.default_validation_hash, max_length=32)),
                ('date_hash_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_verified', models.BooleanField(default=False, help_text='Designates whether this user has confirmed their email.', verbose_name='verified')),
                ('user', sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='emails', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sentry_useremail',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserIP',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('country_code', models.CharField(max_length=16, null=True)),
                ('region_code', models.CharField(max_length=16, null=True)),
                ('first_seen', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_seen', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sentry_userip',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserOption',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('key', models.CharField(max_length=64)),
                ('value', sentry.db.models.fields.encrypted.EncryptedPickledObjectField(editable=False)),
                ('organization', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Organization', null=True)),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project', null=True)),
                ('user', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sentry_useroption',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserPermission',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('permission', models.CharField(max_length=32)),
                ('user', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sentry_userpermission',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserReport',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('event_user_id', sentry.db.models.fields.bounded.BoundedBigIntegerField(null=True)),
                ('event_id', models.CharField(max_length=32)),
                ('name', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=75)),
                ('comments', models.TextField()),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('environment', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Environment', null=True)),
                ('group', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Group', null=True)),
                ('project', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project')),
            ],
            options={
                'db_table': 'sentry_userreport',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Widget',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('order', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('title', models.CharField(max_length=255)),
                ('display_type', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(choices=[(0, b'line'), (1, b'area'), (2, b'stacked_area'), (3, b'bar'), (4, b'pie'), (5, b'table'), (6, b'world_map'), (7, b'percentage_area_chart')])),
                ('display_options', jsonfield.fields.JSONField(default={})),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, choices=[(0, b'active'), (1, b'disabled'), (2, b'pending_deletion'), (3, b'deletion_in_progress')])),
                ('dashboard', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Dashboard')),
            ],
            options={
                'db_table': 'sentry_widget',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WidgetDataSource',
            fields=[
                ('id', sentry.db.models.fields.bounded.BoundedBigAutoField(serialize=False, primary_key=True)),
                ('type', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(choices=[(0, b'discover_saved_search')])),
                ('name', models.CharField(max_length=255)),
                ('data', jsonfield.fields.JSONField(default={})),
                ('order', sentry.db.models.fields.bounded.BoundedPositiveIntegerField()),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0, choices=[(0, b'active'), (1, b'disabled'), (2, b'pending_deletion'), (3, b'deletion_in_progress')])),
                ('widget', sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Widget')),
            ],
            options={
                'db_table': 'sentry_widgetdatasource',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='widgetdatasource',
            unique_together=set([('widget', 'name'), ('widget', 'order')]),
        ),
        migrations.AlterUniqueTogether(
            name='widget',
            unique_together=set([('dashboard', 'title'), ('dashboard', 'order')]),
        ),
        migrations.AlterUniqueTogether(
            name='userreport',
            unique_together=set([('project', 'event_id')]),
        ),
        migrations.AlterIndexTogether(
            name='userreport',
            index_together=set([('project', 'date_added'), ('project', 'event_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='userpermission',
            unique_together=set([('user', 'permission')]),
        ),
        migrations.AlterUniqueTogether(
            name='useroption',
            unique_together=set([('user', 'project', 'key'), ('user', 'organization', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='userip',
            unique_together=set([('user', 'ip_address')]),
        ),
        migrations.AlterUniqueTogether(
            name='useremail',
            unique_together=set([('user', 'email')]),
        ),
        migrations.AlterUniqueTogether(
            name='team',
            unique_together=set([('organization', 'slug')]),
        ),
        migrations.AlterUniqueTogether(
            name='tagvalue',
            unique_together=set([('project_id', 'key', 'value')]),
        ),
        migrations.AlterIndexTogether(
            name='tagvalue',
            index_together=set([('project_id', 'key', 'last_seen')]),
        ),
        migrations.AlterUniqueTogether(
            name='tagkey',
            unique_together=set([('project_id', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='scheduleddeletion',
            unique_together=set([('app_label', 'model_name', 'object_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='savedsearchuserdefault',
            unique_together=set([('project', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='savedsearch',
            unique_together=set([('project', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='reprocessingreport',
            unique_together=set([('project', 'event_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='repository',
            unique_together=set([('organization_id', 'provider', 'external_id'), ('organization_id', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='releaseprojectenvironment',
            unique_together=set([('project', 'release', 'environment')]),
        ),
        migrations.AlterUniqueTogether(
            name='releaseproject',
            unique_together=set([('project', 'release')]),
        ),
        migrations.AlterUniqueTogether(
            name='releaseheadcommit',
            unique_together=set([('repository_id', 'release')]),
        ),
        migrations.AlterUniqueTogether(
            name='releasefile',
            unique_together=set([('release', 'ident')]),
        ),
        migrations.AlterIndexTogether(
            name='releasefile',
            index_together=set([('release', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='releaseenvironment',
            unique_together=set([('organization', 'release', 'environment')]),
        ),
        migrations.AlterUniqueTogether(
            name='releasecommit',
            unique_together=set([('release', 'commit'), ('release', 'order')]),
        ),
        migrations.AddField(
            model_name='release',
            name='projects',
            field=models.ManyToManyField(related_name='releases', through='sentry.ReleaseProject', to='sentry.Project'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='release',
            unique_together=set([('organization', 'version')]),
        ),
        migrations.AlterUniqueTogether(
            name='rawevent',
            unique_together=set([('project', 'event_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='pullrequestcommit',
            unique_together=set([('pull_request', 'commit')]),
        ),
        migrations.AlterUniqueTogether(
            name='pullrequest',
            unique_together=set([('repository_id', 'key')]),
        ),
        migrations.AlterIndexTogether(
            name='pullrequest',
            index_together=set([('repository_id', 'date_added'), ('organization_id', 'merge_commit_sha')]),
        ),
        migrations.AlterUniqueTogether(
            name='promptsactivity',
            unique_together=set([('user', 'feature', 'organization_id', 'project_id')]),
        ),
        migrations.AddField(
            model_name='projectteam',
            name='team',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Team'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='projectteam',
            unique_together=set([('project', 'team')]),
        ),
        migrations.AlterUniqueTogether(
            name='projectsymcachefile',
            unique_together=set([('project', 'debug_file')]),
        ),
        migrations.AlterUniqueTogether(
            name='projectredirect',
            unique_together=set([('organization', 'redirect_slug')]),
        ),
        migrations.AlterUniqueTogether(
            name='projectplatform',
            unique_together=set([('project_id', 'platform')]),
        ),
        migrations.AlterUniqueTogether(
            name='projectoption',
            unique_together=set([('project', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='projectintegration',
            unique_together=set([('project', 'integration')]),
        ),
        migrations.AlterIndexTogether(
            name='projectdebugfile',
            index_together=set([('project', 'debug_id')]),
        ),
        migrations.AddField(
            model_name='projectcficachefile',
            name='debug_file',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(db_column=b'dsym_file_id', on_delete=django.db.models.deletion.DO_NOTHING, to='sentry.ProjectDebugFile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projectcficachefile',
            name='project',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='projectcficachefile',
            unique_together=set([('project', 'debug_file')]),
        ),
        migrations.AlterUniqueTogether(
            name='projectbookmark',
            unique_together=set([('project', 'user')]),
        ),
        migrations.AddField(
            model_name='project',
            name='teams',
            field=models.ManyToManyField(related_name='teams', through='sentry.ProjectTeam', to='sentry.Team'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='project',
            unique_together=set([('organization', 'slug')]),
        ),
        migrations.AddField(
            model_name='processingissue',
            name='project',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='processingissue',
            unique_together=set([('project', 'checksum', 'type')]),
        ),
        migrations.AlterUniqueTogether(
            name='organizationoption',
            unique_together=set([('organization', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='organizationonboardingtask',
            unique_together=set([('organization', 'task')]),
        ),
        migrations.AddField(
            model_name='organizationmemberteam',
            name='team',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Team'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='organizationmemberteam',
            unique_together=set([('team', 'organizationmember')]),
        ),
        migrations.AddField(
            model_name='organizationmember',
            name='teams',
            field=models.ManyToManyField(to='sentry.Team', through='sentry.OrganizationMemberTeam', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='organizationmember',
            name='user',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='sentry_orgmember_set', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='organizationmember',
            unique_together=set([('organization', 'user'), ('organization', 'email')]),
        ),
        migrations.AlterUniqueTogether(
            name='organizationintegration',
            unique_together=set([('organization', 'integration')]),
        ),
        migrations.AddField(
            model_name='organizationaccessrequest',
            name='member',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.OrganizationMember'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='organizationaccessrequest',
            name='team',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Team'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='organizationaccessrequest',
            unique_together=set([('team', 'member')]),
        ),
        migrations.AddField(
            model_name='organization',
            name='members',
            field=models.ManyToManyField(related_name='org_memberships', through='sentry.OrganizationMember', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='monitorcheckin',
            name='location',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.MonitorLocation', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='monitorcheckin',
            name='monitor',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Monitor'),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='monitor',
            index_together=set([('type', 'next_checkin')]),
        ),
        migrations.AlterUniqueTogether(
            name='latestrelease',
            unique_together=set([('repository_id', 'environment_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='integrationexternalproject',
            unique_together=set([('organization_integration_id', 'external_id')]),
        ),
        migrations.AddField(
            model_name='integration',
            name='organizations',
            field=models.ManyToManyField(related_name='integrations', through='sentry.OrganizationIntegration', to='sentry.Organization'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='integration',
            name='projects',
            field=models.ManyToManyField(related_name='integrations', through='sentry.ProjectIntegration', to='sentry.Project'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='integration',
            unique_together=set([('provider', 'external_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='identityprovider',
            unique_together=set([('type', 'external_id')]),
        ),
        migrations.AddField(
            model_name='identity',
            name='idp',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.IdentityProvider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='identity',
            name='user',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='identity',
            unique_together=set([('idp', 'external_id'), ('idp', 'user')]),
        ),
        migrations.AddField(
            model_name='grouptombstone',
            name='project',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='grouptagvalue',
            unique_together=set([('group_id', 'key', 'value')]),
        ),
        migrations.AlterIndexTogether(
            name='grouptagvalue',
            index_together=set([('project_id', 'key', 'value', 'last_seen')]),
        ),
        migrations.AlterUniqueTogether(
            name='grouptagkey',
            unique_together=set([('project_id', 'group_id', 'key')]),
        ),
        migrations.AddField(
            model_name='groupsubscription',
            name='project',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='subscription_set', to='sentry.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='groupsubscription',
            name='user',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='groupsubscription',
            unique_together=set([('group', 'user')]),
        ),
        migrations.AddField(
            model_name='groupshare',
            name='project',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='groupshare',
            name='user',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='groupseen',
            name='project',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='groupseen',
            name='user',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL, db_index=False),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='groupseen',
            unique_together=set([('user', 'group')]),
        ),
        migrations.AddField(
            model_name='grouprulestatus',
            name='project',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='grouprulestatus',
            name='rule',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Rule'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='grouprulestatus',
            unique_together=set([('rule', 'group')]),
        ),
        migrations.AddField(
            model_name='groupresolution',
            name='release',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Release'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='grouprelease',
            unique_together=set([('group_id', 'release_id', 'environment')]),
        ),
        migrations.AlterUniqueTogether(
            name='groupmeta',
            unique_together=set([('group', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='grouplink',
            unique_together=set([('group_id', 'linked_type', 'linked_id')]),
        ),
        migrations.AddField(
            model_name='grouphash',
            name='project',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='grouphash',
            unique_together=set([('project', 'hash')]),
        ),
        migrations.AlterUniqueTogether(
            name='groupenvironment',
            unique_together=set([('group_id', 'environment_id')]),
        ),
        migrations.AlterIndexTogether(
            name='groupenvironment',
            index_together=set([('environment_id', 'first_release_id')]),
        ),
        migrations.AddField(
            model_name='groupemailthread',
            name='project',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='groupemail_set', to='sentry.Project'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='groupemailthread',
            unique_together=set([('email', 'msgid'), ('email', 'group')]),
        ),
        migrations.AlterUniqueTogether(
            name='groupcommitresolution',
            unique_together=set([('group_id', 'commit_id')]),
        ),
        migrations.AddField(
            model_name='groupbookmark',
            name='project',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='bookmark_set', to='sentry.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='groupbookmark',
            name='user',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='sentry_bookmark_set', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='groupbookmark',
            unique_together=set([('project', 'user', 'group')]),
        ),
        migrations.AddField(
            model_name='groupassignee',
            name='project',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='assignee_set1', to='sentry.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='groupassignee',
            name='team',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='sentry_assignee_set1', to='sentry.Team', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='groupassignee',
            name='user',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='sentry_assignee_set1', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='first_release',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sentry.Release', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='project',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='group',
            unique_together=set([('project', 'short_id')]),
        ),
        migrations.AlterIndexTogether(
            name='group',
            index_together=set([('project', 'first_release')]),
        ),
        migrations.AddField(
            model_name='fileblobowner',
            name='organization',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Organization'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='fileblobowner',
            unique_together=set([('blob', 'organization')]),
        ),
        migrations.AlterUniqueTogether(
            name='fileblobindex',
            unique_together=set([('file', 'blob', 'offset')]),
        ),
        migrations.AddField(
            model_name='file',
            name='blob',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='legacy_blob', to='sentry.FileBlob', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='file',
            name='blobs',
            field=models.ManyToManyField(to='sentry.FileBlob', through='sentry.FileBlobIndex'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='featureadoption',
            name='organization',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Organization'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='featureadoption',
            unique_together=set([('organization', 'feature_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='externalissue',
            unique_together=set([('organization_id', 'integration_id', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='eventuser',
            unique_together=set([('project_id', 'hash'), ('project_id', 'ident')]),
        ),
        migrations.AlterIndexTogether(
            name='eventuser',
            index_together=set([('project_id', 'username'), ('project_id', 'ip_address'), ('project_id', 'email')]),
        ),
        migrations.AlterUniqueTogether(
            name='eventtag',
            unique_together=set([('event_id', 'key_id', 'value_id')]),
        ),
        migrations.AlterIndexTogether(
            name='eventtag',
            index_together=set([('group_id', 'key_id', 'value_id')]),
        ),
        migrations.AddField(
            model_name='eventprocessingissue',
            name='processing_issue',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.ProcessingIssue'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventprocessingissue',
            name='raw_event',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.RawEvent'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='eventprocessingissue',
            unique_together=set([('raw_event', 'processing_issue')]),
        ),
        migrations.AlterUniqueTogether(
            name='eventmapping',
            unique_together=set([('project_id', 'event_id')]),
        ),
        migrations.AddField(
            model_name='eventattachment',
            name='file',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.File'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='eventattachment',
            unique_together=set([('project_id', 'event_id', 'file')]),
        ),
        migrations.AlterIndexTogether(
            name='eventattachment',
            index_together=set([('project_id', 'date_added')]),
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('project_id', 'event_id')]),
        ),
        migrations.AlterIndexTogether(
            name='event',
            index_together=set([('group_id', 'datetime')]),
        ),
        migrations.AddField(
            model_name='environmentproject',
            name='project',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='environmentproject',
            unique_together=set([('project', 'environment')]),
        ),
        migrations.AddField(
            model_name='environment',
            name='projects',
            field=models.ManyToManyField(to='sentry.Project', through='sentry.EnvironmentProject'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='environment',
            unique_together=set([('organization_id', 'name')]),
        ),
        migrations.AddField(
            model_name='distribution',
            name='release',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Release'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='distribution',
            unique_together=set([('release', 'name')]),
        ),
        migrations.AddField(
            model_name='discoversavedqueryproject',
            name='project',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='discoversavedqueryproject',
            unique_together=set([('project', 'discover_saved_query')]),
        ),
        migrations.AddField(
            model_name='discoversavedquery',
            name='organization',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Organization'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='discoversavedquery',
            name='projects',
            field=models.ManyToManyField(to='sentry.Project', through='sentry.DiscoverSavedQueryProject'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='deploy',
            name='release',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Release'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dashboard',
            name='organization',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Organization'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='dashboard',
            unique_together=set([('organization', 'title')]),
        ),
        migrations.AddField(
            model_name='counter',
            name='project',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project', unique=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='commitfilechange',
            unique_together=set([('commit', 'filename')]),
        ),
        migrations.AlterUniqueTogether(
            name='commitauthor',
            unique_together=set([('organization_id', 'email'), ('organization_id', 'external_id')]),
        ),
        migrations.AddField(
            model_name='commit',
            name='author',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.CommitAuthor', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='commit',
            unique_together=set([('repository_id', 'key')]),
        ),
        migrations.AlterIndexTogether(
            name='commit',
            index_together=set([('repository_id', 'date_added')]),
        ),
        migrations.AlterUniqueTogether(
            name='broadcastseen',
            unique_together=set([('broadcast', 'user')]),
        ),
        migrations.AddField(
            model_name='authprovider',
            name='default_teams',
            field=models.ManyToManyField(to='sentry.Team', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authprovider',
            name='organization',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Organization', unique=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authidentity',
            name='auth_provider',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.AuthProvider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authidentity',
            name='user',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='authidentity',
            unique_together=set([('auth_provider', 'ident'), ('auth_provider', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='authenticator',
            unique_together=set([('user', 'type')]),
        ),
        migrations.AddField(
            model_name='auditlogentry',
            name='organization',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Organization'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='auditlogentry',
            name='target_user',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='audit_targets', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='assistantactivity',
            unique_together=set([('user', 'guide_id')]),
        ),
        migrations.AddField(
            model_name='apikey',
            name='organization',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(related_name='key_set', to='sentry.Organization'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='apiauthorization',
            unique_together=set([('user', 'application')]),
        ),
        migrations.AddField(
            model_name='activity',
            name='group',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Group', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='project',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to='sentry.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='user',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
