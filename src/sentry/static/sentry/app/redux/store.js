/*global process*/
import {createStore, applyMiddleware} from 'redux';
import {createLogger} from 'redux-logger';
import thunk from 'redux-thunk';
import reducer from './reducers/index';

const middleware = [thunk];

const logger = createLogger({
  diff: true,
});

if (process.env.NODE_ENV !== 'production') {
  middleware.push(logger);
}

export default function configureStore(initialState) {
  const store = createStore(reducer, initialState, applyMiddleware(...middleware));
  return store;
}
