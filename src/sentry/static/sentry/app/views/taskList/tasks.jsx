import PropTypes from 'prop-types';
import React from 'react';
import {connect} from 'react-redux';
import {t} from 'app/locale';
import {tasksGet} from 'app/redux/actions/task';
import {Panel, PanelBody} from 'app/components/panels';
import ProcessListItem from 'app/components/task/processListItem';
import LoadingError from 'app/components/loadingError';
import LoadingIndicator from 'app/components/loadingIndicator';

export class Tasks extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  componentDidMount() {
    const {getTasks} = this.props;
    getTasks();
  }

  renderBody() {
    const {tasks, loading, errorMessage, getTasks} = this.props;

    let body;
    if (loading) {
      body = this.renderLoading();
    } else if (errorMessage) {
      body = <LoadingError message={errorMessage} onRetry={getTasks} />;
    } else if (tasks.length > 0) {
      body = this.renderProcesses();
    } else {
      body = this.renderEmpty();
    }
    return body;
  }

  groupTasksByProcess(tasks) {
    const processes = tasks.reduce((r, task) => {
      const {
        count,
        name,
        processDefinitionKey,
        processDefinitionName,
        taskDefinitionKey,
      } = task;

      const prunedTask = {count, name, taskDefinitionKey};

      r[processDefinitionKey] = r[processDefinitionKey]
        ? {...r[processDefinitionKey]}
        : {
            tasks: [],
            count: 0,
            processDefinitionKey,
            processDefinitionName,
          };
      r[processDefinitionKey].count += count;
      r[processDefinitionKey].tasks.push(prunedTask);

      return r;
    }, {});

    const arrProcesses = [];
    for (const key in processes) {
      arrProcesses.push(processes[key]);
    }

    return arrProcesses;
  }

  renderProcesses() {
    const {tasks} = this.props;
    const processes = this.groupTasksByProcess(tasks);

    const items = processes.map((p, i) => {
      return <ProcessListItem {...p} key={i} />;
    });

    return <PanelBody className="ref-group-list">{items}</PanelBody>;
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

Tasks.propTypes = {
  getTasks: PropTypes.func,
  tasks: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string.isRequired,
      count: PropTypes.number.isRequired,
      taskDefinitionKey: PropTypes.string.isRequired,
      processDefinitionKey: PropTypes.string.isRequired,
      processDefinitionName: PropTypes.string,
    })
  ),
  loading: PropTypes.bool,
  errorMessage: PropTypes.string,
};
Tasks.displayName = 'Tasks';

const mapStateToProps = (state) => state.task;

const mapDispatchToProps = (dispatch) => ({
  getTasks: () => dispatch(tasksGet()),
});

export default connect(mapStateToProps, mapDispatchToProps)(Tasks);
