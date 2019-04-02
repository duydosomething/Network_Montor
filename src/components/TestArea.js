import React from "react";
import Devices from "./Devices";
class TestArea extends React.Component {
  render() {
    return (
      <div className='ui segment'>
        <div className='ui two column divided very relaxed grid'>
          <div className='column'>
            <Devices />
          </div>
          <div className='column'>
            <Devices />
          </div>
        </div>
      </div>
    );
  }
}

export default TestArea;
