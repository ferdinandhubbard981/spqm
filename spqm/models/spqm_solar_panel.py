from odoo import models, fields


class Panel(models.Model):
    _name = "spqm.solar_panel"
    _description = "describes a solar panel"
    name = fields.Char()
    price = fields.Float()
    peak_power = fields.Float()
