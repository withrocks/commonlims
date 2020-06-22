import React from 'react';
import ListView from 'app/components/listView.jsx';
import {shallow} from 'enzyme';
import {Set} from 'immutable';

describe('instantiate listview', function () {
  const oneSample = {
    dataById: {
      1: {
        id: 1,
        name: 'mysample',
        location: {
          container: {
            name: 'mycontainer',
          },
        },
        properties: {
          sample_type: {
            value: 'Zombie brain',
          },
        },
      },
    },
    visibleIds: [1],
  };

  const oneSampleType = {
    dataById: {
      1: {
        id: 1,
        name: 'Zombie brain',
        isGroupHeader: true,
      },
    },
    visibleIds: [1],
  };

  const headers = [
    {
      Header: 'Sample name',
      id: 'name',
      accessor: 'name',
      aggregate: (vals) => '',
    },
    {
      Header: 'Container',
      id: 'container',
      accessor: (d) =>
        d.isGroupHeader ? null : d.location ? d.location.container.name : '<No location>',
    },
    {
      Header: 'Sample Type',
      id: 'sample_type',
      accessor: (d) =>
        d.isGroupHeader
          ? null
          : d.properties.sample_type
          ? d.properties.sample_type.value
          : null,
    },
  ];

  function renderListView(args) {
    const defaultProps = {
      columns: headers,
      errorMessage: '',
      loading: false,
      canSelect: false,
      allVisibleSelected: false,
      toggleAll: jest.fn(),
      toggleSingle: jest.fn(),
      visibleIds: [],
      selectedIds: new Set(),
      dataById: {},
      listActionBar: {},
    };
    const props = {...defaultProps, ...args};
    return shallow(<ListView {...props} />);
  }
  it('listView according to snapshot', () => {
    const wrapper = renderListView({...oneSampleType});
    expect(wrapper.instance()).toMatchSnapshot();
  });

  function fetchElement(wrapper, index) {
    return wrapper.find('td').at(index).text();
  }

  it('column entries ok for 1 sample', () => {
    const wrapper = renderListView({...oneSample});
    const notick = fetchElement(wrapper, 0);
    expect(notick).toBe('');
    const sampleName = fetchElement(wrapper, 1);
    expect(sampleName).toBe('mysample');
    const location = fetchElement(wrapper, 2);
    expect(location).toBe('mycontainer');
    const sampleType = fetchElement(wrapper, 3);
    expect(sampleType).toBe('Zombie brain');
  });

  it('column entries ok for 1 group header', () => {
    const wrapper = renderListView({...oneSampleType});
    const tick = fetchElement(wrapper, 0);
    expect(tick).toBe('<CaretRight />');
    const sampleTypeName = fetchElement(wrapper, 1);
    expect(sampleTypeName).toBe('Zombie brain');
    const location = fetchElement(wrapper, 2);
    expect(location).toBe('');
    const sampleType = fetchElement(wrapper, 3);
    expect(sampleType).toBe('');
  });
});
