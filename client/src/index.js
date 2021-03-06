/**
 * Entry point into the application
 * Router keeps UI and URL in sync and ensures that the props are passed
 * Provider makes the store available to the component hierarchy
 * That way, the components below the hierarchy can access the store’s state with connect
 * method call.
*/

import React from 'react';
import { render } from 'react-dom';
import './styles/sass/index.css';
import App from './containers/App';
import configureStore from './store/configureStore';
import { Provider } from 'react-redux';
// import injectTapEventPlugin from 'react-tap-event-plugin';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';

// Needed for onTouchTap
// http://stackoverflow.com/a/34015469/988941
// injectTapEventPlugin();

// initialize store
const store = configureStore();

// render the application to the DOM
render(
    <Provider store={store}>
        <MuiThemeProvider>
            <App />
        </MuiThemeProvider>
    </Provider>,
    document.getElementById('root')
);
