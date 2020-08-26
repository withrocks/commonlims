import PropTypes from 'prop-types';
import React from 'react';
import {Panel, PanelBody} from 'app/components/panels';
import {Sample} from 'app/components/sampleTransitioner/sample';
import SampleContainerStackActions from './actions';
import {SampleContainer, SampleContainerDirectionality} from './sampleContainer';

class SampleContainerStack extends React.Component {
  // A SampleContainerStack allows the user to move between 1..n different containers
  constructor(props) {
    super(props);

    this.state = {
      containerIndex: 0,
      container: this.props.containers[0],
    };
  }

  nextContainer(e) {
    e.preventDefault();
    let containerIndex = this.state.containerIndex + 1;
    if (containerIndex > this.props.containers.length - 1) {
      containerIndex = 0;
    }
    const container = this.props.containers[containerIndex];

    this.setState({containerIndex, container});
  }

  previousContainer(e) {
    e.preventDefault();
    let containerIndex = this.state.containerIndex - 1;
    if (containerIndex < 0) {
      containerIndex = this.props.containers.length - 1;
    }
    const container = this.props.containers[containerIndex];

    this.setState({containerIndex, container});
  }

  onSampleWellClicked(location, sampleId) {
    this.props.onWellClicked(location, sampleId);
  }

  onSampleWellMouseOver(location, sampleId) {
    if (!this.props.onWellMouseOver) {
      return;
    }

    this.props.onWellMouseOver(location, sampleId);
  }

  render() {
    const containerDirectionality = this.props.source
      ? SampleContainerDirectionality.SOURCE
      : SampleContainerDirectionality.TARGET;

    const samples = this.props.substances.filter(
      (s) => s.getLocation().getContainerId() === this.state.container.id
    );

    const {
      transitionSourceLocations,
      transitionTargetLocations,
      transitionTargetLocationsOfHoveredSample,
      activeSampleTransitionSourceLocation,
    } = this.props;

    return (
      <div style={{display: 'inline-block'}}>
        <Panel>
          <SampleContainerStackActions
            canAdd={this.props.canAdd}
            canRemove={this.props.canRemove}
            name={this.state.container.name}
            numContainers={this.props.containers.length}
            containerIndex={this.state.containerIndex + 1}
            source={this.props.source}
            nextContainer={this.nextContainer.bind(this)}
            previousContainer={this.previousContainer.bind(this)}
          />
          <PanelBody>
            <SampleContainer
              containerId={this.state.container.id}
              containerDirectionality={containerDirectionality}
              numColumns={this.state.container.dimensions.cols}
              numRows={this.state.container.dimensions.rows}
              onWellClicked={this.onSampleWellClicked.bind(this)}
              onWellMouseOver={this.onSampleWellMouseOver.bind(this)}
              onMouseOut={this.props.onMouseOut}
              samples={samples}
              transitionTargetLocationsOfHoveredSample={
                transitionTargetLocationsOfHoveredSample
              }
              activeSampleTransitionSourceLocation={activeSampleTransitionSourceLocation}
              transitionSourceLocations={transitionSourceLocations}
              transitionTargetLocations={transitionTargetLocations}
            />
          </PanelBody>
        </Panel>
      </div>
    );
  }
}

SampleContainerStack.propTypes = {
  onWellClicked: PropTypes.func,
  onWellMouseOver: PropTypes.func,
  onMouseOut: PropTypes.func.isRequired,
  canAdd: PropTypes.bool,
  canRemove: PropTypes.bool,
  containers: PropTypes.array,
  source: PropTypes.bool,
  samples: PropTypes.arrayOf(PropTypes.instanceOf(Sample)),
  // TODO: format these properly
  // TODO: consider separate classes for source and target container stacks
  transitionTargetLocationsOfHoveredSample: PropTypes.arrayOf(PropTypes.shape()),
  transitionTargetLocations: PropTypes.arrayOf(PropTypes.shape()),
  transitionSourceLocations: PropTypes.arrayOf(PropTypes.shape()),
  activeSampleTransitionSourceLocation: PropTypes.object,
};

SampleContainerStack.defaultProps = {
  samples: [],
  transitionTargetLocationsOfHoveredSample: [],
  transitionTargetLocations: [],
  transitionSourceLocations: [],
};

SampleContainerStack.displayName = 'SampleContainerStack';

export default SampleContainerStack;
