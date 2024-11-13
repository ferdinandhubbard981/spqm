from odoo import models, fields


class ProductEntry(models.Model):
    _name = "spqm.product_entry"
    _description = "Product entry in zones"

    zone_id = fields.Many2one("spqm.installation.zone", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product")
    quantity = fields.Integer()
    vat = fields.Float()
    total = fields.Float()
