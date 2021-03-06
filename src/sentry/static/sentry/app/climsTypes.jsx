import PropTypes from 'prop-types';

export const Pagination = PropTypes.shape({
  pageLinks: PropTypes.string.isRequired, // The links returned by the backend
  cursor: PropTypes.string.isRequired,
});

// Defines what data is selected in a view, how it's grouped and so on.
// The data itself is expected to by in a dictionary called byIds.
export const ListViewState = PropTypes.shape({
  visibleIds: PropTypes.array.isRequired,
  selectedIds: PropTypes.array.isRequired,
  groupBy: PropTypes.string.isRequired,
  search: PropTypes.string.isRequired,
  pagination: Pagination.isRequired,
});

// All lists require this data shape
export const List = PropTypes.shape({
  byIds: PropTypes.object.isRequired,
  listViewState: ListViewState.isRequired,
});

// TODO: all these should have javascript-like property names
export const WorkBatch = PropTypes.shape({
  id: PropTypes.number.isRequired,
  name: PropTypes.string.isRequired,
  processDefinitionKey: PropTypes.string.isRequired,
  created_at: PropTypes.string.isRequired, // TODO: Map to date
  updated_at: PropTypes.string.isRequired,
  num_comments: PropTypes.number.isRequired,
  status: PropTypes.string.isRequired,
  subtasks: PropTypes.array.isRequired, // TODO: Describe
  transitions: PropTypes.array.isRequired,
  source: PropTypes.shape({
    substances: PropTypes.array, // TODO: describe
    containers: PropTypes.array,
  }).isRequired,
  target: PropTypes.shape({
    substances: PropTypes.array,
    containers: PropTypes.array,
  }),
  tabs: PropTypes.array.isRequired, // TODO: describe
});

const ClimsTypes = {
  List,
  WorkBatch,
};

export default ClimsTypes;
