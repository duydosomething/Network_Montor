import React, { Component } from "react";
import "./App.css";
// Point Eel web socket to the instance
export const eel = window.eel;
eel.set_host("ws://localhost:8080");

// Expose the `sayHelloJS` function to Python as `say_hello_js`
function sayHelloJS(x) {
	console.log("Hello from " + x);
}
// WARN: must use window.eel to keep parse-able eel.expose{...}
window.eel.expose(sayHelloJS, "say_hello_js");

// Test calling sayHelloJS, then call the corresponding Python function
sayHelloJS("Javascript World!");
eel.say_hello_py("Javascript World!");

async function test() {
	let n = await eel.getDeviceInfo()();
	console.log(typeof n);
}

test();
export class App extends Component {
	constructor(props) {
		super(props);
		this.state = {
			hardwareVersion: "",
			serialNumber: "",
			firmwareVersion: "",
			modelNumber: ""
		};
	}

	pickFile = async () => {
		let n = await eel.getDeviceInfo()();
		for (let key in n) {
			if (n.hasOwnProperty(key)) {
				console.log(key);
				console.log(this.state);
				this.setState({ [key]: n[key] });
			}
		}
	};

	render() {
		return (
			<div className='App'>
				<header className='App-header'>
					<div className='ui segment'>
						<div className='ui labeled input' id='routerField'>
							<div class='ui label'>Model</div>
							<input
								type='text'
								value={this.state.modelNumber}
								placeholder='Model Number'
								onChange={e => this.setState({ modelNumber: e.target.value })}
							/>
						</div>
						<div className='ui labeled input' id='routerField'>
							<div class='ui label'>Firmware</div>
							<input
								type='text'
								value={this.state.firmwareVersion}
								placeholder='Firmware Version'
								onChange={e =>
									this.setState({ firmwareVersion: e.target.value })
								}
							/>
						</div>

						<div className='ui labeled input' id='routerField'>
							<div class='ui label'>Hardware Version</div>
							<input
								type='text'
								value={this.state.hardwareVersion}
								placeholder='Hardware Version'
								onChange={e =>
									this.setState({ hardwareVersion: e.target.value })
								}
							/>
						</div>
						<div className='ui labeled input' id='routerField'>
							<div class='ui label'>Serial Number</div>
							<input
								type='text'
								value={this.state.serialNumber}
								placeholder='Serial Number'
								onChange={e => this.setState({ serialNumber: e.target.value })}
							/>
						</div>
						<button className='button ui primary' onClick={this.pickFile}>
							Get Router info?
						</button>
					</div>
				</header>
			</div>
		);
	}
}

export default App;
