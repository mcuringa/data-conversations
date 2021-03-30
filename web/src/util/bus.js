/**
 * functions for working with the mycroft message bus
 */


import * as _ from 'lodash';

function busListener(f, paths, exclude) {


  const listener = (e)=> {
    const data = JSON.parse(e.data);


    // debug(data);

    //listen to everything
    if (!paths && !exclude) {
      f(data);
    }


    const match = testPath(data.type, paths);
    const ex = testPath(data.type, exclude);

    if (match && !ex) {
      f(data);
    }
  }


  return listener;
}

function testPath(path, paths) {
  if(!paths) {
    return false;
  }

  paths = asArray(paths);
  for(const pattern of paths) {
    const re = new RegExp(pattern);
    if (re.test(path)) {
      return true;
    }
  }
  return false;
}

function asArray(t) {
  if (_.isArray(t)) {
    return t;
  }
  return [t];
}

function debug(data) {
  const type = data.type;
  if (type.indexOf("gui") === -1
     && type.indexOf("time") === -1
     && type.indexOf("enclosure") === -1
     && type.indexOf("reminder") === -1) {
    console.log(data);
  }

}

let bus = { }
bus.busListener = busListener;

export default bus;
export {busListener}
