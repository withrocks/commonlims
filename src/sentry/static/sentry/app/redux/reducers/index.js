import {combineReducers} from 'redux';

import process from './process';
import processDefinition from './processDefinition';
import savedSearch from './savedSearch';
import substanceSearchEntry from './substanceSearchEntry';
import tag from './tag';
import task from './task';
import taskDefinition from './taskDefinition';
import workBatch from './workBatch';
import projectSearchEntry from './projectSearchEntry';

export default combineReducers({
  process,
  processDefinition,
  savedSearch,
  substanceSearchEntry,
  tag,
  task,
  taskDefinition,
  workBatch,
  projectSearchEntry,
});
