import React from "react";
import { Item, Icon } from "semantic-ui-react";

export default class DeviceItem extends React.Component {
	render() {
		return (
			<Item>
				<div className='left floated content'>{this.props.device} </div>
				<Icon name='circle check' color='green' floated='right' />
			</Item>
		);
	}
}
