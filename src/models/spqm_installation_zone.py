from odoo import models, fields, api
import requests
import json


class Zone(models.Model):
    _name = "spqm.installation.zone"
    _description = "The zones of an installation site. Some installation sites have multiple solar panel installation zones with distinct data"
    installation_id = fields.Many2one("spqm.installation", required=True)
    peak_power = fields.Float()
    loss = fields.Float()
    slope = fields.Float()
    azimuth = fields.Float()

    e_m_value = fields.Json(compute="_compute_pvgis", readonly=True, help="electricity generated per month")
    e_m_average = fields.Float(compute="_compute_pvgis", readonly=True, help="average electricity generated per month")
    e_y_total = fields.Float(compute="_compute_pvgis", readonly=True, help="total electricity generated per year")

    @api.depends('installation_id.latitude', 'installation_id.longitude', 'peak_power', 'loss', 'slope', 'azimuth')
    def _compute_pvgis(self):
        for record in self:
            monthly_electricity_generated = []
            url = 'https://re.jrc.ec.europa.eu/api/v5_2/PVcalc'
            params = dict(
                lat=record.installatin_id.latitude,
                lon=record.installation_id.longitude,
                peakpower=record.peakPower,
                loss=record.loss,
                angle=record.slope,
                aspect=record.azimuth,
                outputformat='json'
            )
            response = requests.get(url=url, params=params)
            pvgis_data = response.json()
            for i in range(len(pvgis_data['outputs']['monthly']['fixed'])):
                monthly_electricity_generated.append(pvgis_data['outputs']['monthly']['fixed'][i]['E_m'])
            record.e_m_value = json.dumps(monthly_electricity_generated)
            record.e_m_average = pvgis_data['outputs']['totals']['fixed']['E_m']
            record.e_y_total = pvgis_data['outputs']['totals']['fixed']['E_y']
