import React, { Component } from "react";
import "./App.css";
import RouterInfo from "./components/RouterInfo";
import TestArea from "./components/TestArea";

export class App extends Component {
  render() {
    return (
      <div className='App'>
        <RouterInfo />
        <TestArea />
      </div>
    );
  }
}

export default App;
