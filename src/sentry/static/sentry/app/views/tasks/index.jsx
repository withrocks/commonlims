import PropTypes from 'prop-types';
import React from 'react';
import withOrganization from 'app/utils/withOrganization';
import Tasks from 'app/views/tasks/tasks';
import {connect} from 'react-redux';
import {taskActions} from 'app/redux/actions/task';
import {workBatchActions} from 'app/redux/actions/workBatch';
import {taskDefinitionActions} from 'app/redux/actions/taskDefinition';
import ClimsTypes from 'app/climsTypes';

class TasksContainer extends React.Component {
  constructor(props) {
    super(props);
  }

  componentDidMount() {
    const {processKey, taskKey} = this.props.routeParams;

    // If we don't have the task definition, we load that too:
    // TODO: check if we have it first
    this.props.getTaskDefinition(processKey, taskKey);
    this.props.getTasks(this.props.organization, processKey, taskKey);
  }

  render() {
    const taskDefinition = this.props.detailsId
      ? this.props.taskDefinitionsByIds[this.props.detailsId]
      : null;
    return <Tasks {...this.props} taskDefinition={taskDefinition} />;
  }
}

// TODO: get from redux state (new reducer)
function getColumns() {
  return [
    {
      Header: 'Sample name',
      id: 'name',
      // TODO: javascriptify tracked_object => trackedObject
      accessor: (task) => task.tracked_object.name,
    },
    {
      Header: 'Container',
      id: 'container',
      accessor: (task) =>
        task.tracked_object.location
          ? task.tracked_object.location.container.name
          : '<No location>',
    },
  ];
}

TasksContainer.propTypes = {
  ...ClimsTypes.List,
  organization: ClimsTypes.Organization.isRequired,

  taskDefinitionsByIds: PropTypes.array.isRequired,
  detailsId: PropTypes.string.isRequired,

  getTasks: PropTypes.func.isRequired,
  getTaskDefinition: PropTypes.func.isRequired,
  routeParams: PropTypes.shape({
    processKey: PropTypes.string.isRequired,
    taskKey: PropTypes.string.isRequired,
  }).isRequired,
};

const mapStateToProps = (state) => {
  return {
    // task
    listViewState: state.task.listViewState,
    byIds: state.task.byIds,
    loading: state.task.loading,

    taskDefinition: state.task.taskDefinition,
    workBatch: state.workBatch,

    // taskDefinition:
    detailsId: state.taskDefinition.detailsId,
    taskDefinitionsByIds: state.taskDefinition.byIds,

    // workBatch:
    creatingWorkBatch: state.workBatch.creating,

    // pending:
    columns: getColumns(),
  };
};

const mapDispatchToProps = (dispatch) => ({
  getTasks: (org, processDefinitionKey, taskDefinitionKey) =>
    dispatch(
      taskActions.getList(org, null, null, null, {
        processDefinitionKey,
        taskDefinitionKey,
      })
    ),
  toggleSingle: (id) => dispatch(taskActions.select(id)),
  toggleAll: () => dispatch(taskActions.selectPage()),
  createWorkBatch: (org, tasks, redirect) =>
    dispatch(workBatchActions.create(org, tasks, redirect)),
  getTaskDefinition: (process, task) =>
    dispatch(taskDefinitionActions.get(process + '/' + task)),
});

export default withOrganization(
  connect(mapStateToProps, mapDispatchToProps)(TasksContainer)
);
