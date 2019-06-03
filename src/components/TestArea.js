import React from "react";
import Devices from "./Devices";
import Logging from "./Logging";
import { Grid } from "semantic-ui-react";

class TestArea extends React.Component {
	constructor(props) {
		super(props);
		this.state = {};

		//this.updateStatus = this.updateStatus.bind(this);
	}

	updateStatus = (device, status) => {
		let newState = Object.assign({}, this.state);
		newState[device].status = status;
		this.setState(newState);
	};

	updateList = (device, mac, status) => {
		this.setState({ [device]: { mac, status } });
	};
	render() {
		return (
			<div className='ui segment'>
				<div className='ui two column divided very relaxed grid'>
					<Grid.Column id='devices'>
						<Devices
							devices={this.state}
							updateList={this.updateList}
							updateStatus={this.updateStatus}
						/>
					</Grid.Column>
					<Grid.Column>
						<Logging devices={this.state} updateStatus={this.updateStatus} />
					</Grid.Column>
				</div>
			</div>
		);
	}
}

export default TestArea;
