import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
//import {substancesGet} from 'app/redux/actions/substance';
import {
  substanceSearchEntriesGet,
  substanceSearchEntriesToggleSelectAll,
  substanceSearchEntryToggleSelect,
} from 'app/redux/actions/substanceSearchEntry';
import {t} from 'app/locale';
import ListFilters from 'app/components/listFilters';
import ListView from 'app/components/listView';
import SentryTypes from 'app/sentryTypes';
import ListActionBar from 'app/components/listActionBar';

class Substances extends React.Component {
  constructor(props) {
    super(props);
    this.onImported = this.onImported.bind(this);
    this.onSavedSearchChange = this.onSavedSearchCreate.bind(this);
    this.onGroup = this.onGroup.bind(this);
    this.onSort = this.onSort.bind(this);
    this.onSearch = this.onSearch.bind(this);
    this.toggleAll = this.toggleAll.bind(this);

    let {query} = this.props.substanceSearchEntry;
    const {groupBy} = this.props.substanceSearchEntry;

    if (query === '') {
      query = 'sample.name:sample'; // Add some default search for demo purposes
    }
    this.props.substanceSearchEntriesGet(query, groupBy);
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
        accessor: 'name',
        aggregate: vals => '',
      },
      {
        Header: 'Container',
        id: 'container',
        accessor: d => (d.location ? d.location.container.name : '<No location>'),
      },
      {
        Header: 'Index',
        id: 'index',
        accessor: d => (d.location ? d.location.index : '<No location>'),
        aggregate: vals => '',
      },
      {
        Header: 'Volume',
        id: 'volume',
        accessor: d => (d.properties.volume ? d.properties.volume.value : null),
        aggregate: vals => '',
      },
      {
        Header: 'Sample Type',
        id: 'sample_type',
        accessor: d => (d.properties.sample_type ? d.properties.sample_type.value : null),
      },
      {
        Header: 'Priority',
        id: 'priority',
        accessor: d => d.priority,
        aggregate: vals => '',
      },
      {
        Header: 'Waiting',
        id: 'days_waiting',
        accessor: d => d.days_waiting,
      },
    ];
  }

  onImported() {
    this.props.substanceSearchEntriesGet();
  }

  onGroup(e) {
    this.setState({groupBy: {value: e}});
  }

  onSort(e) {}

  onSearch(query, groupBy) {
    // TODO
    this.props.substanceSearchEntriesGet(query, groupBy);
  }

  listActionBar(canAssignToWorkflow, orgId) {
    return (
      <ListActionBar
        realtimeActive={false}
        query=""
        orgId={orgId}
        canAssignToWorkflow={canAssignToWorkflow}
      />
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
      substanceSearchEntries,
      byIds,
      visibleIds,
      selectedIds,
      loading,
      allVisibleSelected,
    } = this.props.substanceSearchEntry;

    // TODO: The ListActionBar component currently has substance specific things, like
    // these workflows to assign. Refactor so this component is truly generic.
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
            data={substanceSearchEntries}
            dataById={byIds}
            visibleIds={visibleIds}
            selectedIds={selectedIds}
            loading={loading}
            canSelect={true}
            allVisibleSelected={allVisibleSelected}
            toggleAll={this.toggleAll}
            toggleSingle={this.props.substanceSearchEntryToggleSelect}
            listActionBar={actionBar}
          />
        </div>
      </div>
    );
  }
}

Substances.propTypes = {
  loading: PropTypes.bool,
  access: PropTypes.object,
  organization: SentryTypes.Organization.isRequired,
  allVisibleSelected: PropTypes.bool.isRequired,
  substanceSearchEntries: PropTypes.arrayOf(PropTypes.shape({})),
  groupBy: PropTypes.string.isRequired,
  substanceSearchEntriesGet: PropTypes.func.isRequired,
  substanceSearchEntriesToggleSelectAll: PropTypes.func.isRequired,
  byIds: PropTypes.object,
  substanceSearchEntryToggleSelect: PropTypes.func.isRequired,
  substanceSearchEntry: PropTypes.object,
};

const mapStateToProps = state => {
  return {
    substanceSearchEntry: state.substanceSearchEntry,
  };
};

// TODO: Rename all functions in `mapDispatchToProps` in other files so that they match the action
// creators name for consistency.
const mapDispatchToProps = dispatch => ({
  substanceSearchEntriesGet: query => dispatch(substanceSearchEntriesGet(query)),
  substanceSearchEntriesToggleSelectAll: doSelect =>
    dispatch(substanceSearchEntriesToggleSelectAll(doSelect)),
  substanceSearchEntryToggleSelect: (id, doSelect) =>
    dispatch(substanceSearchEntryToggleSelect(id, doSelect)),
});

export default connect(mapStateToProps, mapDispatchToProps)(Substances);
