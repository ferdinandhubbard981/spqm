from odoo import models, fields
# WORK IN PROGRESS


class Region(models.Model):
    _name = "spqm.installation.region"
    _description = "region where the solar panels are being installed"

    postcode = fields.Integer()
    region_name = fields.Char()
    GRD = fields.Char()
    tarif_prosumer = fields.Json()
