import PropTypes from 'prop-types';
import React from 'react';
import createReactClass from 'create-react-class';

import {t, tct, tn} from 'app/locale';
import Avatar from 'app/components/avatar';
import CommitLink from 'app/components/commitLink';
import ConfigStore from 'app/stores/configStore';
import Duration from 'app/components/duration';
import ErrorBoundary from 'app/components/errorBoundary';
import MemberListStore from 'app/stores/memberListStore';
import NoteContainer from 'app/components/activity/noteContainer';
import NoteInput from 'app/components/activity/noteInput';
import PullRequestLink from 'app/components/pullRequestLink';
import TeamStore from 'app/stores/teamStore';
import Version from 'app/components/version';

class WorkBatchActivityItem extends React.Component {
  displayName() {
    return 'WorkBatchActivityItem';
  }

  static propTypes = {
    author: PropTypes.node,
    item: PropTypes.object,
    orgId: PropTypes.string,
    projectId: PropTypes.string,
  };

  render() {
    const {author, item, orgId, projectId} = this.props;
    const {data} = item;

    switch (item.type) {
      case 'note':
        return t('%s left a comment', author);
      case 'set_manual_override':
        return t('%s marked "%s" as %s', author, data.subtask, data.status);
      case 'set_resolved':
        return t('%s marked this issue as resolved', author);
      case 'set_resolved_by_age':
        return t('%(author)s marked this issue as resolved due to inactivity', {
          author,
        });
      case 'set_resolved_in_release':
        return data.version
          ? t('%(author)s marked this issue as resolved in %(version)s', {
              author,
              version: (
                <Version version={data.version} orgId={orgId} projectId={projectId} />
              ),
            })
          : t('%s marked this issue as resolved in the upcoming release', author);
      case 'set_resolved_in_commit':
        return t('%(author)s marked this issue as fixed in %(version)s', {
          author,
          version: (
            <CommitLink
              inline={true}
              commitId={data.commit && data.commit.id}
              repository={data.commit && data.commit.repository}
            />
          ),
        });
      case 'set_resolved_in_pull_request':
        return t('%(author)s marked this issue as fixed in %(version)s', {
          author,
          version: (
            <PullRequestLink
              inline={true}
              pullRequest={data.pullRequest}
              repository={data.pullRequest && data.pullRequest.repository}
            />
          ),
        });
      case 'set_unresolved':
        return t('%s marked this issue as unresolved', author);
      case 'set_ignored':
        if (data.ignoreDuration) {
          return t('%(author)s ignored this issue for %(duration)s', {
            author,
            duration: <Duration seconds={data.ignoreDuration * 60} />,
          });
        } else if (data.ignoreCount && data.ignoreWindow) {
          return tct(
            '[author] ignored this issue until it happens [count] time(s) in [duration]',
            {
              author,
              count: data.ignoreCount,
              duration: <Duration seconds={data.ignoreWindow * 60} />,
            }
          );
        } else if (data.ignoreCount) {
          return tct('[author] ignored this issue until it happens [count] time(s)', {
            author,
            count: data.ignoreCount,
          });
        } else if (data.ignoreUserCount && data.ignoreUserWindow) {
          return tct(
            '[author] ignored this issue until it affects [count] user(s) in [duration]',
            {
              author,
              count: data.ignoreUserCount,
              duration: <Duration seconds={data.ignoreUserWindow * 60} />,
            }
          );
        } else if (data.ignoreUserCount) {
          return tct('[author] ignored this issue until it affects [count] user(s)', {
            author,
            count: data.ignoreUserCount,
          });
        }
        return t('%s ignored this issue', author);
      case 'set_public':
        return t('%s made this issue public', author);
      case 'set_private':
        return t('%s made this issue private', author);
      case 'set_regression':
        return data.version
          ? t('%(author)s marked this issue as a regression in %(version)s', {
              author,
              version: (
                <Version version={data.version} orgId={orgId} projectId={projectId} />
              ),
            })
          : t('%s marked this issue as a regression', author);
      case 'create_issue':
        return t('%(author)s created an issue on %(provider)s titled %(title)s', {
          author,
          provider: data.provider,
          title: <a href={data.location}>{data.title}</a>,
        });
      case 'unmerge_source':
        return tn(
          '%2$s migrated %1$s fingerprint to %3$s',
          '%2$s migrated %1$s fingerprints to %3$s',
          data.fingerprints.length,
          author,
          data.destination ? (
            <a href={`/${orgId}/${projectId}/issues/${data.destination.id}`}>
              {data.destination.shortId}
            </a>
          ) : (
            t('a group')
          )
        );
      case 'unmerge_destination':
        return tn(
          '%2$s migrated %1$s fingerprint from %3$s',
          '%2$s migrated %1$s fingerprints from %3$s',
          data.fingerprints.length,
          author,
          data.source ? (
            <a href={`/${orgId}/${projectId}/issues/${data.source.id}`}>
              {data.source.shortId}
            </a>
          ) : (
            t('a group')
          )
        );
      case 'first_seen':
        return t('%s first saw this issue', author);
      case 'assigned':
        let assignee;

        if (data.assigneeType == 'team') {
          const team = TeamStore.getById(data.assignee);
          assignee = team ? team.slug : '<unknown-team>';

          return t('%(author)s assigned this issue to #%(assignee)s', {
            author,
            assignee,
          });
        }

        if (item.user && data.assignee === item.user.id) {
          return t('%s assigned this issue to themselves', author);
        } else {
          assignee = MemberListStore.getById(data.assignee);
          if (assignee && assignee.email) {
            return t('%(author)s assigned this issue to %(assignee)s', {
              author,
              assignee: assignee.email,
            });
          } else {
            return t('%s assigned this issue to an unknown user', author);
          }
        }
      case 'unassigned':
        return t('%s unassigned this issue', author);
      case 'merge':
        return tn(
          '%2$s merged %1$s issue into this issue',
          '%2$s merged %1$s issues into this issue',
          data.issues.length,
          author
        );
      default:
        return ''; // should never hit (?)
    }
  }
}

const WorkBatchActivity = createReactClass({
  displayName: 'WorkBatchActivity',

  // TODO(dcramer): only re-render on group/activity change
  propTypes: {
    workBatch: PropTypes.object,
  },

  render() {
    const workBatch = this.props.workBatch;
    const me = ConfigStore.get('user');
    const memberList = MemberListStore.getAll();

    const orgId = 'snpseq'; // TODO

    const children = workBatch.activity.map((item, itemIdx) => {
      const authorName = item.user ? item.user.name : 'Sentry';

      if (item.type === 'note') {
        return (
          <NoteContainer
            group={workBatch}
            item={item}
            key={'note' + itemIdx}
            author={{
              name: authorName,
              avatar: <Avatar user={item.user} size={38} />,
            }}
            onDelete={this.onNoteDelete}
            sessionUser={me}
            memberList={memberList}
          />
        );
      } else {
        const avatar = item.user ? (
          <Avatar user={item.user} size={18} className="activity-avatar" />
        ) : (
          <div className="activity-avatar avatar sentry">
            <span className="icon-sentry-logo" />
          </div>
        );

        const author = {
          name: authorName,
          avatar,
        };

        return (
          <li className="activity-item" key={item.id}>
            <a name={'event_' + item.id} />
            {/*<TimeSince date={item.dateCreated} />*/}
            <div className="activity-item-content">
              <ErrorBoundary mini>
                <WorkBatchActivityItem
                  author={
                    <span key="author">
                      {avatar}
                      <span className="activity-author">{author.name}</span>
                    </span>
                  }
                  item={item}
                  orgId={orgId}
                />
              </ErrorBoundary>
            </div>
          </li>
        );
      }
    });

    return (
      <div className="row">
        <div className="activity-container">
          <ul className="activity">
            <li className="activity-note" key="activity-note">
              <Avatar user={me} size={38} />
              <div className="activity-bubble">
                <NoteInput group={workBatch} memberList={memberList} sessionUser={me} />
              </div>
            </li>
            {children}
          </ul>
        </div>
      </div>
    );
  },
});

export default WorkBatchActivity;
