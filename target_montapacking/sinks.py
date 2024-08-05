"""Montapacking target sink class, which handles writing streams."""

from __future__ import annotations

from hotglue_models_ecommerce.ecommerce import SalesOrder

from target_montapacking.client import MontapackingSink


class InboundForecastSink(MontapackingSink):

    endpoint = "inbound_forecast"
    # unified_schema = SalesOrder  # Using SalesOrder
    name = "BuyOrders"
    endpoint = "inboundforecast/group"

    def process_record(self, record: dict, context: dict) -> None:

        # Try to create the Po
        line_items = self.parse_json(record.get("line_items", []))
        delivery_date = self.convert_datetime(record.get("created_at"))
        transaction_date = self.convert_datetime(record.get("transaction_date"))

        lines = [
            {
                "DeliveryDate": delivery_date,
                "Sku": i.get("sku"),
                "Quantity": i.get("quantity"),
            }
            for i in line_items
        ]

        mapping = {
            "Reference": str(record.get("id")),  # enforce id to be string
            "SupplierCode": record.get("customer_id"),
            "InboundForecasts": lines,
        }
        self.logger.info(f"DEBUG REQUEST: Method=[POST], endpoint=[{self.endpoint}], payload=[{mapping}]")
        resp = self.request_api("POST", endpoint=self.endpoint, request_data=mapping)

        self.logger.info(f"DEBUG RESPONSE: {resp.text}")

        # if "Reference already exists for another group" in resp.text:
        #     # if returns "Reference already exists for another group" then get the reference data
        #     new_lines = mapping.get("InboundForecasts", [])

        #     endpoint = f"{self.endpoint}/{record.get('id')}"
        #     order_to_update = self.get_data(endpoint=endpoint)
        #     lines_to_update = order_to_update.get("InboundForecasts", [])
        #     lines_to_update = {item["Sku"]: item for item in lines_to_update}

        #     for line in new_lines:
        #         # Perform the update line by line
        #         sku = line.get("Sku")
        #         endpoint_update = f"{endpoint}/{sku}"
        #         self.logger.info(f"DEBUG REQUEST: Method=[PUT], endpoint=[{endpoint}], payload=[{line}]")
        #         resp = self.request_api("PUT", endpoint=endpoint, request_data=line)

        return None


class UpdateInventory(MontapackingSink):

    endpoint = "update_inventory"
    name = "UpdateInventory"
    endpoint = "UpdateInventory"

    def process_record(self, record: dict, context: dict) -> None:
        return None