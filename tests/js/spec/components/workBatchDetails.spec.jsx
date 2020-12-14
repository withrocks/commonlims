import React from 'react';
import {resource} from 'app/redux/reducers/shared';
import {getUpdatedWorkBatch} from 'app/views/workBatchDetailsWaitingToBeMerged/workbatchDetails';

describe('workbatch details', () => {
  it('should merge updated fields with original workbatch', () => {
    // Arrange
    const originalWorkbatch = {
      id: 1000,
      properties: {
        property1: {
          name: 'property1',
          value: 'orig value',
        },
        property2: {
          name: 'property2',
          value: 'orig value',
        },
      },
    };
    const initialState = {...resource.initialState};
    const workBatchDetailsEntry = {
      ...initialState,
      detailsId: 1000,
      byIds: {
        ...initialState.byIds,
        1000: {
          ...originalWorkbatch,
        },
      },
    };
    const currentFieldValues = {
      property1: 'new value',
      property3: 'new value 3',
    };

    // Act
    const updatedWorkBatch = getUpdatedWorkBatch(
      workBatchDetailsEntry,
      currentFieldValues
    );

    // Assert
    const expectedMergedWorkbatch = {
      id: 1000,
      properties: {
        property1: {
          name: 'property1',
          value: 'new value',
        },
        property2: {
          name: 'property2',
          value: 'orig value',
        },
        property3: {
          name: 'property3',
          value: 'new value 3',
        },
      },
    };
    expect(updatedWorkBatch).toEqual(expectedMergedWorkbatch);
  });
});