import React from "react";
import { Segment, Checkbox } from "semantic-ui-react";
import LabelItem from "./LabelItem";

class Settings extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      scanInterval: 30,
      email: "",
      sendEmailChecked: false
    };
  }
  handleChange = (key, e) => {
    this.setState({ [key]: e.target.value });
  };

  getScanInterval = () => {
    return this.state.scanInterval;
  };

  handleCheck = () => {
    this.setState(({ sendEmailChecked }) => ({
      sendEmailChecked: !sendEmailChecked
    }));
    console.log(this.state.sendEmailChecked);
  };
  render() {
    window.eel.expose(this.getScanInterval, "get_scan_interval");
    return (
      <Segment>
        <LabelItem
          id='routerInfoSettingField'
          label='Scan Interval'
          type='number'
          min='10'
          value={this.state.scanInterval}
          onChange={e => this.handleChange("scanInterval", e)}
        />
        <Checkbox
          label='Send Email at Midnight'
          style={{ padding: "0px 20px 0px" }}
          checked={this.state.sendEmailChecked}
          onChange={this.handleCheck}
        />
        {this.state.sendEmailChecked ? (
          <LabelItem
            id='routerInfoSettingField'
            label='Email'
            placeholder='Email'
            value={this.state.email}
            onChange={e => this.handleChange("email", e)}
          />
        ) : (
          ""
        )}
      </Segment>
    );
  }
}

export default Settings;
