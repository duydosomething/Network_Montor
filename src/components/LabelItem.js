import React from "react";
import { Label, Input } from "semantic-ui-react";

class LabelItem extends React.Component {
  constructor(props) {
    super(props);
  }
  render() {
    return (
      <div className='ui labeled input' id={this.props.id}>
        <Label> {this.props.label} </Label>
        <Input
          type={this.props.type ? this.props.type : "text"}
          value={this.props.value}
          placeholder={this.props.placeholder}
          onChange={this.props.onChange}
        />
      </div>
    );
  }
}

export default LabelItem;
