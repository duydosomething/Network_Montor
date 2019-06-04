import React, { Component } from "react";
import "./App.css";
import RouterInfo from "./components/RouterInfo";
import TestArea from "./components/TestArea";
import RouterInfoSettings from "./components/RouterInfoSettings";

export class App extends Component {
	render() {
		return (
			<div className='App'>
				<RouterInfoSettings />
				<TestArea />
			</div>
		);
	}
}

export default App;
