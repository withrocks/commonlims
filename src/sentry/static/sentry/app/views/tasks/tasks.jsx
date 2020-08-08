import React from 'react';
import {t} from 'app/locale';
import PropTypes from 'prop-types';
import ListView from 'app/components/listView';

import BackButton from 'app/components/backButton';
import ListActionBar from 'app/components/listActionBar';
import LoadingIndicator from 'app/components/loadingIndicator';
import ClimsTypes from 'app/climsTypes';

export default class Tasks extends React.Component {
  listActionBar() {
    const len = this.props.listViewState.selectedIds.size;
    return (
      <ListActionBar>
        <div className="btn-group">
          <button
            className="btn btn-sm btn-default"
            disabled={len == 0 || this.props.creatingWorkBatch}
            onClick={() =>
              this.props.createWorkBatch(
                this.props.organization,
                this.props.listViewState.selectedIds,
                true
              )}
          >
            {`Start work (${len})`}
          </button>
        </div>
      </ListActionBar>
    );
  }

  render() {
    if (this.props.loading) {
      return <LoadingIndicator />;
    }

    const actionBar = this.listActionBar();
    const taskName = this.props.taskDefinition ? this.props.taskDefinition.name : '';
    const processName = this.props.taskDefinition
      ? this.props.taskDefinition.processDefinitionName
      : '';

    return (
      <div>
        <h4>Step: {taskName}</h4>
        <h6>{processName}</h6>
        <BackButton to={`/${this.props.organization.slug}/tasks/`}>
          {t('Back to Available Work')}
        </BackButton>
        <ListView
          orgId={this.props.organization.id}
          columns={this.props.columns}
          dataById={this.props.byIds}
          visibleIds={this.props.listViewState.visibleIds}
          selectedIds={this.props.listViewState.selectedIds}
          allVisibleSelected={this.props.listViewState.allVisibleSelected}
          loading={this.props.substancesLoading}
          canSelect
          listActionBar={actionBar}
          toggleSingle={this.props.toggleSingle}
          toggleAll={this.props.toggleAll}
        />
      </div>
    );
  }
}

// TODO: use well defined prop types
Tasks.propTypes = {
  ...ClimsTypes.List,

  organization: PropTypes.exact({
    id: PropTypes.string,
  }),
  columns: PropTypes.array,
  substancesLoading: PropTypes.bool,
  toggleSingle: PropTypes.func,
  toggleAll: PropTypes.func,
  createWorkBatch: PropTypes.func,
  taskDefinition: ClimsTypes.TaskDefinition.isRequired,
};
