import PropTypes from 'prop-types';
import React from 'react';
import InlineSvg from 'app/components/inlineSvg';
import {SampleLocation} from 'app/components/sampleTransitioner/sampleLocation';

class SampleWell extends React.Component {
  getWellIcon() {
    const {containsSampleId, isTransitionSource, isTransitionTarget} = this.props;

    if (isTransitionTarget) {
      return 'icon-well-added';
    }

    if (isTransitionSource) {
      return 'icon-well-transitioned';
    }

    if (containsSampleId) {
      return 'icon-well-full';
    }

    return 'icon-well-empty';
  }

  getWellClassName() {
    const {
      isActiveTransitionSource,
      inHoveredRowOrColumn,
      isTransitionTargetOfHoveredSample,
    } = this.props;

    let className = 'sample-well';

    if (isActiveTransitionSource) {
      className = `${className} selected`;
    } else if (isTransitionTargetOfHoveredSample) {
      className = `${className} highlighted`;
    }

    return className;
  }

  handleMouseOver() {
    const {location} = this.props;
    this.props.onMouseOver(location);
  }

  handleClick() {
    const {location} = this.props;
    this.props.onClick(location);
  }

  render() {
    return (
      <td
        className={this.getWellClassName()}
        onMouseOver={this.handleMouseOver.bind(this)}
      >
        <InlineSvg
          width="27px"
          height="27px"
          src={this.getWellIcon()}
          onClick={this.handleClick.bind(this)}
        />
      </td>
    );
  }
}

SampleWell.propTypes = {
  location: PropTypes.instanceOf(SampleLocation).isRequired,
  onClick: PropTypes.func.isRequired,
  onMouseOver: PropTypes.func.isRequired,
  containsSampleId: PropTypes.number,
  isTransitionSource: PropTypes.bool,
  isTransitionTarget: PropTypes.bool,
  isActiveTransitionSource: PropTypes.bool,
  isTransitionTargetOfHoveredSample: PropTypes.bool,
  inHoveredRowOrColumn: PropTypes.bool,
};

SampleWell.defaultProps = {
  containsSampleId: null,
  isTransitionSource: false,
  isTransitionTarget: false,
  isActiveTransitionSource: false,
  isTransitionTargetOfHoveredSample: false,
  inHoveredRowOrColumn: false,
};

export default SampleWell;
