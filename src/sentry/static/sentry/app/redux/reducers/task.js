import {
  GET_TASK_REQUEST,
  GET_TASK_SUCCESS,
  GET_TASK_FAILURE,
  TOGGLE_SELECT_TASK,
  TOGGLE_SELECT_PAGE_OF_TASK,
  GET_TASK_LIST_REQUEST,
  GET_TASK_LIST_SUCCESS,
  GET_TASK_LIST_FAILURE,
} from '../actions/task';

import {list, entry} from './shared';

export const initialState = {
  ...list.initialState,
  ...entry.initialState,
};

const task = (state = initialState, action) => {
  switch (action.type) {
    case GET_TASK_LIST_REQUEST:
      return list.getListRequest(state, action);
    case GET_TASK_LIST_SUCCESS:
      return list.getListSuccess(state, action);
    case GET_TASK_LIST_FAILURE:
      return list.getListFailure(state, action);
    case TOGGLE_SELECT_TASK:
      return list.selectSingle(state, action);
    case TOGGLE_SELECT_PAGE_OF_TASK:
      return list.selectAll(state, action);
    case GET_TASK_REQUEST:
      return entry.getEntryRequest(state, action);
    case GET_TASK_SUCCESS:
      return entry.getEntrySuccess(state, action);
    case GET_TASK_FAILURE:
      return entry.getEntryFailure(state, action);
    default:
      return state;
  }
};

export default task;
