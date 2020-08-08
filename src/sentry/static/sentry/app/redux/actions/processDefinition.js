import axios from 'axios';
import {makeResourceActions} from './shared';

export const RESOURCE_NAME = 'PROCESS_DEFINITION';

////// List of ProcessDefinition
export const processDefinitionActions = makeResourceActions(
  RESOURCE_NAME,
  '/api/0/process-definitions/'
);

////// Selection in a list of ProcessDefinition
export const TOGGLE_SELECT_PROCESS_DEFINITION = 'TOGGLE_SELECT_PROCESS_DEFINITION';
export const toggleSelectProcessDefinition = (id) => {
  return {
    type: TOGGLE_SELECT_PROCESS_DEFINITION,
    id,
  };
};

export const TOGGLE_SELECT_PAGE_OF_PROCESS_DEFINITION =
  'TOGGLE_SELECT_PAGE_OF_PROCESS_DEFINITION';
export const toggleSelectPageOfProcessDefinition = (doSelect) => {
  return {
    type: TOGGLE_SELECT_PAGE_OF_PROCESS_DEFINITION,
    doSelect,
  };
};

////// Fetch a single ProcessDefinition
export const GET_PROCESS_DEFINITION_REQUEST = 'GET_PROCESS_DEFINITION_REQUEST';
export const getProcessDefinitionRequest = () => {
  return {
    type: GET_PROCESS_DEFINITION_REQUEST,
  };
};

export const GET_PROCESS_DEFINITION_SUCCESS = 'GET_PROCESS_DEFINITION_SUCCESS';
export const getProcessDefinitionSuccess = (entry) => {
  return {
    type: GET_PROCESS_DEFINITION_SUCCESS,
    entry,
  };
};

export const GET_PROCESS_DEFINITION_FAILURE = 'GET_PROCESS_DEFINITION_FAILURE';
export const getProcessDefinitionFailure = (err) => ({
  type: GET_PROCESS_DEFINITION_FAILURE,
  message: err,
});

export const getProcessDefinition = (id) => (dispatch) => {
  dispatch(getProcessDefinitionRequest());

  const params = {};
  return axios
    .get(`/api/0/process-definitions/${id}`, {params})
    .then((res) => dispatch(getProcessDefinitionSuccess(res.data)))
    .catch((err) => dispatch(getProcessDefinitionFailure(err)));
};
