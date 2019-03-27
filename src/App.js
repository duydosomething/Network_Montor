import React, { Component } from "react";
import logo from "./logo.svg";
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
      message: `Click button to choose a random file from the user's sustem`,
      hardwareVersion: "",
      serialNumber: "",
      firmwareVersion: "",
      modelNumber: ""
    };
  }

  pickFile = async () => {
    console.log("yes");
    let n = await eel.getDeviceInfo()();
    for (let key in n) {
      if (n.hasOwnProperty(key)) {
        console.log(key);
        console.log(this.state);
        this.setState({ [key]: n[key] });
      }
    }

    // eel.getDeviceInfo()(message => this.setState({ message }));
  };

  render() {
    return (
      <div className='App'>
        <header className='App-header'>
          <img src={logo} className='App-logo' alt='logo' />
          <p>{this.state.message}</p>
          Model: {this.state.modelNumber}
          <br />
          Firmware: {this.state.firmwareVersion}
          <br />
          Hardware: {this.state.hardwareVersion}
          <br />
          Serial Number: {this.state.serialNumber}
          <button className='App-button' onClick={this.pickFile}>
            Get Router info?
          </button>
        </header>
      </div>
    );
  }
}

export default App;
