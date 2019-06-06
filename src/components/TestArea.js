import React from "react";
import Devices from "./Devices";
import Logging from "./Logging";
import { Grid } from "semantic-ui-react";

class TestArea extends React.Component {
  constructor(props) {
    super(props);
    this.state = { devices: {} };
  }

  updateStatus = (device, status) => {
    let newState = Object.assign({}, this.state.devices);
    console.log(newState);
    newState[device].status = status;
    this.setState(newState);
  };

  updateList = newDict => {
    console.log(newDict);
    this.setState({ devices: newDict });
  };

  reset = () => {
    this.setState({ devices: {} });
    console.log(this.state);
  };
  render() {
    return (
      <div className='ui segment'>
        <div className='ui two column divided very relaxed grid'>
          <Grid.Column id='devices'>
            <Devices
              devices={this.state.devices}
              updateList={this.updateList}
              updateStatus={this.updateStatus}
              reset={this.reset}
            />
          </Grid.Column>
          <Grid.Column>
            <Logging
              devices={this.state.devices}
              updateStatus={this.updateStatus}
            />
          </Grid.Column>
        </div>
      </div>
    );
  }
}

export default TestArea;
