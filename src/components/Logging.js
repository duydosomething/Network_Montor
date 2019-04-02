import React from "react";

class Logging extends React.Component {
	constructor(props) {
		super(props);
		this.state = { something: "yes" };
	}
	render() {
		return (
			<div class='ui form'>
				<div class='field'>
					<label>Text</label>
					<textarea placeholder='Read Only' readonly='' />
				</div>
			</div>
		);
	}
}

export default Logging;
