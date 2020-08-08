import PropTypes from 'prop-types';
import React from 'react';
import createReactClass from 'create-react-class';
import Modal from 'react-bootstrap/lib/Modal';
import {connect} from 'react-redux';
import ClimsTypes from 'app/climsTypes';

import {t} from 'app/locale';
import SelectControl from 'app/components/forms/selectControl';

import JsonForm from 'app/views/settings/components/forms/jsonForm';
import LoadingIndicator from 'app/components/loadingIndicator';
import Link from 'app/components/link';
import Bpmn from 'app/components/bpmn';
import styled from 'react-emotion';
import {sortBy} from 'lodash';
import {getPresetsById} from 'app/redux/selectors/processDefinition';

import {
  processAssignSelectPreset,
  processAssignSelectProcess,
  processAssignSetVariable,
  processAssignmentsPost,
  processAssignmentsSetEditing,
} from 'app/redux/actions/processAssignment';

import {processDefinitionActions} from 'app/redux/actions/processDefinition';

const StyledBpmn = styled(Bpmn)`
  height: 500px;
`;

// TODO: Write tests for this component
// TODO: Change to JS6 class
// TODO-simple: Rename to AssignToProcess for consistency
const AssignToWorkflowButton = createReactClass({
  displayName: 'AssignToWorkflowButton',

  propTypes: {
    disabled: PropTypes.bool,
    style: PropTypes.object,
    tooltip: PropTypes.string,
    buttonTitle: PropTypes.string,
    process: PropTypes.object,
    substanceSearchEntry: PropTypes.object,
    processAssignmentsPost: PropTypes.func,
    getProcessDefinitionList: PropTypes.func,
    processAssignSelectPreset: PropTypes.func.isRequired,
    processAssignSelectProcess: PropTypes.func.isRequired,
    processAssignSetVariable: PropTypes.func.isRequired,
    presetsById: PropTypes.object,

    processDefinition: ClimsTypes.List.isRequired,
    processAssignment: ClimsTypes.ProcessAssignmentStore.isRequired,
    processAssignmentsSetEditing: PropTypes.func,
  },

  getInitialState() {
    return {
      errors: {},
      value: null,
      setProcessVariables: {},
      selectedProcess: null,
      selectedPreset: null,
      variables: {},
      diagramVisible: false,
    };
  },

  UNSAFE_componentWillMount() {
    this.props.getProcessDefinitionList();
  },

  renderDiagram() {
    const xml = '';
    if (xml === '') {
      return null;
    }
    if (this.state.diagramVisible) {
      return (
        <div>
          <Link onClick={() => this.setState({diagramVisible: false})}>Hide diagram</Link>
          <StyledBpmn xml={xml} />
        </div>
      );
    } else {
      return (
        <Link onClick={() => this.setState({diagramVisible: true})}>Show diagram</Link>
      );
    }
  },

  onVariableChange(key, value) {
    const updated = Object.assign({}, this.state.setProcessVariables);
    updated[key] = value;
    this.setState({
      setProcessVariables: updated,
    });
  },

  onToggle() {
    if (this.props.disabled) {
      return;
    }
    this.props.processAssignmentsSetEditing();
  },

  onSubmit(e) {
    e.preventDefault();

    if (this.props.process.assignmentSaving) {
      return;
    }

    // TODO: substances already selected
    this.props.processAssignmentsPost(
      this.props.processAssignment.assignProcessDefinitionId,
      this.props.processAssignment.assignVariables,
      this.props.substanceSearchEntry.selectedIds.toArray(),
      'lab' // TODO: Get from URL
    );
  },

  createFieldsFromDefinition(processDefinition) {
    return processDefinition.fields.map((fieldConfig) => {
      const field = Object.assign({}, fieldConfig);
      field.onChange = (val) => this.props.processAssignSetVariable(field.name, val);
      return field;
    });
  },

  renderSettings() {
    let fields = null;
    const {assignVariables, assignProcessDefinitionId} = this.props.processAssignment;

    if (assignProcessDefinitionId) {
      const assignProcessDefinition = this.props.processDefinition.byIds[
        assignProcessDefinitionId
      ];
      fields = this.createFieldsFromDefinition(assignProcessDefinition);
    } else {
      fields = [];
    }

    for (const field of fields) {
      field.value = assignVariables[field.name];
    }

    return <JsonForm title={t('Settings')} fields={fields} />;
  },

  render() {
    if (this.props.process.processDefinitionLoading) {
      return <LoadingIndicator />;
    }

    const presets = Object.entries(this.props.presetsById).map(entry => {
      return {value: entry[1].id, label: entry[1].name};
    });
    const presetsSorted = sortBy(presets, 'label');

    // TODO: Here we should handle the case where two workflows have the same name (but different
    // namespaces), by showing the full name in that case
    const processDefinitions = Object.entries(
      this.props.processDefinition.byIds
    ).map(entry => {
      const processId = entry[1].id;
      const elements = processId.split('.');
      const processName = elements[elements.length - 1];
      return {value: entry[0], label: processName};
    });

    const {
      assignPreset,
      assignProcessDefinitionId,
      errorMessage,
    } = this.props.processAssignment;

    // TODO: Remove the <br/>s!
    return (
      <React.Fragment>
        <a
          title={this.props.tooltip || this.props.buttonTitle}
          className={this.props.className}
          disabled={this.props.disabled}
          onClick={this.onToggle}
          style={this.props.style}
        >
          {this.props.children}
        </a>
        <Modal
          show={this.props.processAssignment.editing}
          animation={false}
          onHide={this.onToggle}
        >
          <form onSubmit={this.onSubmit}>
            <div className="modal-header">
              <h4>{t('Assign samples to a workflow')}</h4>
            </div>

            {errorMessage !== null && (
              <div className="alert alert-error alert-block">
                {t(`Not able to assign to process: ${errorMessage}`)}
              </div>
            )}
            <div className="stream-tag-filter">
              <h6 className="nav-header">Preset</h6>
              <SelectControl
                onChange={item =>
                  this.props.processAssignSelectPreset(
                    this.props.presetsById[item.value]
                  )}
                placeholder="Select a preset of workflow and variables"
                options={presetsSorted}
                value={assignPreset ? assignPreset.id : null}
              />
            </div>
            <br />
            <div className="stream-tag-filter">
              <h6 className="nav-header">Workflow</h6>
              <SelectControl
                onChange={(sel) => this.props.processAssignSelectProcess(sel.value)}
                placeholder="Select a workflow or subprocess"
                options={processDefinitions}
                value={assignProcessDefinitionId}
              />
            </div>

            <br />
            {this.renderSettings()}

            {this.renderDiagram()}
            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-default"
                disabled={this.props.process.assignmentSaving}
                onClick={this.onToggle}
              >
                {t('Cancel')}
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={this.props.process.assignmentSaving}
              >
                {t('Assign')}
              </button>
            </div>
          </form>
        </Modal>
      </React.Fragment>
    );
  },
});

const mapStateToProps = (state) => {
  return {
    processDefinition: state.processDefinition,
    substanceSearchEntry: state.substanceSearchEntry,
    process: state.process,
    processAssignment: state.processAssignment,

    presetsById: getPresetsById(state),
  };
};

const mapDispatchToProps = dispatch => ({
  getProcessDefinitionList: () => dispatch(processDefinitionActions.getList()),
  processAssignSelectPreset: preset => dispatch(processAssignSelectPreset(preset)),
  processAssignSelectProcess: process => dispatch(processAssignSelectProcess(process)),
  processAssignSetVariable: (key, value) =>
    dispatch(processAssignSetVariable(key, value)),
  processAssignmentsPost: (definitionId, variables, substances, org) =>
    dispatch(
      processAssignmentsPost(definitionId, variables, substances, org)
    ),
  processAssignmentsSetEditing: value => dispatch(processAssignmentsSetEditing(value)),
});

export default connect(mapStateToProps, mapDispatchToProps)(AssignToWorkflowButton);
