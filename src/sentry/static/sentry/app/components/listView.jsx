import React from 'react';
import styled from 'react-emotion';
import LoadingIndicator from 'app/components/loadingIndicator';
import LoadingError from 'app/components/loadingError';
import {Panel, PanelBody} from 'app/components/panels';
import {CaretDown, CaretRight} from 'app/components/icons';
import PropTypes from 'prop-types';
import Checkbox from 'app/components/checkbox';

const ColumnHeader = styled('div')`
  font-size: 14px;
  text-transform: uppercase;
  font-weight: bold;
  color: ${p => p.theme.gray3};
`;

// TODO: Make the headers sticky again
const Styles = styled.div`
  table {
    width: 100%;
    border-spacing: 0;
    background: ${p => p.theme.offWhite};

    th {
      /*position: sticky;
      position: -webkit-sticky;
      top: 0;
      z-index: 10;*/
      padding: 0.5rem;
      border-bottom: 1px solid ${p => p.theme.borderDark};
    }

    td {
      margin: 0;
      padding: 0.5rem;
      border-bottom: 1px solid ${p => p.theme.borderDark};

      position: relative;

      :last-child {
        border-right: 0;
      }
    }

    tr {
      :last-child {
        td {
          border-bottom: 0;
        }
      }
    }
  }
`;

class ListView extends React.Component {
  static propTypes = {
    columns: PropTypes.array.isRequired,
    errorMessage: PropTypes.string,
    loading: PropTypes.bool.isRequired,
    canSelect: PropTypes.bool.isRequired,
    allVisibleSelected: PropTypes.bool.isRequired,
    toggleAll: PropTypes.func.isRequired,
    toggleSingle: PropTypes.func.isRequired,
    visibleIds: PropTypes.array,
    selectedIds: PropTypes.instanceOf(Set),
    dataById: PropTypes.object.isRequired,
    listActionBar: PropTypes.object,
  };

  constructor() {
    super();
    this.state = {
      expandedRows: [],
    };
  }

  handleRowClick(rowId) {
    const currentlyExpandedRows = this.state.expandedRows;
    const isRowExpanded = currentlyExpandedRows.includes(rowId);
    const newExpandedRows = isRowExpanded
      ? currentlyExpandedRows.filter(id => id !== rowId)
      : currentlyExpandedRows.concat(rowId);

    this.setState({expandedRows: newExpandedRows});
  }

  renderRowExpander(rowId) {
    const currentlyExpandedRows = this.state.expandedRows;
    const isRowExpanded = currentlyExpandedRows.includes(rowId);
    if (isRowExpanded) {
      return <CaretDown />;
    } else {
      return <CaretRight />;
    }
  }

  getDisplayCell(entryId, header) {
    const row = this.props.dataById[entryId];

    if (typeof header.accessor === 'function') {
      return header.accessor(row);
    }
    return row[header.accessor];
  }

  isSelected(entryId) {
    return this.props.selectedIds.has(entryId);
  }

  render() {
    if (this.props.loading) {
      return <LoadingIndicator />;
    } else if (this.props.errorMessage) {
      return <LoadingError />;
    }

    return (
      <Panel>
        {this.props.listActionBar}
        <PanelBody>
          <Styles>
            <table>
              <thead>
                <tr>
                  {
                    <th>
                      <div />
                    </th>
                  }
                  {this.props.canSelect && (
                    <th>
                      <Checkbox
                        checked={this.props.allVisibleSelected}
                        onChange={this.props.toggleAll}
                      />
                    </th>
                  )}
                  {this.props.columns.map((x, index) => {
                    return (
                      <th key={'header-index-' + index}>
                        <ColumnHeader>{x.Header}</ColumnHeader>
                      </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody>
                {this.props.visibleIds.map(entryId => {
                  return (
                    <tr key={'parent-' + entryId}>
                      <td>{this.renderRowExpander(entryId)}</td>
                      {this.props.canSelect && (
                        <td>
                          <Checkbox
                            checked={this.isSelected(entryId)}
                            onChange={() => this.props.toggleSingle(entryId, null)}
                          />
                        </td>
                      )}
                      {this.props.columns.map((header, index) => {
                        return (
                          <td key={'parent-cell-' + entryId + '-' + index}>
                            {this.getDisplayCell(entryId, header)}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </Styles>
        </PanelBody>
      </Panel>
    );
  }
}

export default ListView;
