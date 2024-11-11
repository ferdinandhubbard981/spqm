from odoo import models, fields, api
from .util import MonthlyProduction, YearlyData, Product, ProductEntry
import jsonpickle


class Installation(models.Model):
    _name = "spqm.installation"
    _description = "Represents all the data from a solar panel installation site to generate a quote"

    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)

    # inputs
    # inverter_type = fields.Selection([("micro_inverter", "Micro Inverter"), ("inverter", "Inverter")], required=True, string="Inverter Type")
    selected_years = fields.Json(default=lambda self: jsonpickle.dumps([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 19, 24]))
    computed_year_count = fields.Integer(default=25)
    name = fields.Char(required=True)
    client_id = fields.Many2one("res.partner", string="Client")
    worksite_address = fields.Char(readonly=False)
    billing_address = fields.Char(readonly=False)
    zone_ids = fields.One2many("spqm.installation.zone", "installation_id", required=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    start_year = fields.Integer(required=True)
    elec_price_buy_today_HT = fields.Float(required=True, help="The buying price of electricity in €/kWh excluding tax")
    elec_price_sell_today_HT = fields.Float(required=True, help="The selling price of electricity in €/kWh excluding tax")
    elecVAT = fields.Float(required=True, help="the VAT of electricity as a %", default=6)
    elec_price_inflation = fields.Float(required=True, default=3)
    auto_consumption_rate = fields.Float(help="the percentage of the electricity produced that is used on site")
    offer_validity = fields.Date(help="date after which the offer will be invalid")

    # quote-relevant fields
    peak_power = fields.Float(help="The cumulated peak power of all the zones, in kW")
    cost_per_watt = fields.Float(help="the client cost per watt of peak power from the solar panels")
    total_investment = fields.Float(help="represents the total investment that the client would make into the installation")
    return_on_investment = fields.Float(help="client's ROI in years")
    product_entries = fields.Json(help="the products that are in the quote. These are aggregated from various other fields on the Installation model")
    elec_price_buy_today = fields.Float(compute="_compute_elec_price_buy_today")
    elec_price_sell_today = fields.Float(compute="_compute_elec_price_sell_today")
    monthly_production_list = fields.Json(help="the sum of the monthly production data of all zones, used to plot a graph of production/month")
    yearly_data = fields.Json(help="financial data regarding the installation for x years post-installation")
    cumulated_yearly_data = fields.Json(help="totals of yearly_data")
    # short_year_list = fields.Float(readonly=True, help="list of years to be displayed in table")
    # production_total = fields.Float(readonly=True)
    # production_consumed_total = fields.Float(readonly=True)
    # production_sold_total = fields.Float(readonly=True)
    # elec_economy_total = fields.Float(readonly=True)
    # elec_gain_total = fields.Float(readonly=True)
    # spending_total = fields.Float(readonly=True)

    @api.onchange('client_id')
    def _onchange_address(self):
        for record in self:
            record.worksite_address = record.client_id.contact_address
            record.billing_address = record.client_id.contact_address

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
            for zone in record.zone_ids:
                zone_monthly_production_list_list.append(jsonpickle.loads((zone.monthly_production_list)))
            monthly_production_list = []
            for i in range(12):
                monthly_production_list_for_this_month = []
                for zone_monthly_production_list in zone_monthly_production_list_list:
                    monthly_production_list_for_this_month.append(zone_monthly_production_list[i])
                monthly_production = MonthlyProduction.from_list_of_monthly_productions(monthly_production_list_for_this_month)
                monthly_production_list.append(monthly_production)

            record.monthly_production_list = jsonpickle.dumps(monthly_production_list)

    def _compute_products(self):
        for record in self:
            product_entries = []
            for zone in record.zone_ids:
                product = Product(zone.solar_panel_id.name, zone.solar_panel_id.price)
                product_entry = ProductEntry(product, zone.solar_panel_quantity)
                product_entries.append(product_entry)
            record.product_entries = jsonpickle.dumps(product_entries)

    def _compute_total_investment(self):
        for record in self:
            total_investment = 0
            product_entries = record.get_product_entries()
            for entry in product_entries:
                total_investment += entry.total
            record.total_investment = total_investment

    def _compute_ROI(self):
        # call after _compute_yearly_data
        for record in self:
            yearly_data = record.get_yearly_data()
            for i, year in enumerate(yearly_data):
                if year.cumulated_total < 0:
                    continue
                if i == 0:
                    record.return_on_investment = 0
                    break
                difference = yearly_data[i].cumulated_total - yearly_data[i - 1].cumulated_total
                ROI_point = abs(yearly_data[i - 1].cumulated_total)
                decimals = ROI_point / difference
                return_on_investment = year.years_since_installation + decimals
                record.return_on_investment = return_on_investment
                break

    def _compute_peak_power(self):
        for record in self:
            peak_power = 0
            for zone in record.zone_ids:
                peak_power += zone.solar_panel_id.peak_power * zone.solar_panel_quantity
            record.peak_power = peak_power

    def _compute_cost_per_watt(self):
        for record in self:
            record.cost_per_watt = record.total_investment / (record.peak_power * 1000)

    def _compute_yearly_data(self):
        for record in self:
            yearly_data = []
            cumulated_total = 0
            for year in range(record.start_year, record.start_year + record.computed_year_count):
                years_installed = year - record.start_year

                current_year = YearlyData(year, record.start_year)
                current_year.elec_price_buy = record.elec_price_buy_today_HT * (1 + record.elec_price_inflation / 100) ** years_installed * (1 + record.elecVAT / 100)
                current_year.elec_price_sell = record.elec_price_sell_today_HT * (1 + record.elec_price_inflation / 100) ** years_installed * (1 + record.elecVAT / 100)
                production = 0
                for zone in record.zone_ids:
                    zone_production = zone.e_y_total * (1 - zone.solar_panel_id.module_degradation_in_first_year / 100) ** min(years_installed, 1) * (1 - zone.solar_panel_id.module_degradation_for_subsequent_years / 100) ** max((years_installed - 1), 0)  # TODO double-check this math

                    production += zone_production

                current_year.production = production
                # current_year.production = record.e_y_total * (1 - record.module_degradation_year / 100) ** years_installed
                current_year.consumed = current_year.production * record.auto_consumption_rate / 100
                current_year.elec_economy = current_year.consumed * current_year.elec_price_buy
                current_year.production_sold = current_year.production - current_year.consumed
                current_year.elec_gain = current_year.production_sold * current_year.elec_price_sell
                current_year.expenses = 0
                if years_installed == 0:
                    current_year.expenses += record.total_investment
                current_year.total_gain = current_year.elec_economy + current_year.elec_gain - current_year.expenses
                cumulated_total += current_year.total_gain
                current_year.cumulated_total = cumulated_total
                yearly_data.append(current_year)

            record.yearly_data = jsonpickle.dumps(yearly_data)

    def _compute_cumulated_yearly_data(self):
        for record in self:
            cumulated_yearly_data = YearlyData(-1, 0)
            yearly_data = record.get_yearly_data()
            for data in yearly_data:
                cumulated_yearly_data.production += data.production
                cumulated_yearly_data.consumed += data.consumed
                cumulated_yearly_data.elec_economy += data.elec_economy
                cumulated_yearly_data.production_sold += data.production_sold
                cumulated_yearly_data.elec_gain += data.elec_gain
                cumulated_yearly_data.expenses += data.expenses
                cumulated_yearly_data.total_gain += data.total_gain
            cumulated_yearly_data.cumulated_total = yearly_data[len(yearly_data) - 1].cumulated_total
            record.cumulated_yearly_data = jsonpickle.dumps(cumulated_yearly_data)

    def get_selected_years(self):
        return jsonpickle.loads(self.selected_years)

    def get_yearly_data(self):
        return jsonpickle.loads(self.yearly_data)

    def get_cumulated_yearly_data(self):
        return jsonpickle.loads(self.cumulated_yearly_data)

    def get_monthly_production_list(self):
        return jsonpickle.loads(self.monthly_production_list)

    def get_product_entries(self):
        return jsonpickle.loads(self.product_entries)

    def action_generate_quote(self):
        for zone in self.zone_ids:
            zone._compute_pvgis()
        self._compute_monthly_production()
        self._compute_products()
        self._compute_total_investment()
        self._compute_yearly_data()
        self._compute_cumulated_yearly_data()
        self._compute_ROI()
        self._compute_peak_power()
        self._compute_cost_per_watt()
        return self.env.ref("spqm.action_report_spqm_installation").report_action(self)
