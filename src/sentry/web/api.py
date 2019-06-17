from __future__ import absolute_import, print_function

import base64
import math

import jsonschema
import logging
import random
import six
import traceback

from time import time

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.utils.encoding import force_bytes
from django.views.decorators.cache import never_cache, cache_control
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View as BaseView
from functools import wraps

from sentry import quotas, tsdb, options
from sentry.coreapi import (
    APIError, APIForbidden, APIRateLimited, ClientApiHelper, ClientAuthHelper,
    SecurityAuthHelper, safely_load_json_string, logger as api_logger
)
from sentry.event_manager import EventManager
from sentry.interfaces import schemas
from sentry.interfaces.base import get_interface
from sentry.models import Project, OrganizationOption, Organization
from sentry.signals import (
    event_accepted, event_dropped, event_filtered, event_received)
from sentry.quotas.base import RateLimit
from sentry.utils import json, metrics
from sentry.utils.data_filters import FILTER_STAT_KEYS_TO_VALUES
from sentry.utils.data_scrubber import SensitiveDataFilter
from sentry.utils.dates import to_datetime
from sentry.utils.http import (
    is_valid_origin,
    get_origins,
    is_same_domain,
)
from sentry.utils.pubsub import QueuedPublisherService, KafkaPublisher
from sentry.utils.safe import safe_execute
from sentry.web.helpers import render_to_response

logger = logging.getLogger('sentry')
minidumps_logger = logging.getLogger('sentry.minidumps')

# Transparent 1x1 gif
# See http://probablyprogramming.com/2009/03/15/the-tiniest-gif-ever
PIXEL = base64.b64decode('R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=')

PROTOCOL_VERSIONS = frozenset(('2.0', '3', '4', '5', '6', '7'))

kafka_publisher = QueuedPublisherService(
    KafkaPublisher(
        getattr(
            settings,
            'KAFKA_RAW_EVENTS_PUBLISHER_CONNECTION',
            None),
        asynchronous=False)
) if getattr(settings, 'KAFKA_RAW_EVENTS_PUBLISHER_ENABLED', False) else None


def api(func):
    @wraps(func)
    def wrapped(request, *args, **kwargs):
        data = func(request, *args, **kwargs)
        if request.is_ajax():
            response = HttpResponse(data)
            response['Content-Type'] = 'application/json'
        else:
            ref = request.META.get('HTTP_REFERER')
            if ref is None or not is_same_domain(ref, request.build_absolute_uri()):
                ref = reverse('sentry')
            return HttpResponseRedirect(ref)
        return response

    return wrapped


def process_event(event_manager, project, key, remote_addr, helper, attachments):
    event_received.send_robust(ip=remote_addr, project=project, sender=process_event)

    start_time = time()
    tsdb_start_time = to_datetime(start_time)
    should_filter, filter_reason = event_manager.should_filter()
    if should_filter:
        increment_list = [
            (tsdb.models.project_total_received, project.id),
            (tsdb.models.project_total_blacklisted, project.id),
            (tsdb.models.organization_total_received,
                project.organization_id),
            (tsdb.models.organization_total_blacklisted,
                project.organization_id),
            (tsdb.models.key_total_received, key.id),
            (tsdb.models.key_total_blacklisted, key.id),
        ]
        try:
            increment_list.append(
                (FILTER_STAT_KEYS_TO_VALUES[filter_reason], project.id))
        # should error when filter_reason does not match a key in FILTER_STAT_KEYS_TO_VALUES
        except KeyError:
            pass

        tsdb.incr_multi(
            increment_list,
            timestamp=tsdb_start_time,
        )

        metrics.incr(
            'events.blacklisted', tags={'reason': filter_reason}, skip_internal=False
        )
        event_filtered.send_robust(
            ip=remote_addr,
            project=project,
            sender=process_event,
        )
        raise APIForbidden('Event dropped due to filter: %s' % (filter_reason,))

    # TODO: improve this API (e.g. make RateLimit act on __ne__)
    rate_limit = safe_execute(
        quotas.is_rate_limited, project=project, key=key, _with_transaction=False
    )
    if isinstance(rate_limit, bool):
        rate_limit = RateLimit(is_limited=rate_limit, retry_after=None)

    # XXX(dcramer): when the rate limiter fails we drop events to ensure
    # it cannot cascade
    if rate_limit is None or rate_limit.is_limited:
        if rate_limit is None:
            api_logger.debug('Dropped event due to error with rate limiter')
        tsdb.incr_multi(
            [
                (tsdb.models.project_total_received, project.id),
                (tsdb.models.project_total_rejected, project.id),
                (tsdb.models.organization_total_received,
                    project.organization_id),
                (tsdb.models.organization_total_rejected,
                    project.organization_id),
                (tsdb.models.key_total_received, key.id),
                (tsdb.models.key_total_rejected, key.id),
            ],
            timestamp=tsdb_start_time,
        )
        metrics.incr(
            'events.dropped',
            tags={
                'reason': rate_limit.reason_code if rate_limit else 'unknown',
            },
            skip_internal=False,
        )
        event_dropped.send_robust(
            ip=remote_addr,
            project=project,
            reason_code=rate_limit.reason_code if rate_limit else None,
            sender=process_event,
        )
        if rate_limit is not None:
            raise APIRateLimited(rate_limit.retry_after)
    else:
        tsdb.incr_multi(
            [
                (tsdb.models.project_total_received, project.id),
                (tsdb.models.organization_total_received,
                    project.organization_id),
                (tsdb.models.key_total_received, key.id),
            ],
            timestamp=tsdb_start_time,
        )

    org_options = OrganizationOption.objects.get_all_values(
        project.organization_id)

    data = event_manager.get_data()
    del event_manager

    event_id = data['event_id']

    # TODO(dcramer): ideally we'd only validate this if the event_id was
    # supplied by the user
    cache_key = 'ev:%s:%s' % (project.id, event_id, )

    if cache.get(cache_key) is not None:
        raise APIForbidden(
            'An event with the same ID already exists (%s)' % (event_id, ))

    scrub_ip_address = (org_options.get('sentry:require_scrub_ip_address', False) or
                        project.get_option('sentry:scrub_ip_address', False))
    scrub_data = (org_options.get('sentry:require_scrub_data', False) or
                  project.get_option('sentry:scrub_data', True))

    if scrub_data:
        # We filter data immediately before it ever gets into the queue
        sensitive_fields_key = 'sentry:sensitive_fields'
        sensitive_fields = (
            org_options.get(sensitive_fields_key, []) +
            project.get_option(sensitive_fields_key, [])
        )

        exclude_fields_key = 'sentry:safe_fields'
        exclude_fields = (
            org_options.get(exclude_fields_key, []) +
            project.get_option(exclude_fields_key, [])
        )

        scrub_defaults = (org_options.get('sentry:require_scrub_defaults', False) or
                          project.get_option('sentry:scrub_defaults', True))

        SensitiveDataFilter(
            fields=sensitive_fields,
            include_defaults=scrub_defaults,
            exclude_fields=exclude_fields,
        ).apply(data)

    if scrub_ip_address:
        # We filter data immediately before it ever gets into the queue
        helper.ensure_does_not_have_ip(data)

    # mutates data (strips a lot of context if not queued)
    helper.insert_data_to_database(data, start_time=start_time, attachments=attachments)

    cache.set(cache_key, '', 60 * 5)

    api_logger.debug('New event received (%s)', event_id)

    event_accepted.send_robust(
        ip=remote_addr,
        data=data,
        project=project,
        sender=process_event,
    )

    return event_id


class APIView(BaseView):
    auth_helper_cls = ClientAuthHelper

    def _get_project_from_id(self, project_id):
        if not project_id:
            return
        if not project_id.isdigit():
            raise APIError('Invalid project_id: %r' % project_id)
        try:
            return Project.objects.get_from_cache(id=project_id)
        except Project.DoesNotExist:
            raise APIError('Invalid project_id: %r' % project_id)

    def _parse_header(self, request, helper, project):
        auth = self.auth_helper_cls.auth_from_request(request)

        if auth.version not in PROTOCOL_VERSIONS:
            raise APIError(
                'Client using unsupported server protocol version (%r)' %
                six.text_type(auth.version or '')
            )

        if not auth.client:
            raise APIError("Client did not send 'client' identifier")

        return auth

    def _publish_to_kafka(self, request):
        """
        Sends raw event data to Kafka for later offline processing.
        """
        try:
            # This may fail when we e.g. send a multipart form. We ignore those errors for now.
            data = request.body

            if not data or len(data) > options.get('kafka-publisher.max-event-size'):
                return

            # Sampling
            if random.random() >= options.get('kafka-publisher.raw-event-sample-rate'):
                return

            # We want to send only serializable items from request.META
            meta = {}
            for key, value in request.META.items():
                try:
                    json.dumps([key, value])
                    meta[key] = value
                except (TypeError, ValueError):
                    pass

            meta['SENTRY_API_VIEW_NAME'] = self.__class__.__name__

            kafka_publisher.publish(
                channel=getattr(settings, 'KAFKA_RAW_EVENTS_PUBLISHER_TOPIC', 'raw-store-events'),
                value=json.dumps([meta, base64.b64encode(data)])
            )
        except Exception as e:
            logger.debug("Cannot publish event to Kafka: {}".format(e.message))

    @csrf_exempt
    @never_cache
    def dispatch(self, request, project_id=None, *args, **kwargs):
        helper = ClientApiHelper(
            agent=request.META.get('HTTP_USER_AGENT'),
            project_id=project_id,
            ip_address=request.META['REMOTE_ADDR'],
        )
        origin = None

        if kafka_publisher is not None:
            self._publish_to_kafka(request)

        try:
            origin = self.auth_helper_cls.origin_from_request(request)

            response = self._dispatch(
                request, helper, project_id=project_id, origin=origin, *args, **kwargs
            )
        except APIError as e:
            context = {
                'error': force_bytes(e.msg, errors='replace'),
            }
            if e.name:
                context['error_name'] = e.name

            response = HttpResponse(
                json.dumps(context), content_type='application/json', status=e.http_status
            )
            # Set X-Sentry-Error as in many cases it is easier to inspect the headers
            response['X-Sentry-Error'] = context['error']

            if isinstance(e, APIRateLimited) and e.retry_after is not None:
                response['Retry-After'] = six.text_type(int(math.ceil(e.retry_after)))

        except Exception as e:
            # TODO(dcramer): test failures are not outputting the log message
            # here
            if settings.DEBUG:
                content = traceback.format_exc()
            else:
                content = ''
            logger.exception(e)
            response = HttpResponse(
                content, content_type='text/plain', status=500)

        # TODO(dcramer): it'd be nice if we had an incr_multi method so
        # tsdb could optimize this
        metrics.incr('client-api.all-versions.requests', skip_internal=False)
        metrics.incr('client-api.all-versions.responses.%s' %
                     (response.status_code, ), skip_internal=False)
        metrics.incr(
            'client-api.all-versions.responses.%sxx' % (six.text_type(response.status_code)[0],),
            skip_internal=False,
        )

        if helper.context.version:
            metrics.incr(
                'client-api.v%s.requests' % (helper.context.version, ),
                skip_internal=False,
            )
            metrics.incr(
                'client-api.v%s.responses.%s' % (helper.context.version, response.status_code),
                skip_internal=False,
            )
            metrics.incr(
                'client-api.v%s.responses.%sxx' % (helper.context.version,
                                                   six.text_type(response.status_code)[0]),
                skip_internal=False,
            )

        if response.status_code != 200 and origin:
            # We allow all origins on errors
            response['Access-Control-Allow-Origin'] = '*'

        if origin:
            response['Access-Control-Allow-Headers'] = \
                'X-Sentry-Auth, X-Requested-With, Origin, Accept, ' \
                'Content-Type, Authentication'
            response['Access-Control-Allow-Methods'] = \
                ', '.join(self._allowed_methods())
            response['Access-Control-Expose-Headers'] = \
                'X-Sentry-Error, Retry-After'

        return response

    def _dispatch(self, request, helper, project_id=None, origin=None, *args, **kwargs):
        request.user = AnonymousUser()

        project = self._get_project_from_id(project_id)
        if project:
            helper.context.bind_project(project)

        if origin is not None:
            # This check is specific for clients who need CORS support
            if not project:
                raise APIError('Client must be upgraded for CORS support')
            if not is_valid_origin(origin, project):
                tsdb.incr(tsdb.models.project_total_received_cors,
                          project.id)
                raise APIForbidden('Invalid origin: %s' % (origin, ))

        # XXX: It seems that the OPTIONS call does not always include custom headers
        if request.method == 'OPTIONS':
            response = self.options(request, project)
        else:
            auth = self._parse_header(request, helper, project)

            key = helper.project_key_from_auth(auth)

            # Legacy API was /api/store/ and the project ID was only available elsewhere
            if not project:
                project = Project.objects.get_from_cache(id=key.project_id)
                helper.context.bind_project(project)
            elif key.project_id != project.id:
                raise APIError('Two different projects were specified')

            helper.context.bind_auth(auth)

            # Explicitly bind Organization so we don't implicitly query it later
            # this just allows us to comfortably assure that `project.organization` is safe.
            # This also allows us to pull the object from cache, instead of being
            # implicitly fetched from database.
            project.organization = Organization.objects.get_from_cache(
                id=project.organization_id)

            response = super(APIView, self).dispatch(
                request=request, project=project, auth=auth, helper=helper, key=key, **kwargs
            )

        if origin:
            if origin == 'null':
                # If an Origin is `null`, but we got this far, that means
                # we've gotten past our CORS check for some reason. But the
                # problem is that we can't return "null" as a valid response
                # to `Access-Control-Allow-Origin` and we don't have another
                # value to work with, so just allow '*' since they've gotten
                # this far.
                response['Access-Control-Allow-Origin'] = '*'
            else:
                response['Access-Control-Allow-Origin'] = origin

        return response

    # XXX: backported from Django 1.5
    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]

    def options(self, request, *args, **kwargs):
        response = HttpResponse()
        response['Allow'] = ', '.join(self._allowed_methods())
        response['Content-Length'] = '0'
        return response


class StoreView(APIView):
    """
    The primary endpoint for storing new events.

    This will validate the client's authentication and data, and if
    successful pass on the payload to the internal database handler.

    Authentication works in three flavors:

    1. Explicit signed requests

       These are implemented using the documented signed request protocol, and
       require an authentication header which is signed using with the project
       member's secret key.

    2. CORS Secured Requests

       Generally used for communications with client-side platforms (such as
       JavaScript in the browser), they require a standard header, excluding
       the signature and timestamp requirements, and must be listed in the
       origins for the given project (or the global origins).

    3. Implicit trusted requests

       Used by the Sentry core, they are only available from same-domain requests
       and do not require any authentication information. They only require that
       the user be authenticated, and a project_id be sent in the GET variables.

    """
    type_name = 'store'

    def post(self, request, **kwargs):
        try:
            data = request.body
        except Exception as e:
            logger.exception(e)
            # We were unable to read the body.
            # This would happen if a request were submitted
            # as a multipart form for example, where reading
            # body yields an Exception. There's also not a more
            # sane exception to catch here. This will ultimately
            # bubble up as an APIError.
            data = None

        response_or_event_id = self.process(request, data=data, **kwargs)
        if isinstance(response_or_event_id, HttpResponse):
            return response_or_event_id
        return HttpResponse(
            json.dumps({
                'id': response_or_event_id,
            }), content_type='application/json'
        )

    def get(self, request, **kwargs):
        data = request.GET.get('sentry_data', '')
        response_or_event_id = self.process(request, data=data, **kwargs)

        # Return a simple 1x1 gif for browser so they don't throw a warning
        response = HttpResponse(PIXEL, 'image/gif')
        if not isinstance(response_or_event_id, HttpResponse):
            response['X-Sentry-ID'] = response_or_event_id
        return response

    def pre_normalize(self, data, helper):
        """Mutate the given EventManager. Hook for subtypes of StoreView (CSP)"""
        pass

    def process(self, request, project, key, auth, helper, data, attachments=None, **kwargs):
        metrics.incr('events.total', skip_internal=False)

        if not data:
            raise APIError('No JSON data was found')

        remote_addr = request.META['REMOTE_ADDR']

        event_manager = EventManager(
            data,
            project=project,
            key=key,
            auth=auth,
            client_ip=remote_addr,
            user_agent=helper.context.agent,
            version=auth.version,
            content_encoding=request.META.get('HTTP_CONTENT_ENCODING', ''),
        )
        del data

        self.pre_normalize(event_manager, helper)
        event_manager.normalize()

        agent = request.META.get('HTTP_USER_AGENT')

        # TODO: Some form of coordination between the Kafka consumer
        # and this method (the 'relay') to decide whether a 429 should
        # be returned here.

        # Everything before this will eventually be done in the relay.
        if (kafka_publisher is not None
                and not attachments
                and random.random() < options.get('store.kafka-sample-rate')):

            process_in_kafka = options.get('store.process-in-kafka')

            try:
                kafka_publisher.publish(
                    channel=getattr(settings, 'KAFKA_EVENTS_PUBLISHER_TOPIC', 'store-events'),
                    # Relay will (eventually) need to produce a Kafka message
                    # with this JSON format.
                    value=json.dumps({
                        'data': dict(event_manager.get_data()),
                        'project_id': project.id,
                        'auth': {
                            'sentry_client': auth.client,
                            'sentry_version': auth.version,
                            'sentry_secret': auth.secret_key,
                            'sentry_key': auth.public_key,
                            'is_public': auth.is_public,
                        },
                        'remote_addr': remote_addr,
                        'agent': agent,
                        # Whether or not the Kafka consumer is in charge
                        # of actually processing this event.
                        'should_process': process_in_kafka,
                    })
                )
            except Exception as e:
                logger.exception("Cannot publish event to Kafka: {}".format(e.message))
            else:
                if process_in_kafka:
                    # This event will be processed by the Kafka consumer, so we
                    # shouldn't double process it here.
                    return event_manager.get_data()['event_id']

        # Everything after this will eventually be done in a Kafka consumer.
        return process_event(event_manager, project,
                             key, remote_addr, helper, attachments)


class StoreSchemaView(BaseView):
    def get(self, request, **kwargs):
        return HttpResponse(json.dumps(schemas.EVENT_SCHEMA), content_type='application/json')


class SecurityReportView(StoreView):
    auth_helper_cls = SecurityAuthHelper
    content_types = (
        'application/csp-report',
        'application/json',
        'application/expect-ct-report',
        'application/expect-ct-report+json',
        'application/expect-staple-report',
    )

    def _dispatch(self, request, helper, project_id=None, origin=None, *args, **kwargs):
        # A CSP report is sent as a POST request with no Origin or Referer
        # header. What we're left with is a 'document-uri' key which is
        # inside of the JSON body of the request. This 'document-uri' value
        # should be treated as an origin check since it refers to the page
        # that triggered the report. The Content-Type is supposed to be
        # `application/csp-report`, but FireFox sends it as `application/json`.
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])

        if request.META.get('CONTENT_TYPE') not in self.content_types:
            raise APIError('Invalid Content-Type')

        request.user = AnonymousUser()

        project = self._get_project_from_id(project_id)
        helper.context.bind_project(project)

        # This is yanking the auth from the querystring since it's not
        # in the POST body. This means we expect a `sentry_key` and
        # `sentry_version` to be set in querystring
        auth = self.auth_helper_cls.auth_from_request(request)

        key = helper.project_key_from_auth(auth)
        if key.project_id != project.id:
            raise APIError('Two different projects were specified')

        helper.context.bind_auth(auth)

        return super(APIView, self).dispatch(
            request=request, project=project, auth=auth, helper=helper, key=key, **kwargs
        )

    def post(self, request, project, helper, **kwargs):
        json_body = safely_load_json_string(request.body)
        report_type = self.security_report_type(json_body)
        if report_type is None:
            raise APIError('Unrecognized security report type')
        interface = get_interface(report_type)

        try:
            instance = interface.from_raw(json_body)
        except jsonschema.ValidationError as e:
            raise APIError('Invalid security report: %s' % str(e).splitlines()[0])

        # Do origin check based on the `document-uri` key as explained in `_dispatch`.
        origin = instance.get_origin()
        if not is_valid_origin(origin, project):
            if project:
                tsdb.incr(tsdb.models.project_total_received_cors, project.id)
            raise APIForbidden('Invalid origin')

        data = {
            'interface': interface.path,
            'report': instance,
            'release': request.GET.get('sentry_release'),
            'environment': request.GET.get('sentry_environment'),
        }

        response_or_event_id = self.process(
            request, project=project, helper=helper, data=data, **kwargs
        )
        if isinstance(response_or_event_id, HttpResponse):
            return response_or_event_id
        return HttpResponse(content_type='application/javascript', status=201)

    def security_report_type(self, body):
        report_type_for_key = {
            'csp-report': 'csp',
            'expect-ct-report': 'expectct',
            'expect-staple-report': 'expectstaple',
            'known-pins': 'hpkp',
        }
        if isinstance(body, dict):
            for k in report_type_for_key:
                if k in body:
                    return report_type_for_key[k]
        return None

    def pre_normalize(self, data, helper):
        data.process_csp_report()


@cache_control(max_age=3600, public=True)
def robots_txt(request):
    return HttpResponse("User-agent: *\nDisallow: /\n", content_type='text/plain')


@cache_control(max_age=60)
def crossdomain_xml(request, project_id):
    if not project_id.isdigit():
        return HttpResponse(status=404)

    try:
        project = Project.objects.get_from_cache(id=project_id)
    except Project.DoesNotExist:
        return HttpResponse(status=404)

    origin_list = get_origins(project)
    response = render_to_response(
        'sentry/crossdomain.xml', {'origin_list': origin_list})
    response['Content-Type'] = 'application/xml'

    return response
