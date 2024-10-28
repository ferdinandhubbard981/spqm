from odoo import models, fields


class Installation(models.Model):
    _name = "spqm.installation"
    _description = "Represents all the data from a solar panel installation site to generate a quote"
    client = fields.Many2one("res.partner", string="Client")
    zone_ids = fields.One2many("spqm.installation.zone", "installation_id")
    latitude = fields.Float()
    longitude = fields.Float()

    # quote-relevant fields
    peak_power = fields.Float(readonly=True, compute="_compute_peak_power")
    region = fields.Selection([], readonly=True)
    inverter_type = fields.Selection([], readonly=True)
    elec_price_buy_today = fields.Float(readonly=True)
    elec_price_sell_today = fields.Float(readonly=True)
    elec_price_inflation = fields.Float(readonly=True)
    module_degradation_year = fields.Float(readonly=True)
    auto_consommation_rate = fields.Float(readonly=True)
    certificat_vert_bxl = fields.Float(readonly=True)
    price_per_kw_cht = fields.Float(readonly=True)
    E_m_month = fields.Float(readonly=True)
    E_m_value = fields.Float(readonly=True)
    E_m_average = fields.Float(readonly=True)
    E_y_total = fields.Float(readonly=True)
    short_year_list = fields.Float(readonly=True)
    year = fields.Integer(readonly=True)
    production = fields.Float(readonly=True)
    production_consumed = fields.Float(readonly=True)
    production_sold = fields.Float(readonly=True)
    elec_price_buy = fields.Float(readonly=True)
    elec_economy = fields.Float(readonly=True)
    elec_price_sell = fields.Float(readonly=True)
    elec_gain = fields.Float(readonly=True)
    prime = fields.Float(readonly=True)
    tarif_prosumer = fields.Float(readonly=True)
    spending = fields.Float(readonly=True)
    revenue = fields.Float(readonly=True)
    revenue_cumulated = fields.Float(readonly=True)
    production_total = fields.Float(readonly=True)
    production_consumed_total = fields.Float(readonly=True)
    production_sold_total = fields.Float(readonly=True)
    elec_economy_total = fields.Float(readonly=True)
    elec_gain_total = fields.Float(readonly=True)
    prime_total = fields.Float(readonly=True)
    tarif_prosumer_total = fields.Float(readonly=True)
    spending_total = fields.Float(readonly=True)
    return_rate = fields.Float(readonly=True)
    nbr_year_positive = fields.Float(readonly=True)

    def _compute_peak_power(self):
        for record in self:
            peak_power = 0
            for zone in record.zone_ids:
                peak_power += zone.peak_power
            record.peak_power = peak_power
