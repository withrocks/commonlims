import substanceSearchEntry, {
  initialState,
} from 'app/redux/reducers/substanceSearchEntry';

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
    global_id: 'Substance-' + id,
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
  ret.properties = props.map((x) => ({[x]: SubstanceProperty(x)}));
  return ret;
}

export function SubstanceSearchEntry(groupBy, id) {
  if (groupBy === 'substance') {
    // This is the same as grouping by nothing, so we get a flat list of substances
    // (with an added view state)
    return Substance(id, ['comment', 'flammability', 'sample_type']);
  }
  throw Error('Unknown groupBy: ' + groupBy);
}

function TempEntry(groupBy, id) {
  return {
    id,
    name: groupBy + id,
  };
}

function ListViewEntryFromReducer(groupBy, id, isGroupHeader) {
  let entry = null;
  let entity = null;
  if (!isGroupHeader) {
    entity = SubstanceSearchEntry(groupBy, id);
  } else {
    entity = TempEntry(groupBy, id);
  }
  entry = {
    isGroupHeader,
    entity,
  };
  return entry;
}

export function ListViewEntriesFromReducer(count, groupBy) {
  const ret = [];
  const isGroupHeader = groupBy !== 'substance';
  for (let i = 0; i < count; i++) {
    ret.push(ListViewEntryFromReducer(groupBy, i + 1, isGroupHeader));
  }
  return ret;
}

export function SubstanceSearchEntries(count, groupBy) {
  const ret = [];
  for (let i = 0; i < count; i++) {
    ret.push(SubstanceSearchEntry(groupBy, i + 1));
  }
  return ret;
}

export function SubstanceSearchEntriesPageState(pageSize, groupBy) {
  // NOTE: This stub uses the state management to build a page in the expected state
  // Returns the entire expected state a full page mocked objects after one fetches one page of data
  const mockResponseNoGroup = TestStubs.SubstanceSearchEntries(pageSize, groupBy);
  const nextState = substanceSearchEntry(initialState, {
    type: 'SUBSTANCE_SEARCH_ENTRIES_GET_SUCCESS',
    fetchedEntities: mockResponseNoGroup,
    groupBy,
  });
  return nextState;
}
