import {makeResourceActions} from './shared';

export const RESOURCE_NAME = 'TASK';

export const taskActions = makeResourceActions(
  RESOURCE_NAME,
  '/api/0/organizations/{org}/tasks/',
  '/api/0/tasks/{id}/'
);
