import {
  USER_TASKS_GET_REQUEST,
  USER_TASKS_GET_SUCCESS,
  USER_TASKS_GET_FAILURE,
} from '../actions/userTask';

const initialState = {
  loading: false,
  errorMessage: null,
  userTasks: [],
};

const userTask = (state = initialState, action) => {
  switch (action.type) {
    case USER_TASKS_GET_REQUEST:
      return {
        ...state,
        errorMessage: null,
        loading: true,
      };
    case USER_TASKS_GET_SUCCESS: {
      return {
        ...state,
        userTasks: action.userTasks,
        errorMessage: null,
        loading: false,
      };
    }
    case USER_TASKS_GET_FAILURE:
      return {
        ...state,
        errorMessage: action.message,
        loading: false,
      };
    default:
      return state;
  }
};

export default userTask;