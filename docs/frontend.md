# Frontend Architecture Overview

The Common LIMS frontend app code can be found in `src/static/sentry`. Javascript tests are written in Jest and can be found in `tests/js/spec`.

## Components

Common LIMS uses React for its frontend components.

## API calls

Common LIMS API calls should be performed with the [Axios library](https://github.com/axios/axios) (and mocked with [moxios](https://github.com/axios/moxios)). Legacy Sentry components use a custom HTTP client defined in `app/api.jsx` that uses jQuery under the hood.

## Store

All Common LIMS components use a [Redux](https://react-redux.js.org/) store, while legacy Sentry components use [Reflux](https://github.com/reflux/refluxjs). Only "smart" components, i.e. views should interact with the store. All other "dumb" components should receive the relevant data as props.

Information on connecting React components to the Redux store can be found [here](https://react-redux.js.org/api/connect).

## Redux Architecture

Redux code is in the directory `app/redux`. Common LIMS configures Redux as follows:

* `store.js` configures the store with middleware, including a logger and [redux-thunk](https://medium.com/fullstack-academy/thunks-in-redux-the-basics-85e538a3fe60)
* `app/views/app.jsx` invokes the configuration logic and uses ReduxProvider to expose the store to the React application

This configuration, together with an example Redux implementation, is illustrated in [this pull request](https://github.com/commonlims/commonlims/pull/17/files).

### Actions and Reducers

Typically, each API resource should have its own action and reducer file in `app/redux`. The reducer file should also be added to the index `app/redux/reducers/index.js`.

We use the following convention for naming actions: `[RESOURCE_NAME]_[ACTION]_[REQUEST|SUCCESS|FAILURE]`, where ACTION is usually (but not necessarily) an HTTP method. For example: 'USER_TASKS_GET_SUCCESS'. Each action should be wrapped in its own function, such as userTasksGetSuccess(). In addition, you will want to create a thunk wrapper for any asynchronous API calls, such as userTasksGet().

Every action should be handled in the corresponding reducer file.