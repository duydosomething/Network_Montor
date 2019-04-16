import React from "react";

export const eel = window.eel;
eel.set_host("ws://localhost:8080");

class Logging extends React.Component {
  constructor(props) {
    super(props);
    this.state = { output: "", stopPressed: false, startPressed: false };
  }
  updateOutput = message => {
    this.setState({ output: this.state.output.concat(message) });
  };

  getOuput = () => {
    return this.state.output;
  };

  saveLog = () => {
    eel.save_log();
  };
  startCompare = () => {
    eel.start_compare();
    this.setState({ output: "", stopPressed: false, startPressed: true });
  };

  stopCompare = () => {
    eel.stop_compare();
    this.setState({ stopPressed: true, startPressed: false });
  };
  render() {
    window.eel.expose(this.updateOutput, "update_output");
    window.eel.expose(this.getOuput, "get_output");
    return (
      <div className='ui form'>
        <div className='field'>
          {this.state.startPressed && (
            <button className='ui button negative' onClick={this.stopCompare}>
              Stop
            </button>
          )}
          {!this.state.startPressed && (
            <button className='ui button primary' onClick={this.startCompare}>
              Start
            </button>
          )}

          <button
            className={
              "ui button " + (this.state.stopPressed ? "" : "disabled")
            }
            onClick={this.saveLog}
          >
            Save Log
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
