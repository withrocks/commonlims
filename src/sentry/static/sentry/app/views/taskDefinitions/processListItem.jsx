import {Flex} from 'grid-emotion';
import PropTypes from 'prop-types';
import React from 'react';
import styled from 'react-emotion';
import {PanelBody} from 'app/components/panels';
import TaskListItem from 'app/views/taskDefinitions/taskListItem';

class ProcessListItem extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showTasks: true,
    };
    this.layout = {
      flexWidth: 300,
      flexMargin: 2,
    };
  }

  toggleTasks() {
    this.setState({
      showTasks: !this.state.showTasks,
    });
  }

  renderTasks() {
    const {tasks} = this.props;
    return tasks.map((task, i) => {
      const {count, name, taskDefinitionKey, processDefinitionKey} = task;
      return (
        <TaskListItem
          name={name}
          count={count}
          taskDefinitionKey={taskDefinitionKey}
          processDefinitionKey={processDefinitionKey}
          task={task}
          selectTaskDefinition={this.props.selectTaskDefinition}
          layout={this.layout}
          key={i}
        />
      );
    });
  }

  render() {
    const {processDefinitionName, processDefinitionKey, count} = this.props;
    const {showTasks} = this.state;
    const taskListClass = showTasks ? '' : 'hidden';
    const samplesLabelText = count === 1 ? 'sample' : 'samples';
    const {flexWidth, flexMargin} = this.layout;

    return (
      <ProcessListItemContainer>
        <Sticky
          onClick={this.toggleTasks.bind(this)}
          className="process-list-item-header"
        >
          <StyledFlex py={1} px={0} align="center">
            <Flex flex="1">
              <Flex w={flexWidth} mx={flexMargin} justify="flex-start">
                {processDefinitionName || processDefinitionKey}
              </Flex>
            </Flex>
            <Flex w={flexWidth} mx={flexMargin} justify="flex-start">
              {count} {samplesLabelText}
            </Flex>
            <Flex w={flexWidth} mx={flexMargin} justify="flex-end" />
          </StyledFlex>
        </Sticky>
        <PanelBody className={taskListClass}>{this.renderTasks()}</PanelBody>
      </ProcessListItemContainer>
    );
  }
}

ProcessListItem.propTypes = {
  processDefinitionKey: PropTypes.string.isRequired,
  processDefinitionName: PropTypes.string,
  count: PropTypes.number.isRequired,
  selectTaskDefinition: PropTypes.func.isRequired,
  tasks: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string.isRequired,
      count: PropTypes.number.isRequired,
      taskDefinitionKey: PropTypes.string.isRequired,
    })
  ),
};

ProcessListItem.displayName = 'ProcessListItem';

const Sticky = styled.div`
  position: sticky;
  z-index: ${(p) => p.theme.zIndex.header};
  top: -1px;
`;

const StyledFlex = styled(Flex)`
  align-items: center;
  background: ${(p) => p.theme.offWhite};
  border-bottom: 1px solid ${(p) => p.theme.borderDark};
  border-radius: ${(p) => p.theme.borderRadius} ${(p) => p.theme.borderRadius} 0 0;
  margin-bottom: -1px;
`;

const ProcessListItemContainer = styled.div`
  border-bottom: 1px solid ${(p) => p.theme.borderDark};
`;

export default ProcessListItem;
