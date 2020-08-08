import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {projectSearchEntriesGet} from 'app/redux/actions/projectSearchEntry';
import {t} from 'app/locale';
import ListFilters from 'app/components/listFilters';
import ListView from 'app/components/listView';
import SentryTypes from 'app/sentryTypes';
import Pagination from 'app/components/pagination';
import {browserHistory} from 'react-router';
import ListActionBar from 'app/components/listActionBar';
import CreateProjectButton from 'app/views/projects/createProjectButton';

class Projects extends React.Component {
  constructor(props) {
    super(props);

    this.onGroup = this.onGroup.bind(this);
    this.onSort = this.onSort.bind(this);
    this.onSearch = this.onSearch.bind(this);
    this.onCursor = this.onCursor.bind(this);

    let {search, cursor, groupBy} = this.props.projectSearchEntry;
    const query = this.props.location.query;

    if (query) {
      search = query.search ? query.search : search;
      cursor = query.cursor ? query.cursor : cursor;
      groupBy = query.groupBy ? query.groupBy : groupBy;
    }

    this.onSearch(search, groupBy, cursor);
  }

  getHeaders() {
    // TODO: This should be returned as a contract from the plugin that is registered for this.
    return [
      {
        Header: 'Project name',
        id: 'name',
        accessor: 'name',
      },
      {
        Header: 'PI',
        id: 'pi',
        accessor: 'pi',
      },
    ];
  }

  onGroup(e) {
    this.setState({groupBy: {value: e}});
  }

  onSearch(search, groupBy, cursor) {
    this.props.projectSearchEntriesGet(search, groupBy, cursor);

    const location = this.props.location;
    const query = {
      ...location.query,
      search,
      groupBy,
      cursor,
    };

    browserHistory.push({pathname: location.pathname, query});
  }

  onCursor(cursor) {
    const {search, groupBy} = this.props.projectSearchEntry;
    this.onSearch(search, groupBy, cursor);
  }

  onGroup(e) {
    // TODO Fix this later (should be set through redux )
    this.setState({groupBy: {value: e}});
  }

  onSort(e) {
    // TODO Fix this later (should be set through redux )
  }

  listActionBar() {
    return (
      <ListActionBar>
        <div className="btn-group">
          <CreateProjectButton className="btn btn-sm btn-default" disabled={false}>
            {t('Create project')}
          </CreateProjectButton>
        </div>
      </ListActionBar>
    );
  }

  render() {
    // TODO: Rename css classes to something else than stream
    const groupOptions = [
      {key: 'project_type', title: t('Project type')},
      {key: 'pi', title: t('PI')},
      {key: 'name', title: t('Project name')},
    ];

    const {groupBy, query, byIds, visibleIds, loading} = this.props.projectSearchEntry;
    const actionBar = this.listActionBar();

    return (
      <div className="stream-row">
        <div className="stream-content">
          <ListFilters
            access={this.props.access}
            onSavedSearchCreate={this.onSavedSearchCreate}
            searchPlaceholder={t('Search for projects')}
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
            canSelect={false}
            visibleIds={visibleIds}
            loading={loading}
            listActionBar={actionBar}
          />
          {this.props.projectSearchEntry.paginationEnabled &&
            this.props.projectSearchEntry.pageLinks && (
              <Pagination
                pageLinks={this.props.projectSearchEntry.pageLinks}
                onCursor={this.onCursor}
              />
            )}
        </div>
      </div>
    );
  }
}

Projects.propTypes = {
  access: PropTypes.object,
  organization: SentryTypes.Organization.isRequired,
  projectSearchEntriesGet: PropTypes.func.isRequired,
  byIds: PropTypes.object,
  projectSearchEntry: PropTypes.object,
};

const mapStateToProps = (state) => {
  return {
    projectSearchEntry: state.projectSearchEntry,
  };
};

const mapDispatchToProps = (dispatch) => ({
  projectSearchEntriesGet: (query, groupBy, cursor) =>
    dispatch(projectSearchEntriesGet(query, groupBy, cursor)),
});

export default connect(mapStateToProps, mapDispatchToProps)(Projects);
