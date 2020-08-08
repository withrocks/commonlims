import {resource} from './shared';
import {RESOURCE_NAME} from '../actions/taskDefinition.js';

export const initialState = {
  ...resource.initialState,
};

const taskDefinition = resource.createReducer(RESOURCE_NAME, initialState);
export default taskDefinition;
