import PropTypes from 'prop-types';
import React from 'react';
import {connect} from 'react-redux';
import DocumentTitle from 'react-document-title';

import LoadingIndicator from 'app/components/loadingIndicator';
import ClimsTypes from 'app/climsTypes';
import withOrganization from 'app/utils/withOrganization';
import {
  getWorkBatchDetails,
  createWorkBatchTransition,
} from 'app/redux/actions/workBatchDetails';

import WorkBatchDetailsFields from 'app/views/workBatchDetails/shared/workBatchFields';
import WorkBatchDetailsFiles from 'app/views/workBatchDetails/shared/workBatchFiles';
import WorkBatchDetailsActivity from 'app/views/workBatchDetails/shared/workBatchActivity';
import SampleTransitioner from 'app/components/sampleTransitioner/sampleTransitioner';

import WorkBatchHeader from './header';
import {SampleLocation} from 'app/components/sampleTransitioner/sampleLocation';
import {Sample} from 'app/components/sampleTransitioner/sample';

class WorkBatchDetails extends React.Component {
  constructor(props) {
    super(props);
    this.state = {selectedTab: props.workBatch.tabs[0]};
  }

  getTitle() {
    return this.props.workBatch.name;
  }

  renderTodoItems() {
    const ret = this.props.workBatch.subtasks.map((x) => {
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
    if (this.state.selectedTab.type == 'Transition') {
      return <SampleTransitioner workBatch={this.props.workBatch} />;
    } else if (this.state.selectedTab.type == 'Files') {
      return <WorkBatchDetailsFiles workBatch={this.props.workBatch} />;
    } else if (this.state.selectedTab.type == 'Comments') {
      return <WorkBatchDetailsActivity workBatch={this.props.workBatch} />;
    }
  }

  render() {
    return (
      <DocumentTitle title={this.getTitle()}>
        <div>
          <WorkBatchHeader
            selectedTab={this.state.selectedTab}
            workBatch={this.props.workBatch}
            tabSelected={(tab) => this.setState({selectedTab: tab})}
          />
          <div className="work-batch-details-container">
            <div className="primary">{this.renderTabComponent()}</div>
          </div>
        </div>
      </DocumentTitle>
    );
  }
}

WorkBatchDetails.propTypes = {
  workBatch: ClimsTypes.WorkBatch.isRequired,
};

// TODO: Move this further down, to where we actually need this
function mapSubstanceToJsType(substance) {
  const {containerId, row, col} = substance.location;
  const location = new SampleLocation(containerId, row, col); // TODO: rename sample=> substance
  return new Sample(substance.id, substance.name, location);
}

// Locally, we work with an object that's a bit smarter than the json returned (implements
// equality checks etc.)
function mapWorkbatchToJsType(workBatch) {
  workBatch.source.substances = workBatch.source.substances.map((s) =>
    mapSubstanceToJsType(s)
  );
  workBatch.target.substances = workBatch.target.substances.map((s) =>
    mapSubstanceToJsType(s)
  );
  return workBatch;
}

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
  //

  componentDidMount() {
    this.props.getWorkBatchDetails(0, 0); // TODO
  }

  render() {
    if (this.props.loading || !this.props.workBatch) {
      return <LoadingIndicator />;
    }
    return (
      <WorkBatchDetails
        workBatch={mapWorkbatchToJsType(this.props.workBatch)}
        createWorkBatchTransition={this.props.createWorkBatchTransition}
      />
    );
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
  createWorkBatchTransition: PropTypes.func.isRequired,
};

const mapStateToProps = (state) => state.workBatchDetails;

const mapDispatchToProps = (dispatch) => ({
  getWorkBatchDetails: (org, id) => dispatch(getWorkBatchDetails(org, id)),
  createWorkBatchTransition: (workBatch, transition) =>
    dispatch(createWorkBatchTransition(workBatch, transition)),
});

export default withOrganization(
  connect(mapStateToProps, mapDispatchToProps)(WorkBatchDetailsContainer)
);
