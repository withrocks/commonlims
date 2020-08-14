import {t} from 'app/locale';
import IndicatorStore from 'app/stores/indicatorStore';

import {
  PROCESS_ASSIGN_SELECT_PRESET,
  PROCESS_ASSIGN_SELECT_PROCESS_DEF,
  PROCESS_ASSIGN_SET_VARIABLE,
  PROCESS_ASSIGNMENTS_POST_REQUEST,
  PROCESS_ASSIGNMENTS_POST_SUCCESS,
  PROCESS_ASSIGNMENTS_POST_FAILURE,
  PROCESS_ASSIGNMENTS_SET_EDITING,
} from '../actions/processAssignment';

export const initialState = {
  errorMessage: null,
  processById: {},
  indicatorToken: null,

  // assignment
  assignPresetId: null,
  assignProcessDefinitionId: null,
  assignVariables: {},

  editing: false,
};

const processAssignment = (state = initialState, action) => {
  switch (action.type) {
    case PROCESS_ASSIGN_SELECT_PRESET:
      let assignVariables, assignProcessDefinitionId, assignPreset;
      if (action.preset) {
        assignPreset = action.preset;
        assignVariables = Object.assign({}, action.preset.variables);
        assignProcessDefinitionId = action.preset.processDefinitionId;
      } else {
        assignPreset = null;
        assignVariables = {};
        assignProcessDefinitionId = null;
      }

      return {
        ...state,
        assignPreset,
        assignVariables,
        assignProcessDefinitionId,
        errorMessage: null,
      };
    case PROCESS_ASSIGN_SELECT_PROCESS_DEF:
      return {
        ...state,
        assignProcessDefinitionId: action.processDefinitionId,
        assignVariables: {},
        assignPreset: null,
        errorMessage: null,
      };
    case PROCESS_ASSIGN_SET_VARIABLE: {
      // NOTE: `new` prefix because of scoping issues with using the same name (the linter
      // complains even if this is in its own scope)
      const newAssignVariables = {
        ...state.assignVariables,
        [action.key]: action.value,
      };

      return {
        ...state,
        assignVariables: newAssignVariables,
        assignPreset: null,
        errorMessage: null,
      };
    }
    case PROCESS_ASSIGNMENTS_POST_REQUEST: {
      const indicatorToken = IndicatorStore.add(action.msg);
      return {
        ...state,
        errorMessage: null,
        loading: false,
        saving: true,
        indicatorToken,
      };
    }
    case PROCESS_ASSIGNMENTS_POST_SUCCESS: {
      IndicatorStore.remove(state.indicatorToken);
      const indicatorToken = IndicatorStore.addSuccess(
        t('Successfully assigned to process.')
      );
      return {
        ...state,
        errorMessage: null,
        loading: false,
        saving: false,
        editing: false,
        assignPreset: null,
        assignVariables: {},
        assignProcessDefinitionId: null,
        indicatorToken,
      };
    }
    case PROCESS_ASSIGNMENTS_POST_FAILURE: {
      IndicatorStore.remove(state.indicatorToken);
      return {
        ...state,
        errorMessage: action.message,
        loading: false,
        saving: false,
        indicatorToken: null,
      };
    }
    case PROCESS_ASSIGNMENTS_SET_EDITING: {
      return {
        ...state,
        editing:
          action.editing === null || action.editing === undefined
            ? !state.editing
            : action.editing,
      };
    }
    default:
      return state;
  }
};

export default processAssignment;
