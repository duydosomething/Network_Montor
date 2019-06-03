import React from "react";
import Devices from "./Devices";
import Logging from "./Logging";
import { Grid } from "semantic-ui-react";

class TestArea extends React.Component {
	render() {
		return (
			<div className='ui segment'>
				<div className='ui two column divided very relaxed grid'>
					<Grid.Column id='devices'>
						<Devices />
					</Grid.Column>
					<Grid.Column>
						<Logging />
					</Grid.Column>
				</div>
			</div>
		);
	}
}

export default TestArea;
