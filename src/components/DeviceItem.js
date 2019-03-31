import React from "react";

export default class DeviceItem extends React.Component {
  render() {
    return (
      <div className='ui list item'>
        {this.props.device} <i className='circle check icon green' />
      </div>
    );
  }
}
