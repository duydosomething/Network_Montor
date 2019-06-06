import React from "react";

import { Button, Accordion } from "semantic-ui-react";

export const eel = window.eel;
eel.set_host("ws://localhost:8080");

class Devices extends React.Component {
  // constructor(props) {
  // 	super(props);
  // }

  getDevices = async () => {
    this.props.reset();
    let n = await eel.get_scan_results()();
    let devices = {};
    for (let [key, value] of Object.entries(n)) {
      if (value["addresses"]["mac"]) {
        // this.props.updateList({
        // 	[key]: { mac: value["addresses"]["mac"], status: "up" }
        // });

        //this.props.updateList(key, value["addresses"]["mac"], "up");
        devices[key] = { mac: value["addresses"]["mac"], status: "up" };
      }
    }
    this.props.updateList(devices);
    //return devices;
    // this.setState({ devices: JSON.stringify(n) });
    // console.log(n);
  };
  render() {
    const panels = Object.keys(this.props.devices).map(key => ({
      key: key,
      title: {
        content: key,
        icon: {
          name: "circle",
          color: this.props.devices[key]["status"] === "up" ? "green" : "red"
        }
      },
      content: this.props.devices[key]["mac"]
    }));
    return (
      <div>
        <Button primary onClick={this.getDevices}>
          Get Devices
        </Button>
        <Accordion id='scroll' panels={panels} exclusive={false} />
      </div>
    );
  }
}

export default Devices;
