// import axios from 'axios';
// import {Client} from 'app/api';
import {makeActionCreator} from 'app/redux/actions/shared';

export const WORK_BATCH_DETAILS_GET_REQUEST = 'WORK_BATCH_DETAILS_GET_REQUEST';
export const getWorkBatchDetailsRequest = () => {
  return {
    type: WORK_BATCH_DETAILS_GET_REQUEST,
  };
};

export const WORK_BATCH_DETAILS_GET_SUCCESS = 'WORK_BATCH_DETAILS_GET_SUCCESS';
export const getWorkBatchDetailsSuccess = (workBatch) => {
  return {
    type: WORK_BATCH_DETAILS_GET_SUCCESS,
    workBatch,
  };
};

export const WORK_BATCH_DETAILS_GET_FAILURE = 'WORK_BATCH_DETAILS_GET_FAILURE';
export const getWorkBatchDetailsFailure = (err) => ({
  type: WORK_BATCH_DETAILS_GET_FAILURE,
  message: err,
});

export const CREATE_WORK_BATCH_TRANSITION_REQUEST =
  'CREATE_WORK_BATCH_TRANSITION_REQUEST';
export const createWorkBatchTransitionRequest = makeActionCreator(
  CREATE_WORK_BATCH_TRANSITION_REQUEST,
  'workBatch',
  'entry'
);

export const CREATE_WORK_BATCH_TRANSITION_SUCCESS =
  'CREATE_WORK_BATCH_TRANSITION_SUCCESS';
export const createWorkBatchTransitionSuccess = makeActionCreator(
  CREATE_WORK_BATCH_TRANSITION_SUCCESS,
  'workBatch',
  'entry'
);

export const CREATE_WORK_BATCH_TRANSITION_FAILURE =
  'CREATE_WORK_BATCH_TRANSITION_FAILURE';
export const createWorkBatchTransitionFailure = makeActionCreator(
  CREATE_WORK_BATCH_TRANSITION_FAILURE,
  'statusCode',
  'message'
);

function sleep(time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}

// Creates a transition in the backend that's related to this workbatch. The transition
// will be marked as inProgress, so it can be shown directly to the user.
export const createWorkBatchTransition = (workBatch, entry) => (dispatch) => {
  dispatch(createWorkBatchTransitionRequest(workBatch, entry));

  sleep(1000).then(() => {
    dispatch(createWorkBatchTransitionSuccess(workBatch, entry));
  });

  // TODO: Execute POST on /workBatches/1/transitions/
};

export const removeWorkBatchTransition = (workBatch) => (dispatch) => {
  dispatch(getWorkBatchDetailsRequest());

  // TODO: Execute DELETE on /workBatches/1/transitions/, which soft-deletes the transition
};

export const getWorkBatchDetails = (org, id) => (dispatch) => {
  dispatch(getWorkBatchDetailsRequest());
  // A) Fetch the work batch itself and B) fetch the setting for it if we don't already have it
  // TODO: for that kind of thing to work, we need to join the reducers!

  const data = {
    id: 22,
    name: 'Fragment analyzer', // TODO: backend must set this when creating it
    // TODO: Not included in backend yet
    processDefinitionKey: 'clims.plugins.demo.dnaseq.workflows.sequence.SequenceSimple',
    handler: '', // TODO: This we can remove
    extra_fields: '', // TODO: This we can remove
    created_at: '2020-02-22T17:06:11.717759Z',
    updated_at: '2020-02-22T17:06:11.717776Z',
    num_comments: 0,
    status: 0,
    organization: 1,
    files: [
      {
        sha1: 'ea40a664346c0cb7d4326830d76b8ef468a512d7',
        name: '108620_190321_FA_Sample_List.txt',
        dateCreated: '2019-03-08T14:18:01.371Z',
        headers: {
          'Content-Type': 'application/octet-stream',
          Description: 'Sample list',
        },
        id: '30',
        size: 7566,
      },
      {
        sha1: 'ea40a664346c0cb7d4326830d76b8ef468a512d7',
        name: 'quality.csv',
        dateCreated: '2019-03-06T14:32:04.056Z',
        headers: {
          'Content-Type': 'application/octet-stream',
          Description: 'Quality table',
        },
        id: '20',
        size: 7566,
      },
      {
        sha1: 'ea40a664346c0cb7d4326830d76b8ef468a512d7',
        name: 'PDF report',
        dateCreated: '2019-03-06T14:32:04.056Z',
        headers: {
          'Content-Type': 'application/octet-stream',
          Description: 'PDF report from the robot',
        },
        id: '20',
        size: 7566,
      },
      {
        sha1: 'ea40a664346c0cb7d4326830d76b8ef468a512d7',
        name: 'file.bmf',
        dateCreated: '2019-03-06T14:33:16.353Z',
        headers: {
          'Content-Type': 'application/octet-stream',
          Description: 'Robot file (bmf)',
        },
        id: '24',
        size: 7566,
      },
      {
        sha1: 'ea40a664346c0cb7d4326830d76b8ef468a512d7',
        name: 'raw.zip',
        dateCreated: '2019-03-06T14:33:33.306Z',
        headers: {
          'Content-Type': 'application/octet-stream',
          Description: 'Raw data from the robot',
        },
        id: '26',
        size: 7566,
      },
    ],

    subtasks: [{description: 'first do this'}, {description: 'then do that'}],

    // Transitions map from a substance in a container to a substance in a container
    // NEW LOOK (need to support substances too)
    transitions: [
      // {
      //   containers: [], // In Common LIMS, containers can be transitioned too (e.g. between freezers)
      //   substances: [
      //     // Can be either "analyte" (creates a child) or "move" (just moves)
      //     {source: 1, target: 3, type: 'analyte'},
      //   ],
      // },
    ],
    transitions: [
      // {
      //   sourceLocation: {containerId: 1, column: 1, row: 1},
      //   sourceSampleId: 1,
      //   targetLocation: {containerId: 3, column: 0, row: 0},
      //   targetSampleId: null,
      // },
      // {
      //   sourceLocation: {containerId: 1, column: 1, row: 1},
      //   sourceSampleId: 1,
      //   targetLocation: {containerId: 3, column: 1, row: 1},
      //   targetSampleId: null,
      // },
      // {
      //   sourceLocation: {containerId: 1, column: 1, row: 1},
      //   sourceSampleId: 1,
      //   targetLocation: {containerId: 3, column: 2, row: 2},
      //   targetSampleId: null,
      // },
      // {
      //   sourceLocation: {containerId: 1, column: 1, row: 1},
      //   sourceSampleId: 1,
      //   targetLocation: {containerId: 3, column: 3, row: 3},
      //   targetSampleId: null,
      // },
      // {
      //   sourceLocation: {containerId: 1, column: 1, row: 1},
      //   sourceSampleId: 1,
      //   targetLocation: {containerId: 3, column: 4, row: 4},
      //   targetSampleId: null,
      // },
      // {
      //   sourceLocation: {containerId: 1, column: 1, row: 1},
      //   sourceSampleId: 1,
      //   targetLocation: {containerId: 3, column: 5, row: 3},
      //   targetSampleId: null,
      // },
      // {
      //   sourceLocation: {containerId: 1, column: 1, row: 1},
      //   sourceSampleId: 1,
      //   targetLocation: {containerId: 3, column: 6, row: 2},
      //   targetSampleId: null,
      // },
      // {
      //   sourceLocation: {containerId: 1, column: 1, row: 1},
      //   sourceSampleId: 1,
      //   targetLocation: {containerId: 3, column: 7, row: 1},
      //   targetSampleId: null,
      // },
      // {
      //   sourceLocation: {containerId: 1, column: 1, row: 1},
      //   sourceSampleId: 1,
      //   targetLocation: {containerId: 3, column: 8, row: 0},
      //   targetSampleId: null,
      // },
      // {
      //   sourceLocation: {containerId: 1, column: 1, row: 1},
      //   sourceSampleId: 1,
      //   targetLocation: {containerId: 3, column: 9, row: 1},
      //   targetSampleId: null,
      // },
      // {
      //   sourceLocation: {containerId: 1, column: 1, row: 1},
      //   sourceSampleId: 1,
      //   targetLocation: {containerId: 3, column: 10, row: 2},
      //   targetSampleId: null,
      // },
      // {
      //   sourceLocation: {containerId: 1, column: 1, row: 1},
      //   sourceSampleId: 1,
      //   targetLocation: {containerId: 3, column: 11, row: 3},
      //   targetSampleId: null,
      // },
      // {
      //   sourceLocation: {containerId: 1, column: 1, row: 1},
      //   sourceSampleId: 1,
      //   targetLocation: {containerId: 3, column: 10, row: 4},
      //   targetSampleId: null,
      // },
    ],

    source: {
      substances: [
        {
          id: 1,
          name: 'S1',
          location: {
            containerId: 1,
            row: 0,
            col: 0,
          },
        },
        {
          id: 3,
          name: 'S3',
          location: {
            containerId: 3,
            row: 0,
            col: 0,
          },
        },
      ],
      containers: [
        {
          id: 1,
          name: 'C1',
          dimensions: {rows: 8, cols: 12},
          typeName: '96 well plate',
        },
        {
          id: 2,
          name: 'C2',
          dimensions: {rows: 8, cols: 12},
          typeName: '96 well plate',
        },
      ],
    },
    target: {
      substances: [],
      containers: [
        {
          id: 3,
          name: 'C3',
          dimensions: {rows: 8, cols: 12},
          typeName: '96 well plate',
        },
      ],
    },

    // TODO: Just an ID of a workbatch view
    tabs: [
      {
        title: 'Move samples',
        type: 'Transition',
      },
      {
        title: 'Files',
        type: 'Files',
      },
    ],
  };

  dispatch(getWorkBatchDetailsSuccess(data));

  // return axios
  //   .get(`/api/0/organizations/${org}/work-batches/${id}`)
  //   .then(res => dispatch(workBatchDetailsGetSuccess(res.data)))
  //   .catch(err => dispatch(workBatchDetailsGetFailure(err)));
};
