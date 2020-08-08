import axios from 'axios';

////// List of Task
export const GET_TASK_LIST_REQUEST = 'GET_TASK_LIST_REQUEST';
export const getTaskListRequest = () => {
  return {
    type: GET_TASK_LIST_REQUEST,
  };
};

export const GET_TASK_LIST_SUCCESS = 'GET_TASK_LIST_SUCCESS';
export const getTaskListSuccess = entries => {
  return {
    type: GET_TASK_LIST_SUCCESS,
    entries,
  };
};

export const GET_TASK_LIST_FAILURE = 'GET_TASK_LIST_FAILURE';
export const getTaskListFailure = err => ({
  type: GET_TASK_LIST_FAILURE,
  message: err,
});

export const getTaskList = (org, processDefinitionKey, taskDefinitionKey) => dispatch => {
  dispatch(getTaskListRequest());

  const config = {
    params: {
      processDefinitionKey,
      taskDefinitionKey,
    },
  };

  return axios
    .get(`/api/0/organizations/${org.slug}/tasks/`, config)
    .then(res => dispatch(getTaskListSuccess(res.data)))
    .catch(err => dispatch(getTaskListFailure(err)));
};

////// Selection in a list of Task
export const TOGGLE_SELECT_TASK = 'TOGGLE_SELECT_TASK';
export const toggleSelectTask = id => {
  return {
    type: TOGGLE_SELECT_TASK,
    id,
  };
};

export const TOGGLE_SELECT_PAGE_OF_TASK = 'TOGGLE_SELECT_PAGE_OF_TASK';
export const toggleSelectPageOfTask = doSelect => {
  return {
    type: TOGGLE_SELECT_PAGE_OF_TASK,
    doSelect,
  };
};

////// Fetch a single Task
export const GET_TASK_REQUEST = 'GET_TASK_REQUEST';
export const getTaskRequest = () => {
  return {
    type: GET_TASK_REQUEST,
  };
};

export const GET_TASK_SUCCESS = 'GET_TASK_SUCCESS';
export const getTaskSuccess = entry => {
  return {
    type: GET_TASK_SUCCESS,
    entry,
  };
};

export const GET_TASK_FAILURE = 'GET_TASK_FAILURE';
export const getTaskFailure = err => ({
  type: GET_TASK_FAILURE,
  message: err,
});

export const getTask = id => dispatch => {
  dispatch(getTaskRequest());

  const params = {};
  return axios
    .get(`/api/0/tasks/${id}`, {params})
    .then(res => dispatch(getTaskSuccess(res.data)))
    .catch(err => dispatch(getTaskFailure(err)));
};

// Default dispatchToProps mapping for all actions created here, 1-1 mapping for all params
export const mapTaskDispatchToProps = dispatch => ({
  getTask: id => dispatch(getTask(id)),
  getTaskList: (org, processDefinitionKey, taskDefinitionKey) =>
    dispatch(getTaskList(org, processDefinitionKey, taskDefinitionKey)),
});
