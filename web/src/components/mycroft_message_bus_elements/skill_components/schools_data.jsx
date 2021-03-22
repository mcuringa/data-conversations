import React, { Component, useEffect, useCallback} from 'react';
import { DateTime as dt } from "luxon";


class SchoolsDataSkill extends React.Component {

	constructor(props) {
		super(props);
	}

  render() {
  	const skill_props = this.props.skillState;
		console.log(skill_props);

		return (
			<div className="SchoolsDataSkill">
				<h1>{dt.now().toLocaleString(dt.TIME_SIMPLE)}</h1>
				<p>Forcast{skill_props.forcast}</p>

			</div>
		);
  }
}


export default SchoolsDataSkill;
