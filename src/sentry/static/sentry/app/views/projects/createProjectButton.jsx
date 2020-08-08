import PropTypes from 'prop-types';
import React from 'react';
import Modal from 'react-bootstrap/lib/Modal';

import {t} from 'app/locale';
import {FormState} from 'app/components/forms';
import {ValidationIssues} from 'app/components/validationIssues';
import IndicatorStore from 'app/stores/indicatorStore';

class CreateProjectButton extends React.Component {
  // TODO-simple: lab is hardcoded as an org
  constructor(props) {
    super(props);
    this.state = {
      isModalOpen: false,
      value: null,
      selectedFile: null,
      loaded: 0,
      validationIssues: [],
      errorMsg: null,
    };

    this.onToggle = this.onToggle.bind(this);
  }

  onToggle() {
    if (this.props.disabled) {
      return;
    }

    this.setState({
      isModalOpen: !this.state.isModalOpen,
      state: FormState.READY,
      errorMsg: null,
      validationIssues: [],
    });
  }

  render() {
    return (
      <React.Fragment>
        <a
          title={this.props.tooltip || this.props.buttonTitle}
          className="btn btn-sm btn-default"
          disabled={this.props.disabled}
          onClick={this.onToggle}
          style={this.props.style}
        >
          {this.props.children}
        </a>
        <Modal show={this.state.isModalOpen} animation={false} onHide={this.onToggle}>
          <div className="modal-header">
            <h4>{t('Create project')}</h4>
          </div>
        </Modal>
      </React.Fragment>
    );
  }
}

CreateProjectButton.propTypes = {
  tooltip: PropTypes.string,
  buttonTitle: PropTypes.string,
  disabled: PropTypes.bool,
};

export default CreateProjectButton;
