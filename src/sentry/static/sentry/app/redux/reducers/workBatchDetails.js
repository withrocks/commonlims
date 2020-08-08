import {SampleLocation} from 'app/components/sampleTransitioner/sampleLocation';
import {Sample} from 'app/components/sampleTransitioner/sample';
import {
  WORK_BATCH_DETAILS_GET_REQUEST,
  WORK_BATCH_DETAILS_GET_SUCCESS,
  WORK_BATCH_DETAILS_GET_FAILURE,
} from '../actions/workBatchDetails';

const initialState = {
  loading: false,
  errorMessage: null,
  workBatch: null,
};

function prepareWorkBatchForLocalWork(workBatch) {
  // Maps the contract we get from the API to contain classes that e.g. implement equality checks
  // Also adds
  const sourceSubstances = workBatch.source.substances.map(s => {
    const {containerId, row, col} = s.location;
    const location = new SampleLocation(containerId, row, col); // TODO: rename sample=> substance
    return new Sample(s.id, s.name, location);
  });

  workBatch.source.substances = sourceSubstances;
  return workBatch;
}

const workBatchDetails = (state = initialState, action) => {
  switch (action.type) {
    case WORK_BATCH_DETAILS_GET_REQUEST:
      return {
        ...state,
        errorMessage: null,
        loading: true,
      };
    case WORK_BATCH_DETAILS_GET_SUCCESS: {
      const workBatch = prepareWorkBatchForLocalWork(action.workBatch);

      return {
        ...state,
        errorMessage: null,
        loading: false,
        workBatch,
      };
    }
    case WORK_BATCH_DETAILS_GET_FAILURE: {
      return {
        ...state,
        errorMessage: action.message,
        loading: false,
      };
    }
    default:
      return state;
  }
};

export default workBatchDetails;
