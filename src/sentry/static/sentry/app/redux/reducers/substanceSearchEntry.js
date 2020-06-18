import {Set} from 'immutable';
import {ListViewEntryGenerator} from 'app/redux/utils/substanceSearch';
import {ExpandedState} from 'app/redux/utils/expandedState';
import {
  SUBSTANCE_SEARCH_ENTRIES_GET_REQUEST,
  SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS,
  SUBSTANCE_SEARCH_ENTRIES_GET_FAILURE,
  SUBSTANCE_SEARCH_ENTRIES_TOGGLE_SELECT_ALL,
  SUBSTANCE_SEARCH_ENTRY_TOGGLE_SELECT,
  SUBSTANCE_SEARCH_ENTRY_EXPAND_COLLAPSE_REQUEST,
  SUBSTANCE_SEARCH_ENTRY_EXPAND_SUCCESS,
  SUBSTANCE_SEARCH_ENTRY_EXPAND_COLLAPSE_FAILURE,
  SUBSTANCE_SEARCH_ENTRY_EXPAND_CACHED,
  SUBSTANCE_SEARCH_ENTRY_COLLAPSE,
} from '../actions/substanceSearchEntry';

// NOTE: We export the initial state in order to use it in tests
export const initialState = {
  loading: false,
  errorMessage: null,
  substanceSearchEntries: [],
  allVisibleSelected: false,
  groupBy: 'substance',
  search: 'sample.name:',
  byIds: {}, // The actual substance entries (TODO: have parentById and childById?)
  visibleIds: [], // Sorted list of items visible in the current page
  selectedIds: new Set(), // The set of items selected, allowed to be outside of the current page

  paginationEnabled: true,
  pageLinks: null, // The links returned by the backend
  cursor: '', // The cursor into the current dataset
};

function toggleSelectPage(state, doSelect) {
  if (doSelect) {
    return new Set(state.visibleIds);
  } else {
    return new Set();
  }
}

const substanceSearchEntry = (state = initialState, action) => {
  const entryGenerator = new ListViewEntryGenerator();
  const expandedState = new ExpandedState({...state.byIds}, [...state.visibleIds]);
  switch (action.type) {
    case SUBSTANCE_SEARCH_ENTRY_EXPAND_COLLAPSE_REQUEST:
      return {
        ...state,
        errorMessage: null,
        loading: true,
        parentName: action.parentName,
      };
    case SUBSTANCE_SEARCH_ENTRY_EXPAND_SUCCESS:
      const expandedByIds = {};
      for (const entity of action.fetchedEntities) {
        expandedByIds[entity.global_id] = entryGenerator.wrap(entity);
      }
      expandedState.expandEntry(action.parentEntry.entity.global_id, expandedByIds);
      return {
        ...state,
        errorMessage: null,
        loading: false,
        byIds: expandedState.byIds,
        visibleIds: expandedState.visibleIds,
        pageLinks: action.link,
      };
    case SUBSTANCE_SEARCH_ENTRY_EXPAND_CACHED:
      const cachedIds = action.parentEntry.children.cachedIds;
      expandedState.expandCached(action.parentEntry.entity.global_id, cachedIds);
      return {
        ...state,
        errorMessage: null,
        loading: false,
        visibleIds: expandedState.visibleIds,
        pageLinks: action.link,
      };
    case SUBSTANCE_SEARCH_ENTRY_COLLAPSE:
      expandedState.collapseEntry(action.parentEntry.entity.global_id);
      return {
        ...state,
        errorMessage: null,
        loading: false,
        visibleIds: expandedState.visibleIds,
        pageLinks: action.link,
      };
    case SUBSTANCE_SEARCH_ENTRY_EXPAND_COLLAPSE_FAILURE:
      return {
        ...state,
        errorMessage: action.message,
        loading: false,
      };
    case SUBSTANCE_SEARCH_ENTRIES_GET_REQUEST:
      return {
        ...state,
        errorMessage: null,
        loading: true,
        search: action.search,
        groupBy: action.groupBy,
        cursor: action.cursor,
      };
    case SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS: {
      // The action provides us with the raw data as a list, here we turn it into
      // a dictionary and then update the store's byIds as required.
      const byIds = {};
      for (const entity of action.fetchedEntities) {
        const listViewEntry = entryGenerator.wrap(entity, action.groupBy);
        byIds[listViewEntry.entity.global_id] = listViewEntry;
      }
      const visibleIds = Object.keys(byIds).map(String);

      return {
        ...state,
        errorMessage: null,
        loading: false,
        byIds,
        visibleIds,
        pageLinks: action.link,
      };
    }
    case SUBSTANCE_SEARCH_ENTRIES_GET_FAILURE:
      return {
        ...state,
        errorMessage: action.message,
        loading: false,
      };
    case SUBSTANCE_SEARCH_ENTRIES_TOGGLE_SELECT_ALL:
      // Selects or deselects all items on the current page
      const doSelectAll =
        action.doSelect === null ? !state.allVisibleSelected : action.doSelect;

      return {
        ...state,
        allVisibleSelected: doSelectAll,
        selectedIds: toggleSelectPage(state, doSelectAll),
      };
    case SUBSTANCE_SEARCH_ENTRY_TOGGLE_SELECT:
      const doSelectSingle =
        action.doSelect === null ? !state.selectedIds.has(action.id) : action.doSelect;
      const newSet = doSelectSingle
        ? state.selectedIds.add(action.id)
        : state.selectedIds.delete(action.id);
      return {
        ...state,
        selectedIds: newSet,
      };
    default:
      return state;
  }
};

export default substanceSearchEntry;
