import React from "react";

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

class Logging extends React.Component {
  constructor(props) {
    super(props);
    this.state = { something: "" };
  }

  concatenate = async () => {
    for (let i = 0; i < 10; i++) {
      this.setState({
        something: this.state.something.concat(
          "LONGGGGGGGGGGGGGGGGG SETTTTTTEEEEEEEEEENCEEEEE"
        )
      });
      console.log(this.state);
      await sleep(200);
    }
  };
  render() {
    return (
      <div class='ui form'>
        <div class='field'>
          <label>Text</label>
          <button className='ui button primary' onClick={this.concatenate}>
            Concat
          </button>
          <textarea
            id='scroll'
            value={this.state.something}
            placeholder='Read Only'
            readonly=''
          />
        </div>
      </div>
    );
  }
}

export default Logging;
