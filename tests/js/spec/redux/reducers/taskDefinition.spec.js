import {Set} from 'immutable';
import taskDefinition, {initialState} from 'app/redux/reducers/taskDefinition';
import {taskDefinitionActions} from 'app/redux/actions/taskDefinition';

describe('taskDefinition reducer, list protocol', () => {
  it('has expected state after requesting getting a list', () => {
    const requested = taskDefinition(
      initialState,
      taskDefinitionActions.getListRequest('search', 'groupBy', 'cursor')
    );
    const expected = {
      loading: true,
      errorMessage: null,
      byIds: {},
      listViewState: {
        allVisibleSelected: false,
        visibleIds: [],
        selectedIds: Set(),
        search: 'search',
        groupBy: 'groupBy',
        pagination: {
          pageLinks: null,
          cursor: 'cursor',
        },
      },
      creating: false,
      loadingDetails: false,
      detailsId: null,
    };
    expect(requested).toEqual(expected);
  });

  it('expected state after ListSuccess', () => {
    const requested = taskDefinition(
      initialState,
      taskDefinitionActions.getListRequest('search', 'groupBy', 'cursor')
    );
    const entries = [TestStubs.TaskDefinition(1), TestStubs.TaskDefinition(2)];
    const succeeded = taskDefinition(
      requested,
      taskDefinitionActions.getListSuccess(entries, 'pageLinks')
    );

    const expected = {
      loading: false,
      errorMessage: null,
      byIds: {
        1: entries[0],
        2: entries[1],
      },
      listViewState: {
        allVisibleSelected: false,
        visibleIds: [entries[0].id, entries[1].id],
        selectedIds: Set(),
        search: 'search',
        groupBy: 'groupBy',
        pagination: {
          pageLinks: 'pageLinks',
          cursor: 'cursor',
        },
      },
      creating: false,
      loadingDetails: false,
      detailsId: null,
    };
    expect(succeeded).toEqual(expected);
  });
});
