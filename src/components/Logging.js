import React from "react";
import { Form, Button, TextArea } from "semantic-ui-react";
export const eel = window.eel;
eel.set_host("ws://localhost:8080");

class Logging extends React.Component {
	constructor(props) {
		super(props);
		this.state = { output: "", stopPressed: false, startPressed: false };
	}
	updateOutput = message => {
		this.setState({ output: this.state.output.concat(message) });
	};

	getOuput = () => {
		return this.state.output;
	};

	saveLog = () => {
		eel.save_log();
	};
	startCompare = () => {
		eel.start_compare();
		this.setState({ output: "", stopPressed: false, startPressed: true });
	};

	stopCompare = () => {
		eel.stop_compare();
		this.setState({ stopPressed: true, startPressed: false });
	};
	render() {
		window.eel.expose(this.updateOutput, "update_output");
		window.eel.expose(this.getOutput, "get_output");
		window.eel.expose(this.props.updateStatus, "update_status");
		return (
			<Form ui>
				<Form.Field>
					{this.state.startPressed && (
						<Button negative onClick={this.stopCompare}>
							Stop
						</Button>
					)}
					{!this.state.startPressed && (
						<Button primary onClick={this.startCompare}>
							Start
						</Button>
					)}

					<Button
						className={
							"ui button " + (this.state.stopPressed ? "" : "disabled")
						}
						onClick={this.saveLog}
					>
						Save Log
					</Button>
					<TextArea
						id='scroll'
						value={this.state.output}
						placeholder='Read Only'
						readonly=''
					/>
				</Form.Field>
			</Form>
		);
	}
}

export default Logging;
