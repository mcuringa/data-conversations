# Copyright 2021, Matthew X. Curinga
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import re
import json
from requests import HTTPError, Response

import mycroft.audio
from adapt.intent import IntentBuilder
from mycroft.api import Api
from mycroft import MycroftSkill, intent_handler
from mycroft.messagebus.message import Message
from mycroft.util.log import LOG
from mycroft.util.format import (nice_date, nice_time, nice_number,
                                 pronounce_number, join_list)
from mycroft.util.parse import extract_datetime, extract_number
from mycroft.util.time import now_local, to_utc, to_local

import pandas as pd
from . import schools


def parse_school(text):
    """
        Look for school numbers in a tts utterance
        because mycroft doesn't always put a space between the
        letters and number(ms88 ->ms 88)
    """
    p = re.compile(r"^(.*?)\b([m|p|i]s)([0-9]*)\b(.*)$", re.IGNORECASE)
    m = p.search(text)
    if m:
        return f"{m.group(1)}{m.group(2)} {m.group(3)}{m.group(4)}"
    return text

class SchoolDataSkill(MycroftSkill):
    def __init__(self):
        super().__init__("SchoolDataSkill")

    def initialize(self):
        """load the school demographic data from datahub and keep it local"""
        self.demo_df = schools.load_demographics()
        self.context_df = None



    @intent_handler("school.intent")
    def handle_school(self, message):
        qry = message.data['school']
        qry = parse_school(qry)

        t = schools.find_school(self.demo_df, qry)
        self.context_df = t

        bus_data = {'data': pd.DataFrame.to_json(t.school_name, orient='records'),
          'view': 'school-list',
          'title':"Which school do you want to see?"}


        self.bus.emit(Message('data_conversations:list', bus_data))

        self.speak(f"looking for school called {qry}")



def create_skill():
    return SchoolDataSkill()
