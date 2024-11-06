from odoo import models, fields, api
from .util import MonthlyProduction, YearlyData
import jsonpickle


class Installation(models.Model):
    _name = "spqm.installation"
    _description = "Represents all the data from a solar panel installation site to generate a quote"
    name = fields.Char(required=True)
    # client = fields.Many2one("res.partner", string="Client")

    # inputs
    # inverter_type = fields.Selection([("micro_inverter", "Micro Inverter"), ("inverter", "Inverter")], required=True, string="Inverter Type")
    zone_ids = fields.One2many("spqm.installation.zone", "installation_id", required=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    # region = fields.Selection([])
    start_year = fields.Integer(required=True)
    end_year = fields.Integer(required=True)
    elec_price_buy_today_HT = fields.Float(required=True, help="The buying price of electricity in €/kWh excluding tax")
    elec_price_sell_today_HT = fields.Float(required=True, help="The selling price of electricity in €/kWh excluding tax")
    elecVAT = fields.Float(required=True, help="the VAT of electricity as a %", default=6)
    elec_price_inflation = fields.Float(required=True, default=3)
    module_degradation_year = fields.Float(default=5, help="The degradation year-on-year of the solar panels as a % (of it's full capacity?)")
    auto_consumption_rate = fields.Float(help="the percentage of the electricity produced that is used on site")

    # quote-relevant fields
    elec_price_buy_today = fields.Float(compute="_compute_elec_price_buy_today")
    elec_price_sell_today = fields.Float(compute="_compute_elec_price_sell_today")
    monthly_production_list = fields.Json(help="the sum of the monthly production data of all zones, used to plot a graph of production/month")
    yearly_data = fields.Json(help="financial data regarding the installation for x years post-installation")
    # price_per_kw_cht = fields.Float(readonly=True)
    e_m_average = fields.Float(readonly=True)
    e_y_total = fields.Float(readonly=True, help="The base electricity generated in a year, which is used with module degradation to compute it for the other years.")
    # short_year_list = fields.Float(readonly=True, help="list of years to be displayed in table")
    # production_total = fields.Float(readonly=True)
    # production_consumed_total = fields.Float(readonly=True)
    # production_sold_total = fields.Float(readonly=True)
    # elec_economy_total = fields.Float(readonly=True)
    # elec_gain_total = fields.Float(readonly=True)
    # prime_total = fields.Float(readonly=True)
    # tarif_prosumer_total = fields.Float(readonly=True)
    # spending_total = fields.Float(readonly=True)
    # return_rate = fields.Float(readonly=True)
    # nbr_year_positive = fields.Float(readonly=True)


    @api.depends('elec_price_buy_today_HT', 'elecVAT')
    def _compute_elec_price_buy_today(self):
        for record in self:
            record.elec_price_buy_today = record.elec_price_buy_today_HT * (1 + record.elecVAT / 100.0)

    @api.depends('elec_price_sell_today_HT', 'elecVAT')
    def _compute_elec_price_sell_today(self):
        for record in self:
            record.elec_price_sell_today = record.elec_price_sell_today_HT * (1 + record.elecVAT / 100.0)

    @api.depends('zone_ids')
    def _compute_monthly_production(self):
        for record in self:
            zone_monthly_production_list_list = []
            e_m_average_cumulated = 0
            e_y_total_cumulated = 0
            for zone in record.zone_ids:
                zone_monthly_production_list_list.append(jsonpickle.loads((zone.monthly_production_list)))
                e_m_average_cumulated += zone.e_m_average
                e_y_total_cumulated = zone.e_y_total
            monthly_production_list = []
            for i in range(12):
                monthly_production_list_for_this_month = []
                for zone_monthly_production_list in zone_monthly_production_list_list:
                    monthly_production_list_for_this_month.append(zone_monthly_production_list[i])
                monthly_production = MonthlyProduction.from_list_of_monthly_productions(monthly_production_list_for_this_month)
                monthly_production_list.append(monthly_production)

            record.monthly_production_list = jsonpickle.dumps(monthly_production_list)
            record.e_m_average = e_m_average_cumulated
            record.e_y_total = e_y_total_cumulated


    def _compute_yearly_data(self):
        for record in self:
            yearly_data = []
            cumulated_total = 0
            for year in range(record.start_year, record.end_year):
                years_installed = year - record.start_year
                current_year = YearlyData(year)
                current_year.elec_price_buy = record.elec_price_buy_today_HT * (1 + record.elec_price_inflation / 100) ** years_installed * (1 + record.elecVAT / 100)
                current_year.elec_price_sell = record.elec_price_sell_today_HT * (1 + record.elec_price_inflation / 100) ** years_installed * (1 + record.elecVAT / 100)
                current_year.production = record.e_y_total * (1 - record.module_degradation_year / 100) ** years_installed
                current_year.consumed = current_year.production * record.auto_consumption_rate / 100
                current_year.elec_economy = current_year.consumed * current_year.elec_price_buy
                current_year.production_sold = current_year.production - current_year.consumed
                current_year.elec_gain = current_year.production_sold * current_year.elec_price_sell
                current_year.total_gain = current_year.elec_economy + current_year.elec_gain
                cumulated_total += current_year.total_gain
                current_year.cumulated_total = cumulated_total
                yearly_data.append(current_year)

            record.yearly_data = jsonpickle.dumps(yearly_data)

    def get_yearly_data(self):
        return jsonpickle.loads(self.yearly_data)

    def get_monthly_production_list(self):
        return jsonpickle.loads(self.monthly_production_list)

    def action_generate_quote(self):
        for zone in self.zone_ids:
            zone._compute_pvgis()
        self._compute_monthly_production()
        self._compute_yearly_data()
        return self.env.ref("spqm.action_report_spqm_installation").report_action(self)
