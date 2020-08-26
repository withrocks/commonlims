// import {SampleLocation} from 'app/components/sampleTransitioner/sampleLocation';
// import {Sample} from 'app/components/sampleTransitioner/sample';
import {
  WORK_BATCH_DETAILS_GET_REQUEST,
  WORK_BATCH_DETAILS_GET_SUCCESS,
  WORK_BATCH_DETAILS_GET_FAILURE,
  CREATE_WORK_BATCH_TRANSITION,
} from '../actions/workBatchDetails';

const initialState = {
  loading: false,
  errorMessage: null,
  workBatch: null,
};

// function mapSubstanceToJsType(substance) {
//   const {containerId, row, col} = substance.location;
//   const location = new SampleLocation(containerId, row, col); // TODO: rename sample=> substance
//   return new Sample(substance.id, substance.name, location);
// }

// // Locally, we work with an object that's a bit smarter than the json returned (implements
// // equality checks etc.)
// function mapWorkbatchToJsType(workBatch) {
//   workBatch.source.substances = workBatch.source.substances.map((s) => mapSubstanceToJsType(s));
//   workBatch.target.substances = workBatch.target.substances.map((s) => mapSubstanceToJsType(s));
//   return workBatch;
// }

const workBatchDetails = (state = initialState, action) => {
  switch (action.type) {
    case WORK_BATCH_DETAILS_GET_REQUEST:
      return {
        ...state,
        errorMessage: null,
        loading: true,
      };
    case WORK_BATCH_DETAILS_GET_SUCCESS: {
      // const workBatch = mapWorkbatchToJsType(action.workBatch);

      return {
        ...state,
        errorMessage: null,
        loading: false,
        workBatch: action.workBatch,
      };
    }
    case WORK_BATCH_DETAILS_GET_FAILURE: {
      return {
        ...state,
        errorMessage: action.message,
        loading: false,
      };
    }
    case CREATE_WORK_BATCH_TRANSITION: {
      return {
        ...state,
        workBatch: {
          ...state.workBatch,
          transitions: [action.item],
        },
      };
    }
    default:
      return state;
  }
};

export default workBatchDetails;
