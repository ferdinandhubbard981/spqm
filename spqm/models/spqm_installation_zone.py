from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
from .util import MonthlyProduction
import jsonpickle


class Zone(models.Model):
    _name = "spqm.installation.zone"
    _description = "The zones of an installation site. Some installation sites have multiple solar panel installation zones with distinct data"
    installation_id = fields.Many2one("spqm.installation", required=True, ondelete="cascade")
    solar_panel_id = fields.Many2one("spqm.solar_panel")
    solar_panel_quantity = fields.Integer()
    loss = fields.Float()
    slope = fields.Float()
    azimuth = fields.Float()

    monthly_production_list = fields.Json(help="monthly electricity production data from solar panels used for plotting graph")
    e_m_average = fields.Float(readonly=True, help="average electricity generated per month")
    e_y_total = fields.Float(readonly=True, help="total electricity generated per year")

    @api.depends('installation_id.latitude', 'installation_id.longitude', 'peak_power', 'loss', 'slope', 'azimuth')
    def _compute_pvgis(self):
        for record in self:
            url = 'https://re.jrc.ec.europa.eu/api/v5_2/PVcalc'
            params = dict(
                lat=record.installation_id.latitude,
                lon=record.installation_id.longitude,
                peakpower=record.solar_panel_id.peak_power * record.solar_panel_quantity,
                loss=record.loss,
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
                record.e_m_average = pvgis_data['outputs']['totals']['fixed']['E_m']
                record.e_y_total = pvgis_data['outputs']['totals']['fixed']['E_y']
