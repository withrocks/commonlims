import {t} from 'app/locale';
import {Client} from 'app/api';
import {substanceSearchEntriesToggleSelectAll} from 'app/redux/actions/substanceSearchEntry';

import {makeActionCreator} from 'app/redux/actions/shared';

// Assigning substances to processes.
// TODO-nomerge: Rename actions to processAssignments
// TODO-nomerge: Use the wizard
export const PROCESS_ASSIGN_SELECT_PRESET = 'PROCESS_ASSIGN_SELECT_PRESET';
export const processAssignSelectPreset = makeActionCreator(
  PROCESS_ASSIGN_SELECT_PRESET,
  'preset'
);

export const PROCESS_ASSIGN_SELECT_PROCESS_DEF = 'PROCESS_ASSIGN_SELECT_PROCESS_DEF';
export const processAssignSelectProcess = makeActionCreator(
  PROCESS_ASSIGN_SELECT_PRESET,
  'processDefinitionId'
);

export const PROCESS_ASSIGN_SET_VARIABLE = 'PROCESS_ASSIGN_SET_VARIABLE';
export const processAssignSetVariable = makeActionCreator(
  PROCESS_ASSIGN_SET_VARIABLE,
  'key',
  'value'
);

// Requested a POST TO `process-assignments`
export const PROCESS_ASSIGNMENTS_POST_REQUEST = 'PROCESS_ASSIGNMENTS_POST_REQUEST';
export const processAssignmentsPostRequest = makeActionCreator(
  PROCESS_ASSIGNMENTS_POST_REQUEST,
  'msg'
);

// Successfully POSTed to `process-assignments`
export const PROCESS_ASSIGNMENTS_POST_SUCCESS = 'PROCESS_ASSIGNMENTS_POST_SUCCESS';
export const processAssignmentsPostSuccess = makeActionCreator(
  PROCESS_ASSIGNMENTS_POST_SUCCESS,
  'response'
);

// Error while POSTing to `process-assignments`
export const PROCESS_ASSIGNMENTS_POST_FAILURE = 'PROCESS_ASSIGNMENTS_POST_FAILURE';
export const processAssignmentsPostFailure = makeActionCreator(
  PROCESS_ASSIGNMENTS_POST_FAILURE,
  'message'
);

export const processAssignmentsPost = (definitionId, variables, entities, org) => (
  dispatch
) => {
  dispatch(processAssignmentsPostRequest(t('Assigning to process...')));
  const api = new Client(); // TODO: use axios (must send same headers as Client does).

  const data = {
    definitionId,
    variables,
    entities,
  };
  api.request(`/api/0/organizations/${org}/process-assignments/`, {
    method: 'POST',
    data,
    success: (res) => {
      dispatch(processAssignmentsPostSuccess(res));
      dispatch(substanceSearchEntriesToggleSelectAll(false));
    },
    error: (err) => {
      dispatch(processAssignmentsPostFailure(err.responseJSON.detail));
    },
  });
};

export const PROCESS_ASSIGNMENTS_SET_EDITING = 'PROCESS_ASSIGNMENTS_SET_EDITING';
export const processAssignmentsSetEditing = makeActionCreator(
  PROCESS_ASSIGNMENTS_SET_EDITING,
  'value'
);
