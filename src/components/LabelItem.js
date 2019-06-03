import React from "react";
import { Label, Input } from "semantic-ui-react";

class LabelItem extends React.Component {
	render() {
		return (
			<div className='ui labeled input' id={this.props.id}>
				<Label> {this.props.label} </Label>
				<Input
					type='text'
					value={this.props.value}
					placeholder={this.props.placeholder}
					onChange={this.props.onChange}
				/>
			</div>
		);
	}
}

export default LabelItem;
