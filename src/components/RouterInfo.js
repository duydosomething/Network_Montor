import React from "react";
import LabelItem from "./LabelItem";
import { Segment } from "semantic-ui-react";
export const eel = window.eel;

eel.set_host("ws://localhost:8080");
class RouterInfo extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hardwareVersion: "",
      serialNumber: "",
      firmwareVersion: "",
      modelNumber: ""
    };
  }

  handleChange = (key, e) => {
    this.setState({ [key]: e.target.value });
  };

  getRouterInfo = () => {
    return this.state;
  };

  getDeviceInfo = async () => {
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
    window.eel.expose(this.getRouterInfo, "get_router_info");
    return (
      <Segment>
        <LabelItem
          id='routerInfoSettingField'
          label='Model'
          value={this.state.modelNumber}
          placeholder='Model Number'
          onChange={e => this.handleChange("modelNumber", e)}
        />
        <LabelItem
          id='routerInfoSettingField'
          label='Firmware'
          value={this.state.firmwareVersion}
          placeholder='Firmware Version'
          onChange={e => this.handleChange("firmwareVersion", e)}
        />
        <LabelItem
          id='routerInfoSettingField'
          label='HW Version'
          value={this.state.hardwareVersion}
          placeholder='Hardware Version'
          onChange={e => this.handleChange("hardwareVersion", e)}
        />
        <LabelItem
          id='routerInfoSettingField'
          label='Serial Number'
          value={this.state.serialNumber}
          placeholder='Serial Number'
          onChange={e => this.handleChange("serialNumber", e)}
        />
      </Segment>
    );
  }
}

export default RouterInfo;
