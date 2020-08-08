import {Flex, Box} from 'grid-emotion';
import React from 'react';
import createReactClass from 'create-react-class';
import styled from 'react-emotion';

import SelectedGroupStore from 'app/stores/selectedGroupStore';

// TODO: use regular react class

const ListActionBar = createReactClass({
  displayName: 'ListActionBar',

  getInitialState() {
    return {
      datePickerActive: false,
      anySelected: false,
      multiSelected: false,
      pageSelected: false,
      allInQuerySelected: false,
      selectedIds: new Set(),
    };
  },

  selectAll() {
    this.setState({
      allInQuerySelected: true,
    });
  },

  deselectAll() {
    SelectedGroupStore.deselectAll();
    this.setState({allInQuerySelected: false});
  },

  shouldConfirm(action) {
    return true; // TODO: only if required
  },

  render() {
    return (
      <div>
        <StyledFlex py={1}>
          <ActionSet w={[8 / 12, 8 / 12, 6 / 12]} mx={1} flex="1">
            {this.props.children}
          </ActionSet>
        </StyledFlex>
      </div>
    );
  },
});

const StyledFlex = styled(Flex)`
  align-items: center;
  background: ${(p) => p.theme.offWhite};
  border-radius: ${(p) => p.theme.borderRadius} ${(p) => p.theme.borderRadius} 0 0;
  margin-bottom: -1px;
`;

const ActionSet = styled(Box)`
  display: flex;

  .btn-group {
    margin-right: 6px;
  }
`;

export default ListActionBar;
