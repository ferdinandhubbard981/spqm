class Product:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price


class ProductEntry:
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity
        self.total = product.price * quantity


class MonthlyProduction:
    def __init__(self, month_index, electricity_produced):
        # assumes that E_m_values is sorted in the order of the month each value belongs to (jan -> dec)
        self.month_index = month_index
        self.electricity_produced = electricity_produced

    def from_list_of_monthly_productions(monthly_production_list):
        # assumes all monthly_production in list are from same month in different installation zones
        month_index = monthly_production_list[0].month_index
        electricity_produced = 0
        for monthly_production in monthly_production_list:
            if monthly_production.month_index != month_index:
                raise Exception("month indexes don't match")
            electricity_produced += monthly_production.electricity_produced
        return MonthlyProduction(month_index, electricity_produced)

    def get_month_as_string(self):
        match self.month_index:
            case 0:
                return "January"
            case 1:
                return "February"
            case 2:
                return "March"
            case 3:
                return "April"
            case 4:
                return "May"
            case 5:
                return "June"
            case 6:
                return "July"
            case 7:
                return "August"
            case 8:
                return "September"
            case 9:
                return "October"
            case 10:
                return "November"
            case 11:
                return "December"


class YearlyData:
    def __init__(self, year):
        self.year = year
        self.production = 0.0
        self.consumed = 0.0
        self.elec_price_buy = 0.0
        self.elec_economy = 0.0
        self.production_sold = 0.0
        self.elec_price_sell = 0.0
        self.elec_gain = 0.0
        self.total_gain = 0.0
        self.cumulated_total = 0.0
        # self.prime = 0.0
        # self.certificat_vert_bxl = 0.0  # rebates from the brussels region
        # self.tarif_prosumer = 0.0
        # self.spending = 0.0
        # self.revenue = 0.0
        # self.revenue_cumulated = 0.0
