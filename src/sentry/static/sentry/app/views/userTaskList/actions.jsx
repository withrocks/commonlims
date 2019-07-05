// NOTE: this is a WIP copy of stream/actions.jsx.
// We are porting only relevant functionality bit by bit.
import Checkbox from 'app/components/checkbox';
import {Flex, Box} from 'grid-emotion';
import styled from 'react-emotion';
import PropTypes from 'prop-types';
import React from 'react';

class UserTaskListActions extends React.Component {
  render() {
    let {toggleSelectAll, allSelected} = this.props;

    return (
      <Sticky>
        <StyledFlex py={1}>
          <ActionsCheckbox pl={2}>
            <Checkbox onChange={toggleSelectAll} selected={allSelected} />
          </ActionsCheckbox>
        </StyledFlex>
      </Sticky>
    );
  }
}

const Sticky = styled.div`
  position: sticky;
  z-index: ${p => p.theme.zIndex.header};
  top: -1px;
`;

const StyledFlex = styled(Flex)`
  align-items: center;
  background: ${p => p.theme.offWhite};
  border-bottom: 1px solid ${p => p.theme.borderDark};
  border-radius: ${p => p.theme.borderRadius} ${p => p.theme.borderRadius} 0 0;
  margin-bottom: -1px;
`;

const ActionsCheckbox = styled(Box)`
  & input[type='checkbox'] {
    margin: 0;
    display: block;
  }
`;

UserTaskListActions.propTypes = {
  toggleSelectAll: PropTypes.func,
  allSelected: PropTypes.bool,
};

UserTaskListActions.displayName = 'UserTaskListActions';

export default UserTaskListActions;
