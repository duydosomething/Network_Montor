import React from "react";

class Label extends React.Component {
  render() {
    return (
      <div className='ui labeled input' id={this.props.id}>
        <div className='ui label'>{this.props.label}</div>
        <input
          type='text'
          value={this.props.value}
          placeholder={this.props.placeholder}
          onChange={this.props.onChange}
        />
      </div>
    );
  }
}

export default Label;
