import {makeResourceActions} from './shared';

export const RESOURCE_NAME = 'PROCESS_DEFINITION';

////// List of ProcessDefinition
export const processDefinitionActions = makeResourceActions(
  RESOURCE_NAME,
  '/api/0/process-definitions/'
);
