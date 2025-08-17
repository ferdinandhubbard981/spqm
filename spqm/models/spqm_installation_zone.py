from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
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
    # User-facing azimuth convention (compass): 0°=North, 90°=East, 180°=South, 270°=West
    azimuth = fields.Float(string="Azimuth (deg)", required=True, help="0°=North, 90°=East, 180°=South, 270°=West (must be in [0,360))")

    peak_power = fields.Float(string="Peak power kW", readonly=True, compute="_compute_peak_power", help="The peak power of this zone")
    monthly_production_list = fields.Json(readonly=True, help="Monthly electricity production data from solar panels used for plotting graph")
    e_y_total = fields.Float(string="Electricity generated in 1 year kWh", readonly=True, compute="_compute_pvgis", help="Total electricity generated per year, as reported by pvgis (not including module degradation)")

    @api.depends('solar_panel_id', 'solar_panel_quantity')
    def _compute_peak_power(self):
        for record in self:
            record.peak_power = record.solar_panel_id.peak_power * record.solar_panel_quantity

    @api.depends('installation_id.latitude', 'installation_id.longitude', 'installation_id.loss', 'peak_power', 'slope', 'azimuth')
    def _compute_pvgis(self):
        for record in self:
            if record.peak_power <= 0:
                record.e_y_total = 0
                continue
            url = 'https://re.jrc.ec.europa.eu/api/v5_2/PVcalc'
            params = dict(
                lat=record.installation_id.latitude,
                lon=record.installation_id.longitude,
                peakpower=record.solar_panel_id.peak_power * record.solar_panel_quantity,
                loss=record.installation_id.loss,
                angle=record.slope,
                # Map user compass azimuth to PVGIS convention (0=South, East negative, West positive)
                aspect=self._map_azimuth(record.azimuth),
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

    @staticmethod
    def _map_azimuth(azimuth):
        """
        Convert from user compass convention (0°=North, 90°=East, 180°=South, 270°=West)
        to PVGIS convention (0°=South, -90°=East, 90°=West, ±180°=North).

        Formula:
            PVGIS = user_azimuth - 180, normalized to [-180, 180]

        Examples:
            0   -> -180 (North)
            90  -> -90  (East)
            180 -> 0    (South)
            270 -> 90   (West)
        """
        if azimuth is None:
            return None
        # Normalize user azimuth first into [0, 360)
        user_norm = azimuth % 360
        pvgis = user_norm - 180  # Now in [-180, 180)
        # Ensure 180 edge case (if user_norm == 0 gives -180 which is acceptable)
        if pvgis == -180:
            # PVGIS accepts -180 (same as +180); keep as is.
            return pvgis
        return pvgis

    @api.constrains('azimuth')
    def _check_azimuth_range(self):
        for record in self:
            if record.azimuth is None or not (0 <= record.azimuth < 360):
                raise ValidationError("Azimuth must be >= 0 and < 360 degrees (compass convention: 0=N, 90=E, 180=S, 270=W).")
