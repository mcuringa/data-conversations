import React, { Component } from 'react';

export default class MycroftDateTime extends React.Component {
	constructor(props) {
		super(props)
	}

  render() {
    return (
	  	<div>
	    	{this.props.skillState['time_string']}
	  	</div>
  	)
  }
}
