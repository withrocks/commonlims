import axios from 'axios';

// SubstancesSearchEntry encapsulates a potentially grouped entry in the substance search UI
// The store always has one page worth of data. The list contains a generic wrapper class
// that contains the entry that's displayed. Each entry in the list may contain children
// and knows if they have been fetched or not.

// NOTE: an entry might for example contain a project or a container. It all depends
// on by what we're grouping. The page size is based on how many parent entries should be shown,
// not how many child entires there are. It's named SubstancesSearchEntry because that's what the
// user is searching for.

export const SUBSTANCE_SEARCH_ENTRIES_GET_REQUEST =
  'SUBSTANCE_SEARCH_ENTRIES_GET_REQUEST';
export const SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS =
  'SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS';
export const SUBSTANCE_SEARCH_ENTRIES_GET_FAILURE =
  'SUBSTANCE_SEARCH_ENTRIES_GET_FAILURE';
export const SUBSTANCE_SEARCH_ENTRIES_TOGGLE_SELECT_ALL =
  'SUBSTANCE_SEARCH_ENTRIES_TOGGLE_SELECT_ALL';
export const SUBSTANCE_SEARCH_ENTRY_TOGGLE_SELECT =
  'SUBSTANCE_SEARCH_ENTRY_TOGGLE_SELECT';

export const substanceSearchEntriesGetRequest = (search, groupBy, cursor) => {
  return {
    type: SUBSTANCE_SEARCH_ENTRIES_GET_REQUEST,
    search,
    groupBy,
    cursor,
  };
};

export const substanceSearchEntriesGetSuccess = (
  substanceSearchEntries,
  link,
  isGroupHeader
) => {
  return {
    type: SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS,
    substanceSearchEntries,
    link,
    isGroupHeader,
  };
};

export const substanceSearchEntriesGetFailure = err => ({
  type: SUBSTANCE_SEARCH_ENTRIES_GET_FAILURE,
  message: err,
});

export const substanceSearchEntriesGet = (search, groupBy, cursor) => dispatch => {
  dispatch(substanceSearchEntriesGetRequest(search, groupBy, cursor));
  const request = {
    params: {
      search,
      cursor,
    },
  };
  // return axios
  //   .get('/api/0/organizations/lab/substances/', request)
  //   .then(res => {
  //     dispatch(substanceSearchEntriesGetSuccess(res.data, res.headers.link));
  //   })
  //   .catch(err => dispatch(substanceSearchEntriesGetFailure(err)));

  if (groupBy === 'substance') {
    return axios
      .get('/api/0/organizations/lab/substances/', request)
      .then(res => {
        dispatch(substanceSearchEntriesGetSuccess(res.data, res.headers.link, false));
      })
      .catch(err => dispatch(substanceSearchEntriesGetFailure(err)));
  } else {
    const request2 = {
      params: {
        unique: true,
      },
    };
    return axios
      .get('/api/0/organizations/lab/substances/property/sample_type/', request2)
      .then(res => {
        dispatch(substanceSearchEntriesGetSuccess(res.data, res.headers.link, true));
      })
      .catch(err => dispatch(substanceSearchEntriesGetFailure(err)));
  }
};

export const substanceSearchEntriesToggleSelectAll = doSelect => {
  return {
    type: SUBSTANCE_SEARCH_ENTRIES_TOGGLE_SELECT_ALL,
    doSelect,
  };
};

export const substanceSearchEntryToggleSelect = (id, doSelect) => {
  return {
    type: SUBSTANCE_SEARCH_ENTRY_TOGGLE_SELECT,
    id,
    doSelect,
  };
};
