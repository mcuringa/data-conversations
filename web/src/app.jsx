import React, { useState, useEffect } from 'react';
import * as _ from 'lodash';
import { DateTime } from 'luxon';


import 'bootstrap/dist/css/bootstrap.min.css';
import './app.css';
import Spinner from "./ui/spinner.jsx"
import Face from "./face/face.jsx"
import Chat from "./chat/chat.jsx"
import {busListener} from "util/bus.js"

function App(props) {
    const [ws, setWs] = useState(null);
    useEffect(()=>{
      if (!ws) {
        connectMycroftBus(setWs)
      }
    });
    if (!ws) {
      return <Spinner msg="connecting to mycroft ..." />
    }

    return (
      <div className="App container-fluid">
        <div className="ChatPanel row">
          <div className="col border-right">
            <MycroftPanel ws={ws} />
          </div>
          <div className="MainPanel col-sm-10">

          </div>
        </div>
      </div>
    );
}


function 	connectMycroftBus(setWs) {
  const ws = new WebSocket("ws://localhost:8181/core")
  ws.onopen = (event) => {
    setWs(ws);
  }

}



function Chatter(props) {

  let [messages, setMsg] = useState([]);
  let last = ""
  const addMsg = (data) => {
      console.log(data);
      messages.unshift(data);
      messages = messages.slice(0,20);
      last = messages[0].type;
      setMsg([...messages]);
  }

  let listen = ()=> {props.ws.addEventListener("message", busListener(addMsg, null, "^mycroft-date-time.*$"))};
  listen = _.once(listen);
  useEffect(listen, [last]);

  const log = _.map(messages, MycroftMessageLog);
  return <div>{log}</div>

}


function MycroftMessageLog(m, i) {
  return (
    <pre key={i}>
      {m.type}
      {JSON.stringify(m.data, null, 2)}
    </pre>
  )
}


// function Face(props) {
//
// }


function MycroftPanel(props) {
  return (
      <div>
        <Face ws={props.ws} />
        <Chat ws={props.ws} />
        <div>text input</div>
        <div>logo</div>
      </div>
  )
}

export default App;
