from odoo import models, fields


class Panel(models.Model):
    _name = "spqm.solar_panel"
    _description = "describes a solar panel"
    name = fields.Char()
    price = fields.Float()
    peak_power = fields.Float(help="peak power production solar panel in kW")
    loss = fields.Float()
    module_degradation_in_first_year = fields.Float(default=5, help="The degradation in the first year of the solar panels as a % (of it's full capacity?)")
    module_degradation_for_subsequent_years = fields.Float(default=5, help="The degradation year-on-year (after the first year) of the solar panels as a % (of it's full capacity?)")
