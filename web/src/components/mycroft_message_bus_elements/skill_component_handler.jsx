import React, { Component } from 'react';
import './default.scss';
import GuiExamplesAiix from './skill_components/gui_examples_aiix';
import MycroftDateTime from './skill_components/mycroft_date_time';
import MycroftWiki from './skill_components/mycroft_wiki';
import MycroftWeather from './skill_components/mycroft_weather';

export default class SkillComponentHandler extends Component {
	constructor(props) {
		super(props)
	}

	returnActiveSkillComponent() {
		const active_skill = this.props.activeSkill
		const skill_state = this.props.skillState
  	const component_focus = skill_state['component_focus']
		const component_name = skill_state['components'][component_focus]
		switch (active_skill) {
		  case "schools-data.adelphi":
		  	return (
		  		<DataConversations
		  			skillState = {skill_state}
		  			componentName = {component_name}
		  		/>
	  		)
  		case "mycroft-wiki.mycroftai":
  			return (
  				<MycroftWiki
		  			skillState = {skill_state}
		  			componentName = {component_name}
  				/>
				)
  		case "mycroft-weather.mycroftai":
  			return (
  				<MycroftWeather
		  			skillState = {skill_state}
		  			componentName = {component_name}
  				/>
				)
		  default:
	      console.log("Unhandled component for: " + active_skill)
	      break
		}
	}

	render() {
		return (
			<div className="skill-container row fade-in">
				{this.returnActiveSkillComponent()}
			</div>
		)
	}
}
