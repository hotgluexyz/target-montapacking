"""Montapacking target sink class, which handles writing streams."""

from base64 import b64encode
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, cast

import backoff
import requests
from singer_sdk.exceptions import FatalAPIError, RetriableAPIError


class Rest:

    timeout = 300
    access_token = None

    @property
    def authenticator(self):
        user = self.config.get("username")
        passwd = self.config.get("password")
        token = b64encode(f"{user}:{passwd}".encode()).decode()
        return f"Basic {token}"

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        headers["Content-Type"] = "application/json"
        headers.update({"Authorization": self.authenticator})
        return headers

    @backoff.on_exception(
        backoff.expo,
        (RetriableAPIError, requests.exceptions.ReadTimeout),
        max_tries=5,
        factor=2,
    )
    def _request(
        self, http_method, endpoint, params=None, request_data=None
    ) -> requests.PreparedRequest:
        """Prepare a request object."""
        url = self.url(endpoint)
        headers = self.http_headers
        # headers["User-Agent"] = self.user_agents.get_random_user_agent().strip()

        timeout = 60

        try:
            # By default "timeout" is going to be 60 (seconds). But I'm adding the option
            # to set it back as "None" if "request_timeout" is in the config.
            # If it is and it's "null", the request will have no timeout
            if isinstance(self.config, dict) and "request_timeout" in self.config:
                timeout = self.config.get("request_timeout")
        except:
            pass

        response = requests.request(
            method=http_method,
            url=url,
            params=params,
            headers=headers,
            json=request_data,
            timeout=timeout,
        )
        self.validate_response(response)
        return response

    def request_api(self, http_method, endpoint=None, params=None, request_data=None):
        """Request records from REST endpoint(s), returning response records."""
        resp = self._request(http_method, endpoint, params, request_data)
        return resp

    def validate_response(self, response: requests.Response) -> None:
        """Validate HTTP response."""
        if response.status_code in [429] or 500 <= response.status_code < 600:
            msg = self.response_error_message(response)
            raise RetriableAPIError(msg, response)
        elif response.status_code == 400:
            if "Reference already exists for another group" in response.text:
                # If reference already exists do not raise
                # This means we need to update the record
                return None
            else:
                msg = self.response_error_message(response)
                self.logger.error(response.text)
                raise FatalAPIError(msg)
        elif 400 <= response.status_code < 500:
            try:
                msg = response.text
                if not msg:
                    msg = response.reason
            except:
                msg = self.response_error_message(response)
            raise FatalAPIError(msg)

    def response_error_message(self, response: requests.Response) -> str:
        """Build error message for invalid http statuses."""
        if 400 <= response.status_code < 500:
            error_type = "Client"
        else:
            error_type = "Server"

        return (
            f"{response.status_code} {error_type} Error: "
            f"{response.reason} for path: {self.endpoint}"
            f"{response.text}"
        )

    @staticmethod
    def clean_dict_items(dict):
        return {k: v for k, v in dict.items() if v not in [None, ""]}

    def clean_payload(self, item):
        item = self.clean_dict_items(item)
        output = {}
        for k, v in item.items():
            if isinstance(v, datetime):
                dt_str = v.strftime("%Y-%m-%dT%H:%M:%S%z")
                if len(dt_str) > 20:
                    output[k] = f"{dt_str[:-2]}:{dt_str[-2:]}"
                else:
                    output[k] = dt_str
            elif isinstance(v, dict):
                output[k] = self.clean_payload(v)
            else:
                output[k] = v
        return output
