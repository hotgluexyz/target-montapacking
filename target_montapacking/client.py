"""MontapackingSink target sink class, which handles writing streams."""

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

