import React from 'react';
import PropTypes from 'prop-types';
import SentryTypes from 'app/sentryTypes';

import withEnvironment from 'app/utils/withEnvironment';
import {analytics} from 'app/utils/analytics';

import UserTaskDetails from '../shared/userTaskDetails';

class UserTaskDetailsContainer extends React.Component {
  static propTypes = {
    setProjectNavSection: PropTypes.func,
    environment: SentryTypes.Environment,
  };

  static contextTypes = {
    organization: SentryTypes.Organization,
    project: SentryTypes.Project,
  };

  componentDidMount() {
    this.props.setProjectNavSection('tasks');
    analytics('issue_page.viewed', {
      group_id: parseInt(this.props.params.groupId, 10),
      org_id: parseInt(this.context.organization.id, 10),
      project_id: parseInt(this.context.project.id, 10),
    });
  }

  render() {
    // eslint-disable-next-line no-unused-vars
    const {setProjectNavSection, ...props} = this.props;
    return <UserTaskDetails project={this.context.project} {...props} />;
  }
}

export default withEnvironment(UserTaskDetailsContainer);
