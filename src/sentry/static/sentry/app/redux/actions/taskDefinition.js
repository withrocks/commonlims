import axios from 'axios';
import {makeResourceActions} from './shared';

export const RESOURCE_NAME = 'TASK_DEFINITION';

export const taskDefinitionActions = makeResourceActions(
  RESOURCE_NAME,
  '/api/0/process-definitions/'
);
