from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import json
from .util import MonthlyProduction

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
        # delete all monthly_production records linked ot this zone
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
            try:
                if pvgis_data["status"] == 200:
                    for i in range(len(pvgis_data['outputs']['monthly']['fixed'])):
                        self.env['spqm.installation.monthly_production'].create()
                        E_m_values.append(pvgis_data['outputs']['monthly']['fixed'][i]['E_m'])
                    record.monthly_production = MonthlyProduction(E_m_values).to_bytes()
                    record.e_m_average = pvgis_data['outputs']['totals']['fixed']['E_m']
                else:
                    raise UserError(f"Status code: {pvgis_data['status']}\nMessage: {pvgis_data['message']}")
            except KeyError as e:
                # print(f"pvgis json: \n\n{pvgis_data}\n\n")
                raise KeyError(f"pvgis json: \n\n{pvgis_data}\n\n")
            record.e_y_total = pvgis_data['outputs']['totals']['fixed']['E_y']
