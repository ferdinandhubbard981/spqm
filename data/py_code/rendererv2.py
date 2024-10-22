import base64
import logging
from abc import ABC, abstractmethod

from jinja2 import Environment, PackageLoader

from babel import Locale
from babel.numbers import decimal

import json
import os
from selenium import webdriver

loader = PackageLoader("GrapheTool", "templates")
# default true for security concern of XSS. See bandit B701.
env = Environment(loader=loader, autoescape=True)


class BaseRenderer(ABC):
    def __init__(self, content_model):
        self.content = content_model
        self.rendered_report = None

        self.rendered = None

        self._render()

    @abstractmethod
    def _render(self):
        pass


class Renderer(BaseRenderer):
    def _render(self):
        html_template = env.get_template("graphev2.html")

        content = self.content
        # hosting all tags that will be applied to the jinja2 target string
        tag_all = {
            # map to remove decimal

            "filename": content['filename'],
            "outputFolder": content['outputFolder'],
            "charset": content['charset'],
            "peakPower": content['peakPower'] * 1000,


            "region": content['region'],
            "inverterType": content['inverterType'],

            "elecPriceBuyToday": content['elecPriceBuyTodayHT'] * content['elecVAT'],
            "elecPriceSellToday": content['elecPriceSellTodayHT'] * content['elecVAT'],
            "elecPriceInflation": content['elecPriceInflation'],

            "moduleDegradationYear": content['moduleDegradationYear'],
            "autoconsommationRate": content['autoconsommationRate'],
            "certificatVertBXL": content['certificatVertBXL'],

            "PricePerkWcHT": content['PricePerkWcHT'],

            "E_m_month": content['month'],

            "E_m_value": content['E_m_value'],
            "E_m_average": content['E_m_average'],
            "E_y_total": content['E_y_total'],



            "shortYearList": content['shortYearList'],
            "year": content['year'],

            "production": list(map(int, content['production'])),
            "productionConsummed": list(map(int, content['productionConsummed'])),
            "productionSold": list(map(int, content['productionSold'])),
            "elecPriceBuy": content['elecPriceBuy'],
            "elecEconomy": list(map(int, content['elecEconomy'])),
            "elecPriceSell": content['elecPriceSell'],
            "elecGain": list(map(int, content['elecGain'])),
            "prime": list(map(int, content['prime'])),
            "tarifProsumer": content['tarifProsumer'],
            "spending": content['spending'],
            "revenue": list(map(int, content['revenue'])),
            "revenueCumulated": list(map(int, content['revenueCumulated'])),

            "productionTotal": content['productionTotal'],
            "productionConsummedTotal": content['productionConsummedTotal'],
            "productionSoldTotal": content['productionSoldTotal'],
            "elecEconomyTotal": content['elecEconomyTotal'],
            "elecGainTotal": content['elecGainTotal'],
            "primeTotal": content['primeTotal'],
            "tarifProsumerTotal": content['tarifProsumerTotal'],
            "spendingTotal": content['spendingTotal'],
            "returnRate": content['returnRate'],
            "nbrYearPositive": content['nbrYearPositive']

        }

        # reuse jinja2 env to get absolute file path of the css
        with open(env.get_template("styles.css").filename, "r") as fhandler:
            css = fhandler.read()
            tag_all.update({"css": css})

        self.rendered = html_template.render(**tag_all)

    def dump(self, outputFolder, filename):
        with open("./" + outputFolder + "/" + filename + ".html", "w") as fhandler:
            fhandler.write(self.rendered)
         # setting html path

        htmlPath = os.getcwd() + "\\" + outputFolder + "\\" + filename + ".html"
        addr = "file:///" + htmlPath

        # setting Chrome Driver
        chromeOpt = webdriver.ChromeOptions()
        appState = {
            "recentDestinations": [
                {
                    "id": "Save as PDF",
                    "origin": "local",
                    "account": ""
                }
            ],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        }
        print(os.getcwd())

        prefs = {
            'printing.print_preview_sticky_settings.appState': json.dumps(appState),
            'download.default_directory': os.getcwd()
        }
        chromeOpt.add_experimental_option('prefs', prefs)
        chromeOpt.add_argument('--kiosk-printing')

        if os.name == "posix":
            chromedriver = "./chromedriver"
        else:
            chromedriver = "./chromedriver.exe"

        driver = webdriver.Chrome(executable_path=chromedriver, options=chromeOpt)

        # HTML open and print
        driver.get(addr)
        driver.execute_script('return window.print()')
