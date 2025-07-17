from odoo import models, fields


class Panel(models.Model):
    _name = "spqm.solar_panel"
    _description = "describes a solar panel"
    name = fields.Char(required=True)
    peak_power = fields.Float(string="Peak power kWh", required=True, help="The peak power production of the solar panel in kW")
    module_degradation_in_first_year = fields.Float(string="Module degradation in first year %", required=True, default=1, help="The degradation in the first year of the solar panels as a % (of it's full capacity?)")
    module_degradation_for_subsequent_years = fields.Float(string="Module degradation for subsequent years %", required=True, default=0.4, help="The degradation year-on-year (after the first year) of the solar panels as a % (of it's full capacity?)")
