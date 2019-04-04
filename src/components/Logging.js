import React from "react";

export const eel = window.eel;
eel.set_host("ws://localhost:8080");

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

class Logging extends React.Component {
  constructor(props) {
    super(props);
    this.state = { output: "" };
  }

  concatenate = async () => {
    for (let i = 0; i < 10; i++) {
      this.setState({
        output: this.state.output.concat(
          "LONGGGGGGGGGGGGGGGGG SETTTTTTEEEEEEEEEENCEEEEE\n"
        )
      });
      console.log(this.state);
      await sleep(200);
    }
  };

  startCompare = () => {
    eel.start_compare();
  };

  stopCompare = () => {
    eel.stop_compare();
  };
  render() {
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
