import {Set} from 'immutable';
import taskDefinition, {initialState} from 'app/redux/reducers/taskDefinition';
import {taskDefinitionActions} from 'app/redux/actions/taskDefinition';

describe('taskDefinition reducer, list protocol', () => {
  it('has expected state after requesting getting a list', () => {
    const requested = taskDefinition(
      initialState,
      taskDefinitionActions.getListRequest()
    );
    const expected = {
      loading: true,
      errorMessage: null,
      byIds: {},
      listViewState: {
        allVisibleSelected: false,
        visibleIds: [],
        selectedIds: Set(),
        search: null,
        groupBy: null,
        pagination: {
          pageLinks: null,
          cursor: null,
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
      taskDefinitionActions.getListRequest()
    );
    const entries = [TestStubs.TaskDefinition(1), TestStubs.TaskDefinition(2)];
    const succeeded = taskDefinition(
      requested,
      taskDefinitionActions.getListSuccess(entries)
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
        search: null,
        groupBy: null,
        pagination: {
          pageLinks: null,
          cursor: null,
        },
      },
      creating: false,
      loadingDetails: false,
      detailsId: null,
    };
    expect(succeeded).toEqual(expected);
  });
});
