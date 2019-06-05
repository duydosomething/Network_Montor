import React from "react";
import Devices from "./Devices";
import Logging from "./Logging";
import { Grid } from "semantic-ui-react";

const initalState = {};

class TestArea extends React.Component {
	constructor(props) {
		super(props);
		this.state = {};
	}

	updateStatus = (device, status) => {
		let newState = Object.assign({}, this.state);
		newState[device].status = status;
		this.setState(newState);
	};

	updateList = (device, mac, status) => {
		this.setState({ [device]: { mac, status } });
	};

	reset = () => {
		this.setState(initalState);
		console.log(this.state);
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
							reset={this.reset}
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
