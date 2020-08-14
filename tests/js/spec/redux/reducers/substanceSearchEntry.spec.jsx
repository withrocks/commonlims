import substanceSearchEntry, {
  initialState,
} from 'app/redux/reducers/substanceSearchEntry';
import merge from 'lodash/merge';
import {Set} from 'immutable';
import {keyBy} from 'lodash';

// TODO: Should we rename the store to e.g. `SearchEntry`, as it's actually going to be able
// to search for project, container and substances, but with child elements?

describe('substance reducer', () => {
  const mockResponseNoGroup = TestStubs.SubstanceSearchEntries(2, 'substance');
  const mockResponseNoGroupById = keyBy(mockResponseNoGroup, (entry) => entry.global_id);

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
      fetchedEntities: responseNoGroup,
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
      fetchedEntities: responseGrouped,
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
      fetchedEntities: mockResponseNoGroup,
      groupBy: 'substance',
      link: 'some-link',
    };

    // Act
    const nextState = substanceSearchEntry(prevState, action);

    // Assert

    const responseFromReducer = TestStubs.ListViewEntriesFromReducer(2, 'substance');
    const expectedByIds = keyBy(responseFromReducer, (entry) => entry.entity.global_id);
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
      fetchedEntities: mockResponseGrouped,
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
        entity: {
          global_id: 'Parent-1',
          name: 'my_sample_type',
        },
        isGroupHeader: true,
        children: {
          isFetched: false,
          isExpanded: false,
          cachedIds: [],
        },
      },
    ];

    const expectedByIds = keyBy(
      expectedEntryFromReducer,
      (entry) => entry.entity.global_id
    );

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
      fetchedEntities: mockResponseGrouped,
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
        entity: {
          global_id: 'Container-1',
          name: 'mycontainer',
        },
        isGroupHeader: true,
        children: {
          isFetched: false,
          isExpanded: false,
          cachedIds: [],
        },
      },
    ];

    const expectedByIds = keyBy(
      expectedEntryFromReducer,
      (entry) => entry.entity.global_id
    );

    expect(nextState).toEqual({
      ...prevState,
      errorMessage: null,
      loading: false,
      visibleIds: ['Container-1'],
      byIds: expectedByIds,
      pageLinks: 'some-link',
    });
  });

  it('should handle SUBSTANCE_SEARCH_ENTRIES_EXPAND_COLLAPSE_FAILURE', () => {
    const prevState = {
      ...initialState,
      loading: true,
    };

    const nextState = substanceSearchEntry(prevState, {
      type: 'SUBSTANCE_SEARCH_ENTRY_EXPAND_COLLAPSE_FAILURE',
      message: 'oopsiedoodle',
    });

    expect(nextState).toEqual({
      ...initialState,
      loading: false,
      errorMessage: 'oopsiedoodle',
    });
  });

  it('should handle SUBSTANCE_SEARCH_ENTRIES_EXPAND_SUCCESS', () => {
    // Arrange
    const parentEntry = {
      entity: {
        global_id: 'Container-2',
        name: 'mycontainer',
      },
      children: {
        isFetched: false,
      },
    };

    const action = {
      type: 'SUBSTANCE_SEARCH_ENTRY_EXPAND_SUCCESS',
      fetchedEntities: mockResponseNoGroup,
      link: 'some-link',
      parentEntry,
    };

    const prevState = {
      ...initialState,
      visibleIds: ['Container-1', 'Container-2'],
      byIds: {
        'Container-2': parentEntry,
      },
      loading: true,
      errorMessage: 'oops',
    };

    // Act
    const nextState = substanceSearchEntry(prevState, action);

    // Assert
    const transformedEntries = mockResponseNoGroup.map((e) => {
      return {
        entity: e,
        isGroupHeader: false,
      };
    });
    const updatedParentEntry = {
      ...parentEntry,
      children: {
        ...parentEntry.children,
        isFetched: true,
        isExpanded: true,
        cachedIds: mockResponseNoGroup.map((e) => {
          return e.global_id;
        }),
      },
    };
    transformedEntries.push(updatedParentEntry);

    const expectedByIds = keyBy(transformedEntries, (entry) => entry.entity.global_id);

    expect(nextState).toEqual({
      ...prevState,
      errorMessage: null,
      loading: false,
      visibleIds: ['Container-1', 'Container-2', 'Substance-1', 'Substance-2'],
      byIds: expectedByIds,
      pageLinks: 'some-link',
    });
  });

  it('should handle SUBSTANCE_SEARCH_ENTRIES_EXPAND_CACHED', () => {
    // Arrange
    const parentEntry = {
      entity: {
        global_id: 'Container-2',
        name: 'mycontainer',
      },
      children: {
        isFetched: true,
        isExpanded: false,
        cachedIds: mockResponseNoGroup.map((e) => {
          return e.global_id;
        }),
      },
    };

    const listViewEntries = mockResponseNoGroup.map((e) => {
      return {
        entity: e,
        isGroupHeader: false,
      };
    });
    listViewEntries.push(parentEntry);
    const originalByIds = keyBy(listViewEntries, (e) => e.entity.global_id);

    const prevState = {
      ...initialState,
      visibleIds: ['Container-1', 'Container-2'],
      byIds: originalByIds,
      loading: true,
      errorMessage: 'oops',
    };

    const action = {
      type: 'SUBSTANCE_SEARCH_ENTRY_EXPAND_CACHED',
      parentEntry,
    };

    // Act
    const nextState = substanceSearchEntry(prevState, action);

    // Assert

    const updatedByIds = {
      ...originalByIds,
    };
    updatedByIds[parentEntry.entity.global_id] = {
      ...parentEntry,
      children: {
        ...parentEntry.children,
        isExpanded: true,
      },
    };
    expect(nextState).toEqual({
      ...prevState,
      errorMessage: null,
      loading: false,
      visibleIds: ['Container-1', 'Container-2', 'Substance-1', 'Substance-2'],
      byIds: updatedByIds,
      pageLinks: undefined,
    });
  });

  it('should handle SUBSTANCE_SEARCH_ENTRIES_COLLAPSE', () => {
    // Arrange
    const parentEntry = {
      entity: {
        global_id: 'Container-2',
        name: 'mycontainer',
      },
      children: {
        isFetched: true,
        isExpanded: true,
        cachedIds: mockResponseNoGroup.map((e) => {
          return e.global_id;
        }),
      },
    };

    const listViewEntries = mockResponseNoGroup.map((e) => {
      return {
        entity: e,
        isGroupHeader: false,
      };
    });
    listViewEntries.push(parentEntry);
    const byIds = keyBy(listViewEntries, (e) => e.entity.global_id);

    const prevState = {
      ...initialState,
      visibleIds: ['Container-1', 'Container-2', 'Substance-1', 'Substance-2'],
      byIds,
      loading: true,
      errorMessage: 'oops',
    };

    const action = {
      type: 'SUBSTANCE_SEARCH_ENTRY_COLLAPSE',
      parentEntry,
    };

    // Act
    const nextState = substanceSearchEntry(prevState, action);
    const updatedByIds = {
      ...byIds,
    };
    updatedByIds[parentEntry.entity.global_id] = {
      ...parentEntry,
      children: {
        ...parentEntry.children,
        isExpanded: false,
      },
    };
    // Assert
    expect(nextState).toEqual({
      ...prevState,
      errorMessage: null,
      loading: false,
      visibleIds: ['Container-1', 'Container-2'],
      byIds: updatedByIds,
      pageLinks: undefined,
    });
  });

  it.skip('should use cache at second expand event', () => {
    // Arrange
    const parentEntry = {
      entity: {
        global_id: 'Container-2',
        name: 'mycontainer',
      },
      children: {
        isFetched: false,
      },
    };
    const firstAction = {
      type: 'SUBSTANCE_SEARCH_ENTRY_EXPAND_SUCCESS',
      expandedEntries: mockResponseNoGroup,
      link: 'some-link',
      parentEntry,
    };
    const originalState = {
      ...initialState,
      visibleIds: ['Container-1', 'Container-2'],
      byIds: {
        'Container-2': parentEntry,
      },
      loading: true,
      errorMessage: 'oops',
    };

    const fetchedState = substanceSearchEntry(originalState, firstAction);

    const cachedParent = fetchedState.byIds[parentEntry.entity.global_id];
    const cachedAction = {
      type: 'SUBSTANCE_SEARCH_ENTRY_EXPAND_CACHED',
      parentEntry: cachedParent,
    };
    // Act
    const expandedState = substanceSearchEntry(fetchedState, cachedAction);

    // Assert
    const transformedEntries = mockResponseNoGroup.map((e) => {
      return {
        entity: e,
        isGroupHeader: false,
      };
    });
    const updatedParentEntry = {
      ...parentEntry,
      children: {
        ...parentEntry.children,
        isFetched: true,
        cachedIds: mockResponseNoGroup.map((e) => {
          return e.global_id;
        }),
      },
    };
    transformedEntries.push(updatedParentEntry);

    const expectedByIds = keyBy(transformedEntries, (entry) => entry.entity.global_id);

    expect(expandedState).toEqual({
      ...originalState,
      errorMessage: null,
      loading: false,
      visibleIds: ['Container-1', 'Container-2', 'Substance-1', 'Substance-2'],
      byIds: expectedByIds,
      pageLinks: undefined,
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
