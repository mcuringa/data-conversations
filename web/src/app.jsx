import React, { useState, useEffect } from 'react';
import * as _ from 'lodash';
import { DateTime } from 'luxon';


import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './app.css';
import MIXILogo from "./ui/mixi-logo.png";

import Spinner from "./ui/spinner.jsx"
import Face from "react-mycroft/face/face.jsx"
import Chat from "react-mycroft/chat/chat.jsx"
import ChatBox from "./chat/chatbox.jsx"
import mycroft from "react-mycroft/bus.js"

import ChoiceList from "./data-views/choice-list.jsx"

function App(props) {
    return (
      <div className="App container-fluid p-0 d-flex justify-content-start overflow-auto">
        <mycroft.MessageBusLog />
      </div>
    );
}


// <div className="App container-fluid p-0 d-flex justify-content-start">
//   <MycroftPanel ws={ws} />
//   <div className="MainPanel">
//       <MycroftPanel ws={ws} />
//   </div>
// </div>



function MycroftPanel(props) {
  return (
      <div className="ChatPanel col border-right d-flex align-content-between flex-wrap">
        <div className="">
          <Face ws={props.ws} />
        </div>
        <div className="Chat d-flex flex-column justify-content-end">
          <Chat ws={props.ws} />
          <ChatBox ws={props.ws} />
        </div>
        <div className="Footer mt-3 border-top p-2">
          <img className="img-fluid d-block" src={MIXILogo} alt="stylized word m.i.x.i." />
          <p>
            <strong>Data Converstaions</strong> is a project
            of the <a href="https://mixi.edu">Adelphi University</a> Manhattan
            Imagine-X Institute (MIXI).
          </p>
        </div>
      </div>
  )
}

export default App;
