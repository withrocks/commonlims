import React from 'react';
import withOrganization from 'app/utils/withOrganization';
import {connect} from 'react-redux';
import {workBatchActions} from 'app/redux/actions/workBatch';
import ClimsTypes from 'app/climsTypes';
import ListViewContainer from 'app/components/listViewContainer';
import moment from 'moment';
import Link from 'app/components/link';

class WorkBatchListContainer extends React.Component {
  constructor(props) {
    super(props);
  }

  componentDidMount() {
    // TODO: Should we get the data initially in this didMount or just in the child's didMount?
    this.props.getWorkBatches();
  }

  getColumns() {
    return [
      {
        Header: 'Task',
        id: 'name',
        accessor: row => (
          <Link to={`/${this.props.organization.slug}/workbatches/${row.id}`}>
            {row.name}
          </Link>
        ),
        detailsLink: true,
      },
      {
        Header: 'Started',
        id: 'created_at',
        accessor: date => moment.utc(date.created_at).fromNow(),
      },
      {
        Header: 'Last updated',
        id: 'updated_at',
        accessor: date => moment.utc(date.updated_at).fromNow(),
      },
    ];
  }

  render() {
    // TODO: We need to clean up this access stuff. It makes more sense if it's already
    // a set on the org object
    return (
      <ListViewContainer
        access={new Set(this.props.organization.access)}
        organization={this.props.organization}
        loading={this.props.loading}
        errorMessage={this.props.errorMessage}
        location={this.props.location}
        columns={this.getColumns.bind(this)}
        groupOptions={this.groupOptions}
        searchHelpText="Search for work in progress"
        listViewState={this.props.listViewState}
        byIds={this.props.byIds}
        getEntries={this.props.getWorkBatches}
        toggleSingle={this.props.toggleSingle}
        canSelect={false}
      />
    );
  }
}

WorkBatchListContainer.propTypes = {
  ...ClimsTypes.List,
};

const mapStateToProps = state => state.workBatch;

const mapDispatchToProps = dispatch => ({
  getWorkBatches: () => dispatch(workBatchActions.getList()),
  toggleSingle: id => dispatch(workBatchActions.select(id)),
});

export default withOrganization(
  connect(mapStateToProps, mapDispatchToProps)(WorkBatchListContainer)
);
