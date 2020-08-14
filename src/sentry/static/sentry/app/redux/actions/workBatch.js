import {makeResourceActions} from './shared';

export const RESOURCE_NAME = 'WORK_BATCH';

export const workBatchActions = makeResourceActions(
  RESOURCE_NAME,
  '/api/0/organizations/{org}/work-batches/',
  (org, res) => `/${org.slug}/workbatches/${res.workBatch.id}/`
);
