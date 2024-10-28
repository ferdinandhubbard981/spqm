from odoo import models, fields


class Zone(models.Model):
    _name = "spqm.installation.zone"
    _description = "The zones of an installation site. Some installation sites have multiple solar panel installation zones with distinct data"
    installation_id = fields.Many2one("spqm.installation", required=True)
    peak_power = fields.Float()
    slope = fields.Float()
    azimuth = fields.Float()
    pvgis = fields.Float(readonly=True)
