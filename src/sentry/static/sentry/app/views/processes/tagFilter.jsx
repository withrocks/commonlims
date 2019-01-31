import PropTypes from 'prop-types';
import React from 'react';
import {debounce} from 'lodash';

import {t} from 'app/locale';
import {Client} from 'app/api';
import SelectControl from 'app/components/forms/selectControl';

// TODO(billy): Update to use SelectAutocomplete when it is ported to use react-select
class ProcessesTagFilter extends React.Component {
  static propTypes = {
    tag: PropTypes.object.isRequired,
    orgId: PropTypes.string.isRequired,
    value: PropTypes.string,
    onSelect: PropTypes.func,
  };

  static tagValueToSelectFormat = ({key, id}) => {
    return {
      key,
      label: key,
    };
  };

  static tagValueToSelectFormat2 = x => {
    return {
      x,
      label: x,
    };
  };

  static defaultProps = {
    tag: {},
    value: '',
  };

  constructor(...args) {
    super(...args);
    this.state = {
      query: '',
      isLoading: false,
      value: this.props.value,
      textValue: this.props.value,
    };
    this.api = new Client();
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.value !== this.state.value) {
      this.setState({
        value: nextProps.value,
        textValue: nextProps.value,
      });
    }
  }

  componentWillUnmount() {
    if (!this.api) return;
    this.api.clear();
  }

  getTagValuesAPIEndpoint = () => {
    let {orgId, tag} = this.props;

    // TODO: Cleaner to have the endpoint in the configuration for the search tags?
    // or just redesign it.
    if (tag.key == 'process') {
      // TODO: process.definition?
      // TODO: This will be a bunch of definitions in the end. Consider limiting to just the
      // ones being used or similar.
      return `/api/0/process-definitions/${orgId}/`;
    } else if (tag.key == 'task-type') {
      return `/api/0/task-types/${orgId}/`;
    } else {
      throw new Error(`Unrecognized tag key: ${tag.key}`);
    }
  };

  getProcessOptions = () => {};

  handleLoadOptions = () => {
    let {tag} = this.props;
    if (tag.isInput || tag.predefined) return;
    if (!this.api) return;

    this.setState({
      isLoading: true,
    });

    this.api
      .requestPromise(this.getTagValuesAPIEndpoint(), {
        query: {
          query: this.state.textValue,
        },
      })
      .then(resp => {
        // TODO: I know this is silly! just POKCing still
        if (tag.key == 'process') {
          this.setState({
            isLoading: false,
            options: Object.values(resp).map(ProcessesTagFilter.tagValueToSelectFormat),
          });
        } else if (tag.key == 'task-type') {
          this.setState({
            isLoading: false,
            // options: Object.values(resp).map((x => { x, label: x }),  // TODO: YUNO
            options: Object.values(resp).map(ProcessesTagFilter.tagValueToSelectFormat2),
          });
        }
      });
  };

  handleChangeInput = e => {
    let value = e.target.value;
    this.setState({
      textValue: value,
    });
    this.debouncedTextChange(value);
  };

  debouncedTextChange = debounce(function(text) {
    this.handleChange(text);
  }, 150);

  handleOpenMenu = () => {
    if (this.props.tag.predefined) return;

    this.setState(
      {
        isLoading: true,
      },
      this.handleLoadOptions
    );
  };

  handleChangeSelect = valueObj => {
    let value = valueObj ? valueObj.value : null;
    this.handleChange(value);
  };

  handleChangeSelectInput = value => {
    this.setState(
      {
        textValue: value,
      },
      this.handleLoadOptions
    );
  };

  handleChange = value => {
    let {onSelect, tag} = this.props;

    this.setState(
      {
        value,
      },
      () => {
        onSelect && onSelect(tag, value);
      }
    );
  };

  render() {
    let {tag} = this.props;

    return (
      <div className="stream-tag-filter">
        <h6 className="nav-header">{tag.key}</h6>

        {!!tag.isInput && (
          <input
            className="form-control"
            type="text"
            value={this.state.textValue}
            onChange={this.handleChangeInput}
          />
        )}

        {!tag.isInput && (
          <SelectControl
            filterOptions={(options, filter, currentValues) => options}
            placeholder="--"
            value={this.state.value}
            onChange={this.handleChangeSelect}
            isLoading={this.state.isLoading}
            onInputChange={this.handleChangeSelectInput}
            onOpen={this.handleOpenMenu}
            autoload={false}
            noResultsText={this.state.isLoading ? t('Loading...') : t('No results found')}
            options={
              tag.predefined
                ? tag.values &&
                  tag.values.map(value => ({
                    value,
                    label: value,
                  }))
                : this.state.options
            }
          />
        )}
      </div>
    );
  }
}

export default ProcessesTagFilter;
