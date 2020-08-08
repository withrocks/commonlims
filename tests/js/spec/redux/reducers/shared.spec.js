import {Set} from 'immutable';
import {resource} from 'app/redux/reducers/shared';
import {makeResourceActions} from 'app/redux/actions/shared';

const RESOURCE_NAME = 'SOME_RESOURCE';

// Tests the shared functionality of resource reducers
const initialState = {
  ...resource.initialState,
};

const reducer = resource.createReducer(RESOURCE_NAME, initialState);

const actions = makeResourceActions(RESOURCE_NAME, '/api/0/some-resource/');

function createSuccessState() {
  const originalState = {...initialState};
  const requestedState = reducer(
    originalState,
    actions.getListRequest('search', 'groupby', 'cursor')
  );
  return reducer(
    requestedState,
    actions.getListSuccess(
      [
        {id: '1', name: 'entry1'},
        {id: '2', name: 'entry2'},
      ],
      'link-to-more-results'
    )
  );
}

describe('shared resource reducer, list protocol', () => {
  it('has expected state after requesting', () => {
    const originalState = {...initialState};
    const requestedState = reducer(
      originalState,
      actions.getListRequest('search', 'groupby', 'cursor')
    );
    expect(requestedState).toEqual({
      loadingDetails: false,
      detailsId: null,
      loading: true,
      errorMessage: null,
      byIds: {},
      listViewState: {
        allVisibleSelected: false,
        groupBy: 'groupby',
        search: 'search',
        visibleIds: [],
        selectedIds: new Set(),
        pagination: {pageLinks: null, cursor: 'cursor'},
      },
      creating: false,
    });
  });

  it('has expected state when getting a successful response', () => {
    const successState = createSuccessState();
    expect(successState).toEqual({
      loadingDetails: false,
      detailsId: null,
      loading: false,
      errorMessage: null,
      byIds: {'1': {id: '1', name: 'entry1'}, '2': {id: '2', name: 'entry2'}},
      listViewState: {
        allVisibleSelected: false,
        groupBy: 'groupby',
        search: 'search',
        visibleIds: ['1', '2'],
        selectedIds: new Set(),
        pagination: {pageLinks: 'link-to-more-results', cursor: 'cursor'},
      },
      creating: false,
    });
  });

  it('has expected state when getting a failed response', () => {
    const originalState = {...initialState};
    const requestedState = reducer(
      originalState,
      actions.getListRequest('search', 'groupby', 'cursor')
    );
    const failedState = reducer(
      requestedState,
      actions.getListFailure(500, 'some error')
    );
    expect(failedState).toEqual({
      loadingDetails: false,
      detailsId: null,
      loading: false,
      errorMessage: 'some error',
      byIds: {},
      listViewState: {
        allVisibleSelected: false,
        groupBy: 'groupby',
        search: 'search',
        visibleIds: [],
        selectedIds: new Set(),
        pagination: {pageLinks: null, cursor: 'cursor'},
      },
      creating: false,
    });
  });

  it('has expected state when selecting/deselecting a page', () => {
    const successState = createSuccessState();
    const selectedPageState = reducer(successState, actions.selectPage(true));
    const expectedSelectedPageState = {
      ...successState,
      listViewState: {
        ...successState.listViewState,
        allVisibleSelected: true,
        selectedIds: new Set(['1', '2']),
      },
    };
    expect(selectedPageState).toEqual(expectedSelectedPageState);
    const unSelectedPageState = reducer(selectedPageState, actions.selectPage(false));

    expect(unSelectedPageState).toEqual({
      ...expectedSelectedPageState,
      listViewState: {
        ...expectedSelectedPageState.listViewState,
        allVisibleSelected: false,
        selectedIds: new Set(),
      },
    });
  });

  it('has expected state when selecting/deselecting a single entry', () => {
    const successState = createSuccessState();
    const selectedEntryState = reducer(successState, actions.select('1', true));
    const expectedSelectedEntryState = {
      ...successState,
      listViewState: {
        ...successState.listViewState,
        selectedIds: new Set(['1']),
      },
    };
    expect(selectedEntryState).toEqual(expectedSelectedEntryState);

    const unSelectedEntryState = reducer(selectedEntryState, actions.select('1', false));
    expect(unSelectedEntryState).toEqual({
      ...selectedEntryState,
      listViewState: {
        ...successState.listViewState,
        selectedIds: new Set(),
      },
    });
  });

  it('has expected state when requesting an entry to be created', () => {
    const successState = createSuccessState();
    const createEntryRequestState = reducer(
      successState,
      actions.createRequest({id: '1'})
    );
    expect(createEntryRequestState).toEqual({
      ...successState,
      creating: true,
    });
  });

  it('has expected state when requesting an entry has successfully been created', () => {
    const newItem = {
      id: '3',
      name: 'entry3',
    };
    const successState = createSuccessState();
    const createEntryRequestState = reducer(successState, actions.createRequest(newItem));
    const createEntrySuccessState = reducer(
      createEntryRequestState,
      actions.createSuccess(newItem)
    );

    expect(createEntrySuccessState).toEqual({
      ...successState,
      byIds: {
        ...successState.byIds,
        '3': newItem,
      },
    });
  });
});
