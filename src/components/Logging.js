import React from "react";

export const eel = window.eel;
eel.set_host("ws://localhost:8080");

class Logging extends React.Component {
	constructor(props) {
		super(props);
		this.state = { output: "" };
	}
	updateOutput = message => {
		this.setState({ output: this.state.output.concat(message) });
	};

	startCompare = () => {
		eel.start_compare();
	};

	stopCompare = () => {
		eel.stop_compare();
	};
	render() {
		window.eel.expose(this.updateOutput, "update_output");
		return (
			<div className='ui form'>
				<div className='field'>
					<button className='ui button primary' onClick={this.startCompare}>
						Start
					</button>
					<button className='ui button negative' onClick={this.stopCompare}>
						Stop
					</button>
					<textarea
						id='scroll'
						value={this.state.output}
						placeholder='Read Only'
						readonly=''
					/>
				</div>
			</div>
		);
	}
}

export default Logging;
