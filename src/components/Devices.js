import React from "react";
import DeviceItem from "./DeviceItem";

export const eel = window.eel;
eel.set_host("ws://localhost:8080");

class Devices extends React.Component {
  constructor(props) {
    super(props);
    this.state = { devices: "filler" };
  }
  getDevices = async () => {
    let n = await eel.get_scan_results()();
    for (let [key, value] of Object.entries(n)) {
      if (value["addresses"]["mac"]) {
        this.setState({ [key]: value["addresses"]["mac"] });
      } else {
        this.setState({ [key]: "SELF" });
      }
    }
    this.setState({ devices: JSON.stringify(n) });
    console.log(n);
  };
  render() {
    return (
      <div>
        <button className='ui button' onClick={this.getDevices}>
          Get Devices
        </button>
        <div className='ui middle aligned list'>
          {Object.keys(this.state).map(key => {
            return (
              // <div className='item'>
              //   {key}: {this.state[key]}
              // </div>
              <DeviceItem device={key} />
            );
          })}
        </div>
      </div>
    );
  }
}

export default Devices;
