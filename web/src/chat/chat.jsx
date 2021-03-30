import React, { useState, useEffect } from 'react';
import * as _ from 'lodash';
import classNames from 'classnames';

import { DateTime } from "luxon";

import {busListener} from "util/bus.js"
import mycroftIcon from "./mycroft-chat.png";

import "./chat.css";

function Chat(props) {

  const [messages, setMessages] = useState([]);

  let last = 0;

  const addMsg = (data) => {
      const now = DateTime.now();
      last = now.toISO()
      data.timestamp = last;
      console.log("chat msg:", data);
      messages.push(MycroftChat(data));
      setMessages([...messages]);
  }



  let listen = ()=> {props.ws.addEventListener("message", busListener(addMsg, ["speak","recognizer_loop:utterance"]))};
  listen = _.once(listen);
  useEffect(listen, [last]);


  return (
    <div className="Chat">
      {messages}
    </div>
  )
}


function MycroftChat(data) {

  const mycroft = data.type === "speak";
  const user = !mycroft;

  // different structure for user input and mycroft output
  let msg = data.data.utterance || data.data.utterances[0];

  const css = classNames("card", "p-2", "m-2", "d-flex", {
    "justify-content-start": mycroft,
    "justify-content-end": user,
    "mr-2": mycroft,
    "bg-light": mycroft,
    "text-black": mycroft,
    "text-left": mycroft,
    "ml-2": user,
    "bg-primary": user,
    "text-right": user,
    "text-white": user
  });


  const imgCss = classNames("flex-shrink-0",  {
    "d-none": user,
    "d-block": mycroft
  });

  return (
    <div key={data.timestamp} className={css}>
      <div className={imgCss}>
        <img src={mycroftIcon} className="rounded-circle" alt="mycroft icon" />
      </div>
      <div className="flex-grow-1 ms-3">{msg}</div>
    </div>
  )
}

export default Chat;
