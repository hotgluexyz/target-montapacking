"""Montapacking target sink class, which handles writing streams."""

from __future__ import annotations

from hotglue_models_ecommerce.ecommerce import SalesOrder

from target_montapacking.client import MontapackingSink


class PoSink(MontapackingSink):

    endpoint = "orders"
    unified_schema = SalesOrder
    name = SalesOrder.Stream.name
    endpoint = "inboundforecast/group"

    def process_record(self, record: dict, context: dict) -> None:

        # Try to create the Po

        lines = [
            {
                "DeliveryDate": record.get("created_at"),
                "Sku": i.get("sku"),
                "Quantity": i.get("quantity"),
            }
            for i in record.get("line_items", [])
        ]

        mapping = {
            "Reference": record.get("id"),
            "InboundForecasts": lines,
            # "Created": This fied is overrited by Montapacking API
            "DeliveryDate": record.get("created_at"),
        }

        resp = self.request_api("POST", endpoint=self.endpoint, request_data=mapping)

        if "Reference already exists for another group" in resp.text:
            # if returns "Reference already exists for another group" then get the reference data
            new_lines = mapping.get("InboundForecasts", [])

            endpoint = f"{self.endpoint}/{record.get('id')}"
            order_to_update = self.get_data(endpoint=endpoint)
            lines_to_update = order_to_update.get("InboundForecasts", [])
            lines_to_update = {item["Sku"]: item for item in lines_to_update}

            for line in new_lines:
                # Perform the update line by line
                sku = line.get("Sku")
                endpoint_update = f"{endpoint}/{sku}"
                resp = self.request_api("PUT", endpoint=endpoint, request_data=line)

        return None
