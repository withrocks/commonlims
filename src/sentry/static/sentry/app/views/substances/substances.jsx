import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {browserHistory} from 'react-router';
import {
  substanceSearchEntriesGet,
  substanceSearchEntriesToggleSelectAll,
  substanceSearchEntryToggleSelect,
  substanceSearchEntryExpandCollapse,
} from 'app/redux/actions/substanceSearchEntry';
import {t} from 'app/locale';
import ListFilters from 'app/components/listFilters';
import ListView from 'app/components/listView';
import SentryTypes from 'app/sentryTypes';
import ListActionBar from 'app/components/listActionBar';
import Pagination from 'app/components/pagination';
import {showRounded} from 'app/utils/formatters';
import UploadSubstancesButton from 'app/views/substances/uploadSubstancesButton';
import AssignToWorkflowButton from 'app/components/substances/assignToWorkflow';

class Substances extends React.Component {
  constructor(props) {
    super(props);
    this.onImported = this.onImported.bind(this);
    this.onSavedSearchChange = this.onSavedSearchCreate.bind(this);
    this.onGroup = this.onGroup.bind(this);
    this.onSort = this.onSort.bind(this);
    this.onSearch = this.onSearch.bind(this);
    this.toggleAll = this.toggleAll.bind(this);
    this.onCursor = this.onCursor.bind(this);

    let {search, cursor, groupBy} = this.props.substanceSearchEntry;
    const query = this.props.location.query;

    if (query) {
      search = query.search ? query.search : search;
      cursor = query.cursor ? query.cursor : cursor;
      groupBy = query.groupBy ? query.groupBy : groupBy;
    }

    this.onSearch(search, groupBy, cursor);
  }

  onSearch(search, groupBy, cursor) {
    this.props.substanceSearchEntriesGet(search, groupBy, cursor);

    // Add search to history
    const location = this.props.location;
    const query = {
      ...location.query,
      search,
      groupBy,
      cursor,
    };

    browserHistory.push({
      pathname: location.pathname,
      query,
    });
  }

  onCursor(cursor) {
    const {search, groupBy} = this.props.substanceSearchEntry;
    this.onSearch(search, groupBy, cursor);
  }

  onSavedSearchCreate() {
    // TODO: Link with redux instead
  }

  toggleAll() {
    this.props.substanceSearchEntriesToggleSelectAll(null);
  }

  getHeaders() {
    // TODO: This should be returned as a contract from the plugin that is registered for this.
    return [
      {
        Header: 'Sample name',
        id: 'name',
        accessor: (d) => d.name,
        fontstyle: (isGroupHeader) => (isGroupHeader ? 'italic' : 'normal'),
      },
      {
        Header: 'Container',
        id: 'container',
        accessor: (d, isGroupHeader) =>
          isGroupHeader ? null : d.location ? d.location.container.name : '<No location>',
      },
      {
        Header: 'Index',
        id: 'index',
        accessor: (d, isGroupHeader) =>
          isGroupHeader ? null : d.location ? d.location.index : '<No location>',
      },
      {
        Header: 'Volume',
        id: 'volume',
        accessor: (d, isGroupHeader) =>
          isGroupHeader
            ? null
            : d.properties && d.properties.volume
            ? showRounded(d.properties.volume.value)
            : null,
      },
      {
        Header: 'Sample Type',
        id: 'sample_type',
        accessor: (d, isGroupHeader) =>
          isGroupHeader
            ? null
            : d.properties && d.properties.sample_type
            ? d.properties.sample_type.value
            : null,
      },
      {
        Header: 'Priority',
        id: 'priority',
        accessor: (d, isGroupHeader) => (isGroupHeader ? null : d.priority),
      },
      {
        Header: 'Waiting',
        id: 'days_waiting',
        accessor: (d, isGroupHeader) => (isGroupHeader ? null : d.days_waiting),
      },
    ];
  }

  onImported() {
    this.props.substanceSearchEntriesGet();
  }

  onGroup(e) {
    this.setState({groupBy: {value: e}});
    const {search, cursor} = this.props.substanceSearchEntry;
    this.onSearch(search, e, cursor);
  }

  onSort(e) {}

  listActionBar(canAssignToWorkflow, orgId) {
    return (
      <ListActionBar>
        <div className="btn-group">
          <UploadSubstancesButton className="btn btn-sm btn-default" disabled={false}>
            {t('Import samples')}
          </UploadSubstancesButton>
        </div>
        <div className="btn-group">
          <AssignToWorkflowButton
            className="btn btn-sm btn-default"
            disabled={!canAssignToWorkflow}
            organization={this.props.organization}
          >
            {t('Assign to workflow')}
          </AssignToWorkflowButton>
        </div>
      </ListActionBar>
    );
  }

  render() {
    // TODO: Rename css classes to something else than stream
    const groupOptions = [
      {key: 'substance', title: t('Substance')},
      {key: 'container', title: t('Container')},
      {key: 'sample_type', title: t('Sample type')},
    ];
    const {
      groupBy,
      query,
      byIds,
      visibleIds,
      selectedIds,
      loading,
      allVisibleSelected,
    } = this.props.substanceSearchEntry;

    const canAssignToWorkflow = selectedIds.size > 0;
    const actionBar = this.listActionBar(canAssignToWorkflow, this.props.organization.id);

    return (
      <div className="stream-row">
        <div className="stream-content">
          <ListFilters
            access={this.props.access}
            onSavedSearchCreate={this.onSavedSearchCreate}
            searchPlaceholder={t('Search for samples, containers, projects and steps')}
            groupOptions={groupOptions}
            grouping={groupBy}
            onGroup={this.onGroup}
            onSearch={this.onSearch}
            orgId={this.props.organization.id}
            query={query}
          />
          <ListView
            orgId={this.props.organization.id}
            columns={this.getHeaders()}
            dataById={byIds}
            visibleIds={visibleIds}
            selectedIds={selectedIds}
            loading={loading}
            canSelect={true}
            allVisibleSelected={allVisibleSelected}
            toggleAll={this.toggleAll}
            toggleSingle={this.props.substanceSearchEntryToggleSelect}
            listActionBar={actionBar}
            expandCollapse={this.props.substanceSearchEntryExpandCollapse}
          />

          {this.props.substanceSearchEntry.paginationEnabled &&
            this.props.substanceSearchEntry.pageLinks && (
              <Pagination
                pageLinks={this.props.substanceSearchEntry.pageLinks}
                onCursor={this.onCursor}
              />
            )}
        </div>
      </div>
    );
  }
}

Substances.propTypes = {
  loading: PropTypes.bool,
  access: PropTypes.object,
  organization: SentryTypes.Organization.isRequired,
  groupBy: PropTypes.string.isRequired,
  substanceSearchEntriesGet: PropTypes.func.isRequired,
  substanceSearchEntriesToggleSelectAll: PropTypes.func.isRequired,
  substanceSearchEntryExpandCollapse: PropTypes.func.isRequired,
  byIds: PropTypes.object,
  substanceSearchEntryToggleSelect: PropTypes.func.isRequired,
  substanceSearchEntry: PropTypes.object,
  location: PropTypes.object.isRequired,
};

const mapStateToProps = (state) => {
  return {
    substanceSearchEntry: state.substanceSearchEntry,
  };
};

// TODO: Rename all functions in `mapDispatchToProps` in other files so that they match the action
// creators name for consistency.
const mapDispatchToProps = (dispatch) => ({
  substanceSearchEntriesGet: (query, groupBy, cursor, isGroupHeader) =>
    dispatch(substanceSearchEntriesGet(query, groupBy, cursor, isGroupHeader)),
  substanceSearchEntriesToggleSelectAll: (doSelect) =>
    dispatch(substanceSearchEntriesToggleSelectAll(doSelect)),
  substanceSearchEntryToggleSelect: (id, doSelect) =>
    dispatch(substanceSearchEntryToggleSelect(id, doSelect)),
  substanceSearchEntryExpandCollapse: (parentEntry) =>
    dispatch(substanceSearchEntryExpandCollapse(parentEntry)),
});

export default connect(mapStateToProps, mapDispatchToProps)(Substances);
