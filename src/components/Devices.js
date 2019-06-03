import React from "react";
import DeviceItem from "./DeviceItem";
import { Button, Accordion, Item } from "semantic-ui-react";

export const eel = window.eel;
eel.set_host("ws://localhost:8080");

class Devices extends React.Component {
	constructor(props) {
		super(props);
		this.state = {};
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
				<Button color='blue' onClick={this.getDevices}>
					Get Devices
				</Button>

				<Item.Group divided id='scroll'>
					{Object.keys(this.state).map(key => {
						return <DeviceItem device={key} />;
					})}
				</Item.Group>
			</div>
		);
	}
}

export default Devices;
