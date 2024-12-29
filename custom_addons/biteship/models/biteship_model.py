import requests
from odoo import models, fields, _
from odoo.exceptions import UserError

class DeliveryCarrierBiteship(models.Model):
    _inherit = 'delivery.carrier'

    # Add Biteship to delivery_type options
    delivery_type = fields.Selection(
        selection_add=[('biteship', 'Biteship')],
        ondelete={'biteship': 'set default'}
    )
    biteship_api_key = fields.Char(string="Biteship API Key", help="API Key for Biteship API")

    apply_to_all_products = fields.Boolean(string="Apply to All Products", default=True)

    def _compute_delivery_cost(self, order):
        """Override method to apply delivery cost to all products."""
        self.ensure_one()
        if self.apply_to_all_products:
            # Custom logic to compute rates for all products
            total_cost = sum(line.product_id.weight for line in order.order_line) * 100  # Example logic
            return total_cost
        return super()._compute_delivery_cost(order)

    def biteship_rate_shipment(self, order):
        """Fetch shipping rates from Biteship API."""
        self.ensure_one()
        if not self.biteship_api_key:
            raise UserError(_("Biteship API key is missing in the delivery carrier configuration."))

        # Prepare request to Biteship
        url = "https://api.biteship.com/v1/rates/couriers"
        headers = {
            "Authorization": f"Bearer {self.biteship_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "origin": {"area_id": "example_origin"},  # Replace with actual origin
            "destination": {"area_id": "example_destination"},  # Replace with actual destination
            "couriers": ["jne", "pos", "tiki"]  # Example courier list
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                raise UserError(_("Biteship API Error: %s") % response.text)

            rates = response.json()
            # Example: Assume the first rate is used
            rate = rates['pricing'][0]['price'] if rates.get('pricing') else 0
            return rate

        except Exception as e:
            raise UserError(_("Error fetching rates from Biteship: %s") % str(e))

    def biteship_send_shipping(self, pickings):
        """Send shipping information to Biteship."""
        self.ensure_one()
        if not self.biteship_api_key:
            raise UserError(_("Biteship API key is missing."))

        for picking in pickings:
            url = "https://api.biteship.com/v1/orders"
            headers = {
                "Authorization": f"Bearer {self.biteship_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "shipper_contact_name": "Warehouse Contact",
                "destination_contact_name": picking.partner_id.name,
                "courier_company": "jne",  # Replace with selected courier
                "origin_area_id": "origin_id",
                "destination_area_id": "destination_id",
                "items": [{"name": move.product_id.name, "quantity": move.quantity_done}]
            }
            try:
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code != 200:
                    raise UserError(_("Error sending shipping to Biteship: %s") % response.text)
                tracking_data = response.json()
                picking.write({'carrier_tracking_ref': tracking_data.get('order_id')})
            except Exception as e:
                raise UserError(_("Error sending shipping request: %s") % str(e))

    def biteship_get_tracking_link(self, picking):
        """Return tracking URL for the Biteship order."""
        if picking.carrier_tracking_ref:
            return f"https://biteship.com/track/{picking.carrier_tracking_ref}"
        return ""

    def biteship_cancel_shipment(self, picking):
        """Cancel the shipment in Biteship."""
        self.ensure_one()
        if not self.biteship_api_key or not picking.carrier_tracking_ref:
            raise UserError(_("Missing API key or tracking reference."))

        url = f"https://api.biteship.com/v1/orders/{picking.carrier_tracking_ref}/cancel"
        headers = {"Authorization": f"Bearer {self.biteship_api_key}"}

        try:
            response = requests.post(url, headers=headers)
            if response.status_code != 200:
                raise UserError(_("Failed to cancel shipment: %s") % response.text)
        except Exception as e:
            raise UserError(_("Error cancelling shipment: %s") % str(e))
