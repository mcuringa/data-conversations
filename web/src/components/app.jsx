import React, { Component } from 'react';
import Face from './face/face'
import MycroftMessageBusSkillComponent from './mycroft_message_bus_elements/mycroft_message_bus';
import 'bootstrap/dist/css/bootstrap.min.css';
import './app.css';

class App extends Component {
  render() {
    return (
      <div className="App container-fluid">
        <div class="row">
          <div class="col">
            Smily Face
          </div>
          <div class="col-sm-10">
            <MycroftMessageBusSkillComponent />
          </div>
        </div>
      </div>
    );
  }
}

export default App;
