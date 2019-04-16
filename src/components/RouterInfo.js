import React from "react";
import Label from "./Label";
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
      <div className='ui segment'>
        <Label
          id='routerField'
          label='Model'
          value={this.state.modelNumber}
          placeholder='Model Number'
          onChange={e => this.handleChange("modelNumber", e)}
        />
        <Label
          id='routerField'
          label='Firmware'
          value={this.state.firmwareVersion}
          placeholder='Firmware Version'
          onChange={e => this.handleChange("firmwareVersion", e)}
        />
        <Label
          id='routerField'
          label='HW Version'
          value={this.state.hardwareVersion}
          placeholder='Hardware Version'
          onChange={e => this.handleChange("hardwareVersion", e)}
        />
        <Label
          id='routerField'
          label='Serial Number'
          value={this.state.serialNumber}
          placeholder='Serial Number'
          onChange={e => this.handleChange("serialNumber", e)}
        />

        <button className='button ui primary' onClick={this.getDeviceInfo}>
          Get Router info?
        </button>
      </div>
    );
  }
}

export default RouterInfo;
