from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
from .util import MonthlyProduction
import jsonpickle


class Zone(models.Model):
    _name = "spqm.installation.zone"
    _description = "The zones of an installation site. Some installation sites have multiple solar panel installation zones with distinct data"
    installation_id = fields.Many2one("spqm.installation", required=True, ondelete="cascade")
    peak_power = fields.Float()
    loss = fields.Float()
    slope = fields.Float()
    azimuth = fields.Float()

    monthly_production = fields.Json(help="monthly electricity production data from solar panels used for plotting graph")
    e_m_average = fields.Float(readonly=True, help="average electricity generated per month")
    e_y_total = fields.Float(readonly=True, help="total electricity generated per year")

    @api.depends('installation_id.latitude', 'installation_id.longitude', 'peak_power', 'loss', 'slope', 'azimuth')
    def _compute_pvgis(self):
        for record in self:
            if record.peak_power == 0:
                continue
            E_m_values = []
            url = 'https://re.jrc.ec.europa.eu/api/v5_2/PVcalc'
            params = dict(
                lat=record.installation_id.latitude,
                lon=record.installation_id.longitude,
                peakpower=record.peak_power,
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
                for i in range(len(pvgis_data['outputs']['monthly']['fixed'])):
                    E_m_values.append(pvgis_data['outputs']['monthly']['fixed'][i]['E_m'])
                record.monthly_production = jsonpickle.dumps(MonthlyProduction(E_m_values))
                record.e_m_average = pvgis_data['outputs']['totals']['fixed']['E_m']
                record.e_y_total = pvgis_data['outputs']['totals']['fixed']['E_y']
