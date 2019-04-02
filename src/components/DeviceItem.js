import React from "react";

export default class DeviceItem extends React.Component {
	render() {
		return (
			<div className='item'>
				<div className='left floated content'>{this.props.device} </div>
				<div className='right floated content'>
					<i className='circle check icon green' />{" "}
				</div>
			</div>
		);
	}
}
