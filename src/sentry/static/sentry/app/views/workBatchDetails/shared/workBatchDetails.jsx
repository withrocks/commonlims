import PropTypes from 'prop-types';
import React from 'react';
import {connect} from 'react-redux';
import DocumentTitle from 'react-document-title';

import LoadingIndicator from 'app/components/loadingIndicator';
import ClimsTypes from 'app/climsTypes';
import withOrganization from 'app/utils/withOrganization';
import {getWorkBatchDetails} from 'app/redux/actions/workBatchDetails';

import WorkBatchDetailsFields from 'app/views/workBatchDetails/shared/workBatchFields';
import WorkBatchDetailsFiles from 'app/views/workBatchDetails/shared/workBatchFiles';
import WorkBatchDetailsActivity from 'app/views/workBatchDetails/shared/workBatchActivity';
import SampleTransitioner from 'app/components/sampleTransitioner/sampleTransitioner';

import WorkBatchHeader from './header';

class WorkBatchDetails extends React.Component {
  getTitle() {
    return this.props.workBatch.name;
  }

  renderTodoItems() {
    const ret = this.props.workBatch.subtasks.map(x => {
      return (
        <TodoItem
          handleManualClick={() => this.subtaskManualClick(x)}
          handleTitleClick={() => this.subtaskTitleClick(x)}
          description={x.description}
          key={x.description}
          status={x.status}
          manualOverride={x.manualOverride}
        />
      );
    });
    return ret;
  }

  renderTabComponent() {
    const tab = {};
    // TODO: Quick hack. This will be revisited in a commit that's soon-to-come
    tab.id = 'samples';
    if (tab.id == 'samples') {
      return <SampleTransitioner workBatch={this.props.workBatch} />;
    } else if (tab.id == 'details') {
      return <WorkBatchDetailsFields workBatch={this.state.workBatch} />;
    } else if (tab.id == 'files') {
      return <WorkBatchDetailsFiles workBatch={this.state.workBatch} />;
    } else if (tab.id == 'activity') {
      return <WorkBatchDetailsActivity workBatch={this.state.workBatch} />;
    } else {
      throw new Error('Unexpected tab id ' + tab.id);
    }
  }

  activeTab() {
    for (const tab of this.workBatch.tabs) {
      if (tab.active) {
        return tab;
      }
    }
    throw new Error('No active tab found');
  }

  render() {
    return (
      <DocumentTitle title={this.getTitle()}>
        <div>
          <WorkBatchHeader workBatch={this.props.workBatch} />
          <div className="work-batch-details-container">
            <div className="primary">{this.renderTabComponent()}</div>
            <div className="secondary">
              <div className="work-batch-todo-container">
                <h6>Task list</h6>
                {this.renderTodoItems()}
              </div>
            </div>
          </div>
        </div>
      </DocumentTitle>
    );
  }
}

WorkBatchDetails.propTypes = {
  workBatch: ClimsTypes.WorkBatch.isRequired,
};

class WorkBatchDetailsContainer extends React.Component {
  // TODO: connect to redux
  //

  // subtaskManualClick(subtask) {
  //   WorkBatchStore.setSubtaskManualOverride(
  //     subtask.view,
  //     !subtask.manualOverride,
  //   );
  // },

  // subtaskTitleClick(subtask) {
  //   WorkBatchStore.activateView(subtask.view);
  // },
  //
  componentDidMount() {
    this.props.getWorkBatchDetails(0, 0); // TODO
  }

  render() {
    if (this.props.loading || !this.props.workBatch) {
      return <LoadingIndicator />;
    }

    return <WorkBatchDetails {...this.props} />;
  }
}

const TodoItem = (props) => {
  let icon = 'icon-checkmark';
  if (props.status === 'error') {
    icon = 'icon-ban';
  }

  let status = props.status;
  if (props.manualOverride) {
    status = 'manual';
  }

  return (
    <div className="todo-item">
      <a className="btn btn-default btn-sm" onClick={props.handleManualClick}>
        <span className={`${icon} ${status}`} />
      </a>
      <span className="description">
        <a onClick={props.handleTitleClick}>{props.description}</a>
      </span>
    </div>
  );
};

TodoItem.propTypes = {
  status: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  handleTitleClick: PropTypes.func.isRequired,
  handleManualClick: PropTypes.func.isRequired,
  manualOverride: PropTypes.bool.isRequired,
};

WorkBatchDetailsContainer.propTypes = {
  workBatch: ClimsTypes.WorkBatch.isRequired,
  loading: PropTypes.bool.isRequired,
  getWorkBatchDetails: PropTypes.func.isRequired,
};

const mapStateToProps = state => state.workBatchDetails;

const mapDispatchToProps = dispatch => ({
  getWorkBatchDetails: (org, id) => dispatch(getWorkBatchDetails(org, id)),
});

export default withOrganization(
  connect(mapStateToProps, mapDispatchToProps)(WorkBatchDetailsContainer)
);
