class MonthlyProduction():
    def __init__(self, E_m_values):
        # assumes that E_m_values is sorted in the order of the month each value belongs to (jan -> dec)
        self.E_m_values = {}
        for i, val in enumerate(E_m_values):
            self.E_m_values[i] = val

    def from_list_of_monthly_productions(monthly_production_list):
        E_m_values = [0] * 12
        for monthly_production in monthly_production_list:
            for i, val in monthly_production.E_m_values.values():
                E_m_values[i] += val
        return MonthlyProduction(E_m_values)


class YearlyData:
    def __init__(self, year):
        self.year = year
        self.production = 0.0
        self.consumed = 0.0
        self.elec_price_buy = 0.0
        # self.elec_economy = 0.0
        # self.production_sold = 0.0
        self.elec_price_sell = 0.0
        # self.elec_gain = 0.0
        # self.prime = 0.0
        # self.certificat_vert_bxl = 0.0  # rebates from the brussels region
        # self.tarif_prosumer = 0.0
        # self.spending = 0.0
        # self.revenue = 0.0
        # self.revenue_cumulated = 0.0
