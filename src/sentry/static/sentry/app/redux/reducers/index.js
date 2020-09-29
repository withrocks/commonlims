import {combineReducers} from 'redux';

import process from './process';
import processAssignment from './processAssignment';
import processDefinition from './processDefinition';
import savedSearch from './savedSearch';
import substanceSearchEntry from './substanceSearchEntry';
import tag from './tag';
import workDefinition from './workDefinition';
import workBatch from './workBatch';
import workBatchDetails from './workBatchDetails';
import projectSearchEntry from './projectSearchEntry';
import availableWork from './availableWork';
import availableWorkUnit from './availableWorkUnit';

export default combineReducers({
  process,
  processAssignment,
  processDefinition,
  savedSearch,
  substanceSearchEntry,
  tag,
  workDefinition,
  workBatch,
  workBatchDetails,
  projectSearchEntry,
  availableWork,
  availableWorkUnit,
});
