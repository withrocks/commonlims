import substanceSearchEntry, {
  initialState,
} from 'app/redux/reducers/substanceSearchEntry';
import {Set} from 'immutable';
import {keyBy} from 'lodash';

// TODO: Should we rename the store to e.g. `SearchEntry`, as it's actually going to be able
// to search for project, container and substances, but with child elements?

describe('substance reducer', () => {
  const mockResponseNoGroup = TestStubs.SubstanceSearchEntries(2, 'substance');
  const mockResponseNoGroupById = keyBy(mockResponseNoGroup, entry => entry.global_id);

  it('should handle initial state', () => {
    expect(substanceSearchEntry(undefined, {})).toEqual(initialState);
  });

  it('should handle SUBSTANCE_SEARCH_ENTRIES_GET_REQUEST', () => {
    const prevState = {
      ...initialState,
      loading: false,
      errorMessage: 'oops',
    };

    const nextState = substanceSearchEntry(prevState, {
      type: 'SUBSTANCE_SEARCH_ENTRIES_GET_REQUEST',
      groupBy: 'aGroup',
      search: 'aSearch',
      cursor: 'aCursor',
    });

    expect(nextState).toEqual({
      ...prevState,
      loading: true,
      errorMessage: null,
      groupBy: 'aGroup',
      search: 'aSearch',
      cursor: 'aCursor',
    });
  });

  it('state is not mutated when no grouping', () => {
    // Arrange
    const prevState = {
      ...initialState,
      loading: true,
      errorMessage: 'oops',
    };

    const responseNoGroup = TestStubs.SubstanceSearchEntries(2, 'substance');

    const action = {
      type: 'SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS',
      substanceSearchEntries: responseNoGroup,
      groupBy: 'substance',
      link: 'some-link',
    };

    const action_orig = JSON.parse(JSON.stringify(action));
    const prevState_orig = JSON.parse(JSON.stringify(prevState));

    // Act
    substanceSearchEntry(prevState, action);

    // Assert
    // It has to be 'copied' in the same way as before. An empty Immutable.Set()
    // is converted to []
    const actionAfter = JSON.parse(JSON.stringify(action));
    const stateAfter = JSON.parse(JSON.stringify(prevState));
    expect(actionAfter).toEqual(action_orig);
    expect(stateAfter).toEqual(prevState_orig);
  });

  it('state is not mutated when grouping', () => {
    // Arrange
    const responseGrouped = ['my_sample_type'];

    const prevState = {
      ...initialState,
      loading: true,
      errorMessage: 'oops',
    };

    const action = {
      type: 'SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS',
      substanceSearchEntries: responseGrouped,
      groupBy: 'sample_type',
      link: 'some-link',
    };
    const prevState_orig = JSON.parse(JSON.stringify(prevState));
    const action_orig = JSON.parse(JSON.stringify(action));

    // Act
    substanceSearchEntry(prevState, action);

    // Assert
    const treatedAction = JSON.parse(JSON.stringify(action));
    const treatedState = JSON.parse(JSON.stringify(prevState));
    expect(treatedAction).toEqual(action_orig);
    expect(treatedState).toEqual(prevState_orig);
  });

  it('should handle SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS for not-grouped', () => {
    // Arrange
    const prevState = {
      ...initialState,
      loading: true,
      errorMessage: 'oops',
    };

    const action = {
      type: 'SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS',
      substanceSearchEntries: mockResponseNoGroup,
      groupBy: 'substance',
      link: 'some-link',
    };

    // Act
    const nextState = substanceSearchEntry(prevState, action);

    // Assert

    const responseFromReducer = TestStubs.SubstanceEntriesFromReducer(2, 'substance');
    const expectedByIds = keyBy(responseFromReducer, entry => entry.global_id);
    expect(nextState).toEqual({
      ...prevState,
      errorMessage: null,
      loading: false,
      visibleIds: ['Substance-1', 'Substance-2'],
      byIds: expectedByIds,
      pageLinks: 'some-link',
    });
  });

  it('should handle SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS for sample type', () => {
    // Arrange
    const mockResponseGrouped = ['my_sample_type'];

    const action = {
      type: 'SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS',
      substanceSearchEntries: mockResponseGrouped,
      link: 'some-link',
      groupBy: 'sample_type',
    };

    const prevState = {
      ...initialState,
      loading: true,
      errorMessage: 'oops',
    };

    // Act
    const nextState = substanceSearchEntry(prevState, action);

    // Assert
    const expectedEntryFromReducer = [
      {
        global_id: 'Parent-1',
        name: 'my_sample_type',
        isGroupHeader: true,
      },
    ];

    const expectedByIds = keyBy(expectedEntryFromReducer, entry => entry.global_id);

    expect(nextState).toEqual({
      ...prevState,
      errorMessage: null,
      loading: false,
      visibleIds: ['Parent-1'],
      byIds: expectedByIds,
      pageLinks: 'some-link',
    });
  });

  it('should handle SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS for containers', () => {
    // Arrange
    const mockResponseGrouped = [{name: 'mycontainer', global_id: 'Container-1'}];

    const action = {
      type: 'SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS',
      substanceSearchEntries: mockResponseGrouped,
      link: 'some-link',
      groupBy: 'container',
    };

    const prevState = {
      ...initialState,
      loading: true,
      errorMessage: 'oops',
    };

    // Act
    const nextState = substanceSearchEntry(prevState, action);

    // Assert
    const expectedEntryFromReducer = [
      {
        global_id: 'Container-1',
        name: 'mycontainer',
        isGroupHeader: true,
      },
    ];

    const expectedByIds = keyBy(expectedEntryFromReducer, entry => entry.global_id);

    expect(nextState).toEqual({
      ...prevState,
      errorMessage: null,
      loading: false,
      visibleIds: ['Container-1'],
      byIds: expectedByIds,
      pageLinks: 'some-link',
    });
  });

  it('should handle SUBSTANCE_SEARCH_ENTRIES_GET_FAILURE', () => {
    const prevState = {
      ...initialState,
      loading: true,
    };

    const nextState = substanceSearchEntry(prevState, {
      type: 'SUBSTANCE_SEARCH_ENTRIES_GET_FAILURE',
      message: 'oopsiedoodle',
    });

    expect(nextState).toEqual({
      ...initialState,
      loading: false,
      errorMessage: 'oopsiedoodle',
    });
  });

  it('should handle toggling a single search entry', () => {
    const prevState = {
      ...initialState,
      byIds: mockResponseNoGroupById,
    };

    const nextState = substanceSearchEntry(prevState, {
      type: 'SUBSTANCE_SEARCH_ENTRY_TOGGLE_SELECT',
      id: 1,
      doSelect: null, // null means toggle from previous state
    });

    expect(nextState).toEqual({
      ...prevState,
      byIds: mockResponseNoGroupById,
      selectedIds: prevState.selectedIds.add(1),
    });
  });

  it('should handle de-selecting a substance', () => {
    const prevState = {
      ...initialState,
      selectedIds: initialState.selectedIds.add(1),
    };

    const nextState = substanceSearchEntry(prevState, {
      type: 'SUBSTANCE_SEARCH_ENTRY_TOGGLE_SELECT',
      id: 1,
      doSelect: null,
    });

    expect(nextState).toEqual(initialState);
  });

  it('gets expected page state through mock', () => {
    // This test makes sure that our test stub returns the expected state, so we don't have
    // to in the tests that use it. Note that this duplicates the test for
    // SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS as the stub uses that action under the hood
    const prevState = TestStubs.SubstanceSearchEntriesPageState(2, 'substance');
    expect(prevState.visibleIds).toEqual(['Substance-1', 'Substance-2']);
    expect(prevState.selectedIds).toEqual(new Set());
  });

  it('should handle selecting and deselecting all search entries', () => {
    const state1 = TestStubs.SubstanceSearchEntriesPageState(2, 'substance');
    expect(state1.selectedIds.isEmpty()).toBe(true);

    const state2 = substanceSearchEntry(state1, {
      type: 'SUBSTANCE_SEARCH_ENTRIES_TOGGLE_SELECT_ALL',
      doSelect: true,
    });
    expect(state2.selectedIds.isEmpty()).toBe(false);
    expect(state2.selectedIds).toEqual(new Set(['Substance-1', 'Substance-2']));

    const state3 = substanceSearchEntry(state2, {
      type: 'SUBSTANCE_SEARCH_ENTRIES_TOGGLE_SELECT_ALL',
      doSelect: false,
    });
    expect(state3.selectedIds.isEmpty()).toBe(true);
  });
});
