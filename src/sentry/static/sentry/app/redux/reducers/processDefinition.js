import {resource} from './shared';
import {RESOURCE_NAME} from '../actions/processDefinition';

export const initialState = {
  ...resource.initialState,
};

const processDefinition = resource.createReducer(RESOURCE_NAME, initialState);
export default processDefinition;
