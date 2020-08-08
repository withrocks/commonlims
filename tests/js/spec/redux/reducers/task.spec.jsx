import {Set} from 'immutable';
import task, {initialState} from 'app/redux/reducers/task';

describe('task reducer', () => {
  const mockTask = {
    id: 1,
    name: 'Fragment Analyze',
    organization: 1,
    num_samples: 175,
  };

  it('should handle initial state', () => {
    expect(task(undefined, {})).toEqual(initialState);
  });

  it('should handle TASK_GET_REQUEST', () => {
    const state = task(initialState, {
      type: 'TASK_GET_REQUEST',
    });

    expect(state).toEqual({
      byIds: {},
      creating: false,
      detailsId: null,
      errorMessage: null,
      listViewState: {
        allVisibleSelected: false,
        groupBy: null,
        pagination: {cursor: '', pageLinks: null},
        search: null,
        selectedIds: Set(),
        visibleIds: [],
      },
      loading: false,
      loadingDetails: false,
    });
  });

  it('should set state correctly after getting a list of TaskDefinition', () => {
    const state = task(initialState, {
      type: 'GET_TASK_DEFINITION_LIST_SUCCESS',
      tasks: [mockTask],
    });

    // TODO: Shouldn't be empty!
    expect(state).toEqual({
      byIds: {},
      creating: false,
      detailsId: null,
      errorMessage: null,
      listViewState: {
        allVisibleSelected: false,
        groupBy: null,
        pagination: {cursor: '', pageLinks: null},
        search: null,
        selectedIds: Set(),
        visibleIds: [],
      },
      loading: false,
      loadingDetails: false,
    });
  });

  it('should handle TASK_DEFINITIONS_GET_FAILURE', () => {
    const state = task(initialState, {
      type: 'TASK_DEFINITIONS_GET_FAILURE',
      message: 'oopsiedoodle',
    });

    expect(state).toEqual({
      byIds: {},
      creating: false,
      detailsId: null,
      errorMessage: null,
      listViewState: {
        allVisibleSelected: false,
        groupBy: null,
        pagination: {cursor: '', pageLinks: null},
        search: null,
        selectedIds: Set(),
        visibleIds: [],
      },
      loading: false,
      loadingDetails: false,
    });
  });
});
