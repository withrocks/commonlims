import substance, {initialState} from 'app/redux/reducers/substance';

export function SubstanceProperty(id) {
  return {
    id,
    name: id,
    display_name: id,
    value: id,
  };
}

export function Substance(id, props) {
  // TODO: Use javascript conventions with the names in the data contract (camel case)
  const ret = {
    id,
    version: 1,
    name: 'sample-' + id,
    type_full_name: 'clims.services.substance.SubstanceBase',
    days_waiting: 56,
    position: {
      index: 'A:1',
      container: {
        name: 'cont1',
      },
    },
    // This data is added by our redux code (not from the server)
    viewState: {
      selected: false,
    },
  };
  ret.properties = props.map(x => ({[x]: SubstanceProperty(x)}));
  return ret;
}

export function SubstanceDUNNO(groupBy, id) {
  if (groupBy === 'sample') {
    // This is the same as grouping by nothing, so we get a flat list of substances
    // (with an added view state)
    return Substance(id, ['comment', 'flammability', 'sample_type']);
  }
  throw Error('Unknown groupBy: ' + groupBy);
}

function GroupedEntryFromReducer(groupBy, id) {
  return {
    id,
    name: groupBy + id,
  };
}

function SubstanceEntryFromReducer(groupBy, id, isGroupHeader) {
  let entry = null;
  if (!isGroupHeader) {
    entry = Substance(groupBy, id);
  } else {
    entry = GroupedEntryFromReducer(groupBy, id);
  }
  entry.isGroupHeader = isGroupHeader;
  return entry;
}

export function SubstanceEntriesFromReducer(count, groupBy) {
  const ret = [];
  const isGroupHeader = groupBy !== 'sample';
  for (let i = 0; i < count; i++) {
    ret.push(SubstanceEntryFromReducer(groupBy, i + 1, isGroupHeader));
  }
  return ret;
}

export function SubstanceSearchEntries(count, groupBy) {
  const ret = [];
  for (let i = 0; i < count; i++) {
    ret.push(Substance(groupBy, i + 1));
  }
  return ret;
}

export function SubstanceSearchEntriesPageState(pageSize, groupBy) {
  // NOTE: This stub uses the state management to build a page in the expected state
  // Returns the entire expected state a full page mocked objects after one fetches one page of data
  const mockResponseNoGroup = TestStubs.SubstanceSearchEntries(2, groupBy);

  const nextState = substance(initialState, {
    type: 'SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS',
    substanceSearchEntries: mockResponseNoGroup,
  });
  return nextState;
}
