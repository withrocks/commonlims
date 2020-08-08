import {Flex, Box} from 'grid-emotion';
import PropTypes from 'prop-types';
import React from 'react';
import {PanelItem} from 'app/components/panels';
import {Link} from 'react-router';

class TaskListItem extends React.Component {
  render() {
    const {name, count, layout} = this.props;
    const {flexMargin, flexWidth} = layout;
    return (
      <PanelItem py={1} px={0} align="center">
        <Flex flex="1">
          <Box w={flexWidth} mx={flexMargin} justify="flex-start">
            <Link
              to={`/lab/tasks/${this.props.processDefinitionKey}/${this.props.taskDefinitionKey}/`}
            >
              {name}
            </Link>
          </Box>
        </Flex>
        <Flex w={flexWidth} mx={flexMargin} justify="flex-start">
          <span className="task-list-item-sample-count">{count}</span>
        </Flex>
        <Flex w={flexWidth} mx={flexMargin} justify="flex-end" />
      </PanelItem>
    );
  }
}

TaskListItem.propTypes = {
  name: PropTypes.string.isRequired,
  count: PropTypes.number.isRequired,
  processDefinitionKey: PropTypes.string.isRequired,
  taskDefinitionKey: PropTypes.string.isRequired,
  layout: PropTypes.shape({
    flexWidth: PropTypes.number,
    flexMargin: PropTypes.number,
  }),
};

TaskListItem.defaultProps = {
  layout: {
    flexWidth: 300,
    flexMargin: 2,
  },
};

TaskListItem.displayName = 'TaskListItem';

export default TaskListItem;
