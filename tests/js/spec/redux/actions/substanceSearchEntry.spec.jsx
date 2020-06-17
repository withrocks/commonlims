import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import moxios from 'moxios';

import {
  SUBSTANCE_SEARCH_ENTRIES_GET_REQUEST,
  SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS,
  SUBSTANCE_SEARCH_ENTRIES_GET_FAILURE,
  SUBSTANCE_SEARCH_ENTRIES_TOGGLE_SELECT_ALL,
  SUBSTANCE_SEARCH_ENTRY_TOGGLE_SELECT,
  substanceSearchEntriesGetRequest,
  substanceSearchEntriesGetSuccess,
  substanceSearchEntriesGetFailure,
  substanceSearchEntriesGet,
  substanceSearchEntryToggleSelect,
  substanceSearchEntriesToggleSelectAll,
} from 'app/redux/actions/substanceSearchEntry';

const middlewares = [thunk];
const mockStore = configureStore(middlewares);

describe('substance redux actions', function () {
  beforeEach(function () {
    moxios.install();
  });

  afterEach(function () {
    moxios.uninstall();
  });

  const mockResponseNoGroup = TestStubs.SubstanceSearchEntries(5, 'substance');

  describe('get', () => {
    it('should create an action to request substance search entries GET', () => {
      const expectedAction = {
        type: SUBSTANCE_SEARCH_ENTRIES_GET_REQUEST,
      };
      expect(substanceSearchEntriesGetRequest()).toEqual(expectedAction);
    });

    it('should create an action to handle substance search entries GET success', () => {
      const fetchedEntities = [mockResponseNoGroup];
      const expectedAction = {
        type: SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS,
        fetchedEntities,
      };
      expect(substanceSearchEntriesGetSuccess(fetchedEntities)).toEqual(expectedAction);
    });

    it('should create an action to handle substance search entries GET failure', () => {
      const expectedAction = {
        type: SUBSTANCE_SEARCH_ENTRIES_GET_FAILURE,
        message: 'my error',
      };
      expect(substanceSearchEntriesGetFailure('my error')).toEqual(expectedAction);
    });

    it('should create an action to GET substance search entries from the substances API', async () => {
      const fetchedEntities = mockResponseNoGroup;
      const store = mockStore({substances: []});

      // TODO: New endpoint
      moxios.stubRequest('/api/0/organizations/lab/substances/?search=search', {
        status: 200,
        responseText: fetchedEntities,
        headers: [],
      });

      const search = 'search';
      const groupBy = 'substance';
      const cursor = undefined;

      const expectedActions = [
        {
          type: SUBSTANCE_SEARCH_ENTRIES_GET_REQUEST,
          search,
          groupBy,
        },
        {
          type: SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS,
          fetchedEntities,
          groupBy,
        },
      ];

      // TODO: return
      return store
        .dispatch(substanceSearchEntriesGet(search, groupBy, cursor))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions);
          const request = moxios.requests.mostRecent();
          expect(request.url).toBe('/api/0/organizations/lab/substances/?search=search');
        });
    });

    it('should create an action to GET grouped substances', () => {
      const mockResponseGrouped = ['sample_type1'];

      const fetchedEntities = mockResponseGrouped;
      const store = mockStore({substances: []});

      moxios.stubRequest(
        '/api/0/organizations/lab/substances/property/sample_type/?unique=true',
        {
          status: 200,
          responseText: fetchedEntities,
          headers: [],
        }
      );

      const search = 'search';
      const groupBy = 'sample_type';
      const cursor = undefined;
      const isGroupHeader = true;

      const expectedActions = [
        {
          type: SUBSTANCE_SEARCH_ENTRIES_GET_REQUEST,
          search,
          groupBy,
        },
        {
          type: SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS,
          groupBy,
          fetchedEntities,
        },
      ];
      return store
        .dispatch(substanceSearchEntriesGet(search, groupBy, cursor, isGroupHeader))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions);
          const request = moxios.requests.mostRecent();
          expect(request.url).toBe(
            '/api/0/organizations/lab/substances/property/sample_type/?unique=true'
          );
        });
    });
  });

  describe('select', () => {
    it('should create an action to toggle the user selection of a substance search entry', () => {
      const expectedAction = {
        type: SUBSTANCE_SEARCH_ENTRY_TOGGLE_SELECT,
        id: 100,
        doSelect: true,
      };
      expect(substanceSearchEntryToggleSelect(100, true)).toEqual(expectedAction);
    });

    it('should create an action to toggle the user selection of all substance search entries', () => {
      const expectedAction = {
        type: SUBSTANCE_SEARCH_ENTRIES_TOGGLE_SELECT_ALL,
        doSelect: true,
      };
      expect(substanceSearchEntriesToggleSelectAll(true)).toEqual(expectedAction);
    });
  });
});
