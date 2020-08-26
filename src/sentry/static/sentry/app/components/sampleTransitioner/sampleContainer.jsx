import PropTypes from 'prop-types';
import React from 'react';
import SampleWell from './sampleWell';
import {SampleLocation} from './sampleLocation';
import {Sample} from './sample';

export const SampleContainerDirectionality = {
  SOURCE: 1,
  TARGET: 2,
};

export class SampleContainer extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      hoverRow: null,
      hoverCol: null,
    };
  }

  isHoveredRowOrColumn(row, col) {
    const {hoverRow, hoverCol} = this.state;
    return hoverRow === row || hoverCol === col;
  }

  getHeaderClassName(row, col) {
    return this.isHoveredRowOrColumn(row, col) ? 'highlighted-background' : '';
  }

  isSourceContainer() {
    const {containerDirectionality} = this.props;
    return containerDirectionality === SampleContainerDirectionality.SOURCE;
  }

  isTargetContainer() {
    const {containerDirectionality} = this.props;
    return containerDirectionality === SampleContainerDirectionality.TARGET;
  }

  isTransitionSource(location) {
    const {transitionSourceLocations} = this.props;
    if (!this.isSourceContainer()) {
      return false;
    }

    return !!transitionSourceLocations.find((tl) => tl.equals(location));
  }

  isActiveTransitionSource(location) {
    const {activeSampleTransitionSourceLocation} = this.props;

    if (!this.isSourceContainer() || !activeSampleTransitionSourceLocation) {
      return false;
    }

    return activeSampleTransitionSourceLocation.equals(location);
  }

  isTransitionTarget(location) {
    const {transitionTargetLocations} = this.props;

    if (!this.isTargetContainer()) {
      return false;
    }

    return !!transitionTargetLocations.find((tl) => tl.equals(location));
  }

  isTransitionTargetOfHoveredSample(location) {
    const {transitionTargetLocationsOfHoveredSample} = this.props;

    if (!this.isTargetContainer()) {
      return false;
    }

    return !!transitionTargetLocationsOfHoveredSample.find((tl) => tl.equals(location));
  }

  onMouseOut() {
    const {onMouseOut} = this.props;

    if (this.state.hoverRow || this.state.hoverCol) {
      this.setState({hoverRow: null, hoverCol: null});
    }

    onMouseOut();
  }

  renderColumnsHeader() {
    const {numColumns} = this.props;
    const keyPrefix = 'thead-th';
    const ths = [<th key={`${keyPrefix}-corner`} />];

    for (let c = 0; c < numColumns; c++) {
      const label = c + 1;
      ths.push(
        <th key={`${keyPrefix}-${c}`} className={this.getHeaderClassName(-1, c)}>
          {label}
        </th>
      );
    }

    return <tr key="thead-tr">{ths}</tr>;
  }

  renderRowHeader(row) {
    const keyPrefix = 'th';
    const label = String.fromCharCode(65 + row);
    return (
      <th key={`${keyPrefix}-${row}`} className={this.getHeaderClassName(row, -1)}>
        {label}
      </th>
    );
  }

  renderSampleWell(row, col, sampleId) {
    const {containerId, onWellClicked, onWellMouseOver} = this.props;

    const handleClick = (location) => {
      onWellClicked(location, sampleId);
    };

    const handleMouseOver = (location) => {
      if (!this.isHoveredRowOrColumn(row, col)) {
        this.setState({hoverRow: row, hoverCol: col});
      }

      onWellMouseOver(location, sampleId);
    };

    const location = new SampleLocation(containerId, row, col);
    const x = this.isTransitionSource(location);

    return (
      <SampleWell
        key={`samplewell-${row}-${col}`}
        location={location}
        onClick={handleClick}
        onMouseOver={handleMouseOver}
        containsSampleId={sampleId}
        isTransitionSource={this.isTransitionSource(location)}
        isTransitionTarget={this.isTransitionTarget(location)}
        isActiveTransitionSource={this.isActiveTransitionSource(location)}
        isTransitionTargetOfHoveredSample={this.isTransitionTargetOfHoveredSample(
          location
        )}
        inHoveredRowOrColumn={this.isHoveredRowOrColumn(row, col)}
      />
    );
  }

  renderRows() {
    const {numColumns, numRows, samples} = this.props;
    const keyPrefix = 'tr';
    const rows = [];

    for (let r = 0; r < numRows; r++) {
      const row = [this.renderRowHeader(r)];
      const rowSamples = samples.filter((s) => s.getLocation().getRow() === r);

      for (let c = 0; c < numColumns; c++) {
        const sample = rowSamples.find((s) => s.getLocation().getColumn() === c);
        const sampleId = sample ? sample.id : null;
        row.push(this.renderSampleWell(r, c, sampleId));
      }

      rows.push(<tr key={`${keyPrefix}-${r}`}>{row}</tr>);
    }
    return rows;
  }

  render() {
    return (
      <table className="sample-container" onMouseOut={this.onMouseOut.bind(this)}>
        <thead>{this.renderColumnsHeader()}</thead>
        <tbody>{this.renderRows()}</tbody>
      </table>
    );
  }
}

SampleContainer.propTypes = {
  containerId: PropTypes.number.isRequired,
  containerDirectionality: PropTypes.number.isRequired,
  numColumns: PropTypes.number.isRequired,
  numRows: PropTypes.number.isRequired,
  onWellClicked: PropTypes.func.isRequired,
  onWellMouseOver: PropTypes.func.isRequired,
  onMouseOut: PropTypes.func.isRequired,
  samples: PropTypes.arrayOf(PropTypes.instanceOf(Sample)),
  transitionSourceLocations: PropTypes.arrayOf(PropTypes.instanceOf(SampleLocation)),
  transitionTargetLocations: PropTypes.arrayOf(PropTypes.instanceOf(SampleLocation)),
  transitionTargetLocationsOfHoveredSample: PropTypes.arrayOf(
    PropTypes.instanceOf(SampleLocation)
  ),
  activeSampleTransitionSourceLocation: PropTypes.instanceOf(SampleLocation),
};

SampleContainer.defaultProps = {
  samples: [],
  transitionSourceLocations: [],
  transitionTargetLocations: [],
  transitionTargetLocationsOfHoveredSample: [],
  activeSampleTransitionSourceLocation: null,
};

SampleContainer.displayName = 'SampleContainer';

export default SampleContainer;
