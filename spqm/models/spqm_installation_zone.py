from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
from .util import MonthlyProduction
import jsonpickle


class Zone(models.Model):
    _name = "spqm.installation.zone"
    _description = "The zones of an installation site. Some installation sites have multiple solar panel installation zones with distinct data"
    installation_id = fields.Many2one("spqm.installation", required=True, ondelete="cascade")
    solar_panel_id = fields.Many2one("spqm.solar_panel", required=True)
    solar_panel_quantity = fields.Integer(required=True)
    slope = fields.Float(string="Slope (deg)", required=True)
    azimuth = fields.Float(string="Azimuth (deg)", required=True, help="South=0°, West=90°, East=-90°, north=+-180°")
    product_entry_ids = fields.One2many("spqm.product_entry", "zone_id")

    peak_power = fields.Float(string="Peak power kW", readonly=True, compute="_compute_peak_power", help="The peak power of this zone")
    monthly_production_list = fields.Json(help="Monthly electricity production data from solar panels used for plotting graph")
    e_y_total = fields.Float(string="Electricity generated in 1 year kWh", readonly=True, compute="_compute_pvgis", help="Total electricity generated per year, as reported by pvgis (not including module degradation)")

    @api.depends('solar_panel_id', 'solar_panel_quantity')
    def _compute_peak_power(self):
        for record in self:
            record.peak_power = record.solar_panel_id.peak_power * record.solar_panel_quantity

    @api.depends('installation_id.latitude', 'installation_id.longitude', 'installation_id.loss', 'peak_power', 'slope', 'azimuth')
    def _compute_pvgis(self):
        for record in self:
            url = 'https://re.jrc.ec.europa.eu/api/v5_2/PVcalc'
            params = dict(
                lat=record.installation_id.latitude,
                lon=record.installation_id.longitude,
                peakpower=record.solar_panel_id.peak_power * record.solar_panel_quantity,
                loss=record.installation_id.loss,
                angle=record.slope,
                aspect=record.azimuth,
                outputformat='json'
            )
            response = requests.get(url=url, params=params)
            pvgis_data = response.json()
            if "status" in pvgis_data:
                raise UserError(f"Status code: {pvgis_data['status']}\nMessage: {pvgis_data['message']}")
            else:
                monthly_production_list = []
                for i in range(len(pvgis_data['outputs']['monthly']['fixed'])):
                    monthly_production = MonthlyProduction(i, pvgis_data['outputs']['monthly']['fixed'][i]['E_m'])
                    monthly_production_list.append(monthly_production)
                record.monthly_production_list = jsonpickle.dumps(monthly_production_list)
                record.e_y_total = pvgis_data['outputs']['totals']['fixed']['E_y']
