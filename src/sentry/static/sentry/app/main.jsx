/* global module */
import {hot} from 'react-hot-loader';
import React from 'react';
import {Router, browserHistory} from 'react-router';

import routes from 'app/routes';
import {loadPreferencesState} from 'app/actionCreators/preferences';

class Main extends React.Component {
  componentDidMount() {
    loadPreferencesState();
  }

  render() {
    return <Router history={browserHistory}>{routes()}</Router>;
  }
}

export default hot(module)(Main);
