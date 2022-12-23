"""Montapacking target class."""

from __future__ import annotations

from typing import Type

from singer_sdk import typing as th
from singer_sdk.sinks import Sink
from singer_sdk.target_base import Target

from target_montapacking.sinks import InboundForecastSink,UpdateInventory

SINK_TYPES = [InboundForecastSink,UpdateInventory]


class TargetMontapacking(Target):
    """Sample target for Montapacking."""

    name = "target-montapacking"
    config_jsonschema = th.PropertiesList(
        th.Property("username", th.StringType),
        th.Property("password", th.StringType),
    ).to_dict()

    def get_sink_class(self, stream_name: str) -> Type[Sink]:
        """Get sink for a stream."""
        return next(
            (
                sink_class
                for sink_class in SINK_TYPES
                if sink_class.name.lower() == stream_name.lower()
            ),
            None,
        )


if __name__ == "__main__":
    TargetMontapacking.cli()
