import React from "react";

export const eel = window.eel;
eel.set_host("ws://localhost:8080");

class Devices extends React.Component {
  constructor(props) {
    super(props);
    this.state = { devices: "filler" };
  }
  getDevices = async () => {
    let n = await eel.get_scan_results()();
    this.setState({ devices: JSON.stringify(n) });
    console.log(n);
  };
  render() {
    return (
      <div>
        <button className='ui button' onClick={this.getDevices}>
          Get Devices
        </button>
        {this.state.devices}
      </div>
    );
  }
}

export default Devices;
