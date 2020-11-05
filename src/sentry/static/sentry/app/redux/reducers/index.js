import {combineReducers} from 'redux';

import process from './process';
import processAssignment from './processAssignment';
import processDefinition from './processDefinition';
import savedSearch from './savedSearch';
import substanceSearchEntry from './substanceSearchEntry';
import tag from './tag';
import task from './task';
import taskDefinition from './taskDefinition';
import workBatch from './workBatch';
import workBatchDetails from './workBatchDetails';
import projectSearchEntry from './projectSearchEntry';
import {resource} from './shared';

const sharedInitialState = {
  ...resource.initialState,
};

export const WORK_BATCH_DEFINITION = 'WORK_BATCH_DEFINITION';
export const WORK_BATCH = 'WORK_BATCH';
export const EVENTS = 'EVENTS';

const workBatchDefinitionEntry = resource.createReducer(
  WORK_BATCH_DEFINITION,
  sharedInitialState
);

const workBatchEntry = resource.createReducer(WORK_BATCH, sharedInitialState);

export default combineReducers({
  process,
  processAssignment,
  processDefinition,
  savedSearch,
  substanceSearchEntry,
  tag,
  task,
  taskDefinition,
  workBatch,
  workBatchDetails,
  projectSearchEntry,
  workBatchDefinitionEntry,
  workBatchEntry,
});
