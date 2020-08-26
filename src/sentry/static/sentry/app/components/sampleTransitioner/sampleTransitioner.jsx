import React from 'react';
import PropTypes from 'prop-types';
import SampleContainerStack from 'app/components/sampleTransitioner/sampleContainerStack';
import {SampleLocation} from 'app/components/sampleTransitioner/sampleLocation';
import {SampleTransition} from 'app/components/sampleTransitioner/sampleTransition';
import {Sample} from 'app/components/sampleTransitioner/sample';

// TODO: Handle more than one by laying them down_first or right_first
// TODO: Implement shift and ctrl select
//
// TODO: Allow n..n rather than just 1..n. That would enable pooling
// TODO: losing focus on the table should cancel all highlights
// TODO: Be able to switch the container view to a list of samples that can be transitioned
// TODO: Add and remove target containers
// TODO: Allow moving within the same plate
// TODO: Auto-save user's changes in each tab
// TODO: A bunch of mapping code here that could be simplified by synching apis
//
// TODO in transition:
//   [x] Rename container after placing samples

class SampleTransitioner extends React.Component {
  constructor(props) {
    super(props);

    const {workBatch} = props;

    this.state = {
      loading: false,
      error: false,
      activeSampleTransition: null,
      transitionTargetLocationsOfHoveredSample: [],
    };
  }

  setActiveSampleTransition(sampleTransition) {
    this.setState({activeSampleTransition: sampleTransition});
  }

  getActiveSampleTransition() {
    return this.state.activeSampleTransition;
  }

  completeActiveSampleTransition() {
    // TODO: should we de-dupe sample transitions here,
    // or leave that to the API?
    console.log(this.props);
    const {transitions} = this.props.workBatch;
    const activeSampleTransition = this.getActiveSampleTransition();

    if (activeSampleTransition.isComplete()) {
      console.log('FIRING EVENT', activeSampleTransition);
      this.props.createWorkBatchTransition(this.props.workBatch, activeSampleTransition);
      // This is a hack! TODO: We should invoke an action to update the state.
      // const updatedSampleTransitions = sampleTransitions.concat(activeSampleTransition);
      //   console.log(updatedSampleTransitions);
      //throw ex;
      return true;
    } else {
      return false;
    }
  }

  onSourceWellClicked(sampleLocation, containsSampleId) {
    console.log('>>', sampleLocation, containsSampleId);
    // If an empty well was clicked, clear current transition
    if (!containsSampleId) {
      this.setActiveSampleTransition(null);
    }

    // Otherwise reset the current sample transition
    if (sampleLocation.valid()) {
      this.setActiveSampleTransition(
        new SampleTransition(sampleLocation, containsSampleId)
      );
    }
  }

  onTargetWellClicked(sampleLocation) {
    console.log('CLICKING TARGET', sampleLocation);
    const activeSampleTransition = this.getActiveSampleTransition();
    console.log('ACTIVE TRANSITION', activeSampleTransition);
    if (!activeSampleTransition || !activeSampleTransition.hasValidSource()) {
      console.log('NOT VALID SOURCE');
      return;
    }

    // If there is a valid source, create the target,
    // save the transition and clear current transition object.
    const targetSet = activeSampleTransition.setTarget(sampleLocation);
    if (targetSet) {
      const ok = this.completeActiveSampleTransition();
      if (ok) {
        this.setActiveSampleTransition(null);
      }
    }
  }

  onSourceWellMouseOver(sampleLocation, containsSampleId) {
    //const {sampleTransitions} = this.state;
    const sampleTransitions = this.props.workBatch.transitions;

    // If an empty well was hovered, ignore
    if (!containsSampleId || !sampleLocation.valid()) {
      return;
    }

    // Find all transitions for this well and highlight them.
    const transitionTargetLocationsOfHoveredSample = sampleTransitions
      .filter((t) => t.sourceLocation.equals(sampleLocation))
      .map((f) => f.targetLocation);
    this.setState({transitionTargetLocationsOfHoveredSample});
  }

  onMouseOut() {
    this.setState({transitionTargetLocationsOfHoveredSample: []});
  }

  // For now we assume all samples fetched are mapped to source containers.
  // TODO: These could potentially be mapped to source OR target containers.
  // (Perhaps transitions have already been created and the result samples are in the target containers)
  render() {
    // TODO: only pass the transitions that are relevant to each container.
    const {transitionTargetLocationsOfHoveredSample, activeSampleTransition} = this.state;

    const sampleTransitions = this.props.workBatch.transitions;

    let activeSampleTransitionSourceLocation;
    if (activeSampleTransition) {
      activeSampleTransitionSourceLocation = activeSampleTransition.getSource();
    }
    const {workBatch} = this.props;
    if (!workBatch) {
      return <b>bold</b>;
    }

    // TODO: we should pass samples to the target container stack as well,
    // since we may be rendering this after fetching previously created transitions
    // from the api.
    return (
      <div className="sample-transitioner">
        <div className="row">
          <div className="col-md-6">
            <SampleContainerStack
              title="Source containers"
              canAdd={false}
              canRemove={false}
              containers={workBatch.source.containers}
              onWellClicked={this.onSourceWellClicked.bind(this)}
              onWellMouseOver={this.onSourceWellMouseOver.bind(this)}
              source={true}
              substances={workBatch.source.substances}
              onMouseOut={this.onMouseOut.bind(this)}
              activeTransitionSourceLocation={activeSampleTransitionSourceLocation}
              transitionSourceLocations={sampleTransitions.map((st) => st.sourceLocation)}
            />
          </div>
          <div className="col-md-6">
            <SampleContainerStack
              title="Target containers"
              canAdd={true}
              canRemove={true}
              containers={workBatch.target.containers}
              onWellClicked={this.onTargetWellClicked.bind(this)}
              source={false}
              substances={workBatch.target.substances}
              onMouseOut={this.onMouseOut.bind(this)}
              transitionTargetLocationsOfHoveredSample={
                transitionTargetLocationsOfHoveredSample
              }
              transitionTargetLocations={sampleTransitions.map((st) => st.targetLocation)}
            />
          </div>
        </div>
        {JSON.stringify(sampleTransitions)}
      </div>
    );
  }
}

SampleTransitioner.propTypes = {
  // TODO: specify individual props instead of entire workBatch
  workBatch: PropTypes.object,
};

export default SampleTransitioner;
