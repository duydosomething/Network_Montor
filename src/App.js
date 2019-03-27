import React, { Component } from "react";
import "./App.css";

import RouterInfo from "./components/RouterInfo";
// Point Eel web socket to the instance

export class App extends Component {
  render() {
    return (
      <div className='App'>
        <RouterInfo />
      </div>
    );
  }
}

export default App;
