import React, { useState, useEffect } from 'react';
import * as _ from 'lodash';
import classNames from 'classnames';

import {busListener} from "util/bus.js"
import "./face.css";

function Face(props) {

  const [status, setStatus] = useState("resting");

  const actions = {
    "wakeword": "listening",
    "utterance": "thinking",
    "audio_output_start": "speaking",
    "audio_output_end": "resting"
  }

  const onStatusChange = (data) => {
      // console.log(data);
      const [route, action] = data.type.split(":")
      console.log("face status:", route, action);
      let s = actions[action];
      if (s) {
        setStatus(s);
      }
  }

  let listen = ()=> {props.ws.addEventListener("message", busListener(onStatusChange, "^recognizer_loop.*"))};
  listen = _.once(listen);
  useEffect(listen, [status]);

  const css = classNames({
    "spinner-grow": status !== "thinking",
    "spinner-border": status === "thinking",
    "resting": status === "resting",
    "listening": status === "listening",
    "thinking": status === "thinking",
    "speaking": status === "speaking",
    "confused": status === "confused",
    "text-primary": status === "resting",
    "text-success": status === "listening",
    "text-info": status === "thinking",
    "text-danger": status === "speaking",
    "text-warning": status === "confused"
  })

  return (
    <div className="Face d-flex justify-content-center p-3">
      <div className={css} role="status">
        <span className="visually-hidden"></span>
      </div>
    </div>
  )
}



export default Face;
