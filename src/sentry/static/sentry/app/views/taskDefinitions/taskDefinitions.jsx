import PropTypes from 'prop-types';
import React from 'react';
import {t} from 'app/locale';
import {Panel, PanelBody} from 'app/components/panels';
import ProcessListItem from 'app/views/taskDefinitions/processListItem';
import LoadingError from 'app/components/loadingError';
import LoadingIndicator from 'app/components/loadingIndicator';
import {groupBy, sum} from 'lodash';
import ClimsTypes from 'app/climsTypes';
import {taskDefinitionActions} from 'app/redux/actions/taskDefinition';

export class TaskDefinitions extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  renderBody() {
    const {
      taskDefinitions,
      tasksLoading,
      errorMessage,
      getTaskDefinitionList,
    } = this.props;

    let body;
    if (tasksLoading) {
      body = this.renderLoading();
    } else if (errorMessage) {
      body = (
        <LoadingError
          message={errorMessage}
          onRetry={() => getTaskDefinitionList(this.props.organization)}
        />
      );
    } else if (taskDefinitions.length > 0) {
      body = this.renderProcesses();
    } else {
      body = this.renderEmpty();
    }
    return body;
  }

  groupTasksByProcess(taskDefinitions) {
    const ret = [];
    const grouped = groupBy(taskDefinitions, (x) => x.processDefinitionKey);
    for (const [processDefinitionKey, tasks] of Object.entries(grouped)) {
      const entry = {
        tasks,
        count: sum(tasks.map((x) => x.count)),
        processDefinitionKey,
        processDefinitionName: tasks[0].processDefinitionName,
      };
      ret.push(entry);
    }
    return ret;
  }

  renderProcesses() {
    const {taskDefinitions} = this.props;
    const taskDefinitionsGroupedByProcess = this.groupTasksByProcess(taskDefinitions);

    const items = taskDefinitionsGroupedByProcess.map((p, i) => {
      return (
        <ProcessListItem
          {...p}
          key={i}
          selectTaskDefinition={(taskDefinition) =>
            this.onTaskSelected.bind(this)(taskDefinition)
          }
        />
      );
    });

    return <PanelBody className="ref-group-list">{items}</PanelBody>;
  }

  onTaskSelected(task) {
    this.props.selectTaskDefinition(task);
  }

  renderLoading() {
    return <LoadingIndicator />;
  }

  renderEmpty() {
    const message = t('Sorry, no tasks match your filters.');

    return (
      <div className="empty-stream" style={{border: 0}}>
        <p>
          <span className="icon icon-exclamation" /> {message}
        </p>
      </div>
    );
  }

  render() {
    return (
      <Panel>
        <PanelBody>{this.renderBody()}</PanelBody>
      </Panel>
    );
  }
}

TaskDefinitions.propTypes = {
  getTaskDefinitionList: PropTypes.func,
  tasks: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string.isRequired,
      count: PropTypes.number.isRequired,
      taskDefinitionKey: PropTypes.string.isRequired,
      processDefinitionKey: PropTypes.string.isRequired,
      processDefinitionName: PropTypes.string,
    })
  ),
  tasksLoading: PropTypes.bool.isRequired,
  errorMessage: PropTypes.string.isRequired,
  selectTaskDefinition: PropTypes.func.isRequired,
  taskDefinitions: PropTypes.arrayOf(ClimsTypes.TaskDefinition).isRequired,
  organization: ClimsTypes.Organization.isRequired,
};
TaskDefinitions.displayName = 'TaskDefinitions';

export default TaskDefinitions;
