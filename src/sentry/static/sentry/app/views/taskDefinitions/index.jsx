import ClimsTypes from 'app/climsTypes';
import React from 'react';
import withOrganization from 'app/utils/withOrganization';
import TaskDefinitions from 'app/views/taskDefinitions/taskDefinitions';
import {connect} from 'react-redux';
import {mapTaskDefinitionDispatchToProps} from 'app/redux/actions/taskDefinition';

class TaskDefinitionsContainer extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    const {visibleIds, byIds} = this.props;
    const taskDefinitions = visibleIds.map((id) => byIds[id]);

    return <TaskDefinitions taskDefinitions={taskDefinitions} {...this.props} />;
  }
}

TaskDefinitionsContainer.propTypes = {
  ...ClimsTypes.List,
};

const mapStateToProps = (state) => {
  return {
    task: state.task,
    taskDefinition: state.taskDefinition,
    byIds: state.taskDefinition.byIds,
    visibleIds: state.taskDefinition.listViewState.visibleIds,
    workBatch: state.workBatch,
  };
};

export default withOrganization(
  connect(mapStateToProps, mapTaskDefinitionDispatchToProps)(TaskDefinitionsContainer)
);
