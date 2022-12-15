"""MontapackingSink target sink class, which handles writing streams."""

import json
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, cast

from singer_sdk.plugin_base import PluginBase
from singer_sdk.sinks import RecordSink

from target_montapacking.rest import Rest


class MontapackingSink(RecordSink, Rest):
    """MontapackingSink target sink class."""

    @property
    def name(self):
        raise NotImplementedError

    @property
    def endpoint(self):
        raise NotImplementedError

    @property
    def unified_schema(self):
        raise NotImplementedError

    @property
    def base_url(self):
        return "https://api.montapacking.nl/rest/v5/"

    def url(self, endpoint=None):
        if not endpoint:
            endpoint = self.endpoint
        return f"{self.base_url}{endpoint}"

    def validate_input(self, record: dict):
        return self.unified_schema(**record).dict()

    def validate_output(self, mapping):
        payload = self.clean_payload(mapping)
        # Add validation logic here
        return payload

    def get_data(self, endpoint):
        resp = self.request_api("GET", endpoint=endpoint)
        return resp.json()

    def parse_json(self, input):
        # if it's a string, use json.loads, else return whatever it is
        if isinstance(input, str):
            return json.loads(input)
        return input

    def convert_datetime(self, date: datetime):
        # convert datetime.datetime into str
        if isinstance(date, datetime):
            # This is the format -> "2022-08-15T19:16:35Z"
            return date.strftime("%Y-%m-%dT%H:%M:%SZ")
        return date
