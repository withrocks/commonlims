import {resource} from './shared';
import {RESOURCE_NAME} from '../actions/task';

export const initialState = {
  ...resource.initialState,
};

const task = resource.createReducer(RESOURCE_NAME, initialState);
export default task;
