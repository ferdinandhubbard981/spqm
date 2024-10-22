# -*- coding: utf-8 -*-
import argparse
from turtle import color
import yaml
import logging
import math
import os

import rendererv2
from geopy.geocoders import Nominatim
import requests
import plotly.graph_objects as go

import numpy as np
from PIL import Image, ImageOps
import locale


def read_content_yaml(content_file):
    with open(content_file, "r") as stream:
        try:
            return yaml.safe_load(stream)

        except yaml.YAMLError as e:
            logging.critical(e)


def getRegion(cp):
    # 1000-1299 : BXL : Région de Bruxelles-Capitale
    # 1300–1499 : WAL:  Province du Brabant wallon
    # 1500–1999 : FLA :  Province du Brabant flamand (arrondissement de Hal-Vilvorde, sauf Overijse)
    # 2000–2999 : FLA : Province d'Anvers
    # 3000–3499 : FLA :  Province du Brabant flamand (arrondissement de Louvain, plus Overijse)
    # 3500–3999 : FLA : Province de Limbourg
    # 4000–4999 : WAL:  Province de Liège
    # 5000–5680 : WAL : Province de Namur
    # 6000–6599 : WAL : Province de Hainaut
    # 6600–6999 : WAL : Province de Luxembourg
    # 7000–7999 : WAL : Province de Hainaut
    # 8000–8999 : FLA : Province de Flandre-Occidentale
    # 9000–9999 : FLA :  Province de Flandre-Orientale

    # BXL
    if (1000 <= cp <= 1299):
        print("Région: Bruxelles")
        return "BXL"
    elif ((1300 <= cp <= 1499) or (4000 <= cp <= 7999)):
        print("Région: Wallonie")
        return "WAL"
    elif ((1500 <= cp <= 3999) or (8000 <= cp <= 9999)):
        print("Région: Flandre")
        return "FLA"
    else:
        print("the given postal code", cp, " is not right")
        exit()
    return 0


def getGRD(cp):

    AIEG = [5300, 5300, 5300, 5300, 5300, 5300, 5300, 5300, 5300, 5300, 5340, 5340, 5340, 5340, 5340, 5350, 5350, 5351, 5352, 5353, 5354, 5670, 5670, 5670, 5670, 5670, 5670, 5670, 5670, 5670, 7610, 7611, 7618]
    AIESH = [5660, 5660, 5660, 5660, 5660, 5660, 5660, 5660, 5660, 6440, 6440, 6440, 6440, 6441, 6460, 6460, 6460, 6460, 6460, 6460, 6461, 6462, 6463, 6464, 6464, 6464, 6464, 6464, 6470, 6470, 6470, 6470, 6470, 6470, 6500, 6500, 6500, 6500, 6500, 6500, 6500, 6511, 6590, 6591, 6592, 6593, 6594, 6596, 6596]
    ORES_BRABANT_WALLON = [1310, 1315, 1315, 1315, 1315, 1315, 1320, 1320, 1320, 1320, 1320, 1325, 1325, 1325, 1325, 1325, 1330, 1331, 1332, 1340, 1340, 1341, 1342, 1348, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1357, 1357, 1357, 1357, 1360, 1360, 1360, 1360, 1360, 1367, 1367, 1367, 1367, 1367, 1367, 1367, 1367, 1370, 1370, 1370, 1370, 1370, 1370, 1370, 1370, 1370, 1370, 1380, 1380, 1380, 1380, 1380, 1380, 1390, 1390, 1390, 1390, 1390, 1400, 1400, 1401, 1402, 1404, 1410, 1420, 1421, 1428, 1430, 1430, 1430, 1430, 1430, 1435, 1435, 1435, 1440, 1440, 1450, 1450, 1450, 1450, 1450, 1457, 1457, 1457, 1457, 1460, 1460, 1461, 1470, 1470, 1470, 1471, 1472, 1473, 1474, 1476, 1480, 1480, 1480, 1480, 1490, 1495, 1495, 1495, 1495, 1495, 4287, 4287, 4287, 7090, 7090, 7090, 7090, 7090, 7090, 7190, 7190, 7190, 7191]
    ORES_EST = [4700, 4701, 4710, 4711, 4720, 4721, 4728, 4730, 4730, 4731, 4750, 4750, 4760, 4760, 4761, 4770, 4770, 4770, 4771, 4780, 4780, 4782, 4783, 4784, 4790, 4790, 4791, 4850, 4850, 4850, 4851, 4851, 4852, 4950, 4950, 4950, 4950, 4960, 4960, 4960]
    ORES_HAINAUT = [6000, 6001, 6010, 6020, 6030, 6030, 6031, 6032, 6040, 6041, 6042, 6043, 6044, 6060, 6061, 6110, 6111, 6120, 6120, 6120, 6120, 6120, 6120, 6140, 6141, 6142, 6150, 6180, 6181, 6182, 6183, 6200, 6200, 6200, 6220, 6220, 6220, 6220, 6221, 6222, 6223, 6224, 6230, 6230, 6230, 6230, 6230, 6238, 6238, 6240, 6240, 6250, 6250, 6250, 6250, 6250, 6530, 6530, 6531, 6532, 6533, 6534, 6536, 6536, 6540, 6540, 6542, 6543, 6560, 6560, 6560, 6560, 6560, 6560, 6567, 6567, 6567, 6567, 7000, 7000, 7011, 7012, 7012, 7020, 7020, 7020, 7021, 7022, 7022, 7022, 7022, 7022, 7024, 7030, 7031, 7032, 7033, 7034, 7034, 7040, 7040, 7040, 7040, 7040, 7040, 7040, 7040, 7040, 7041, 7041, 7050, 7050, 7050, 7050, 7050, 7050, 7060, 7060, 7061, 7061, 7062, 7063, 7063, 7070, 7070, 7070, 7070, 7070, 7080, 7080, 7080, 7080, 7080, 7100, 7100, 7100, 7100, 7100, 7110, 7110, 7110, 7110, 7110, 7120, 7120, 7120, 7120, 7120, 7120, 7120, 7120, 7120, 7120, 7130, 7130, 7130, 7131, 7133, 7134, 7134, 7134, 7134, 7140, 7140, 7141, 7141, 7160, 7160, 7160, 7170, 7170, 7170, 7170, 7170, 7180, 7181, 7181, 7181, 7181, 7300, 7301, 7320, 7321, 7321, 7322, 7322, 7330, 7331, 7332, 7332, 7333, 7334, 7334, 7340, 7340, 7340, 7340, 7350, 7350, 7350, 7350, 7370, 7370, 7370, 7370, 7380, 7380, 7382, 7387, 7387, 7387, 7387, 7387, 7387, 7387, 7387, 7387, 7387, 7387, 7390, 7390, 7500, 7500, 7500, 7501, 7502, 7503, 7504, 7506, 7520, 7520, 7521, 7522, 7522, 7522, 7522, 7530, 7531, 7532, 7533, 7534, 7534, 7536, 7538, 7540, 7540, 7540, 7540, 7542, 7543, 7548, 7600, 7601, 7602, 7603, 7604, 7604, 7604, 7604, 7604, 7608, 7620, 7620, 7620, 7620, 7620, 7620, 7621, 7622, 7623, 7624, 7640, 7640, 7640, 7641, 7642, 7643, 7760, 7760, 7760, 7800, 7800, 7801, 7802, 7803, 7804, 7804, 7810, 7811, 7812, 7812, 7812, 7812, 7812, 7812, 7822, 7822, 7822, 7823, 7830, 7830, 7830, 7830, 7830, 7830, 7830, 7830, 7850, 7850, 7850, 7860, 7861, 7861, 7862, 7863, 7864, 7866, 7866, 7870, 7870, 7870, 7870, 7870, 7880, 7890, 7890, 7900, 7900, 7901, 7903, 7903, 7903, 7904, 7904, 7904, 7906, 7910, 7910, 7911, 7911, 7911, 7911, 7911, 7911, 7911, 7940, 7940, 7941, 7942, 7943, 7950, 7950, 7950, 7950, 7950, 7951, 7970, 7971, 7971, 7971, 7971, 7972, 7972, 7972, 7973, 7973]
    ORES_Luxembourg = [6600, 6600, 6600, 6600, 6600, 6630, 6637, 6637, 6637, 6640, 6640, 6640, 6640, 6640, 6640, 6642, 6660, 6660, 6661, 6661, 6662, 6663, 6666, 6670, 6670, 6671, 6672, 6673, 6674, 6680, 6680, 6680, 6681, 6686, 6687, 6688, 6690, 6690, 6692, 6698, 6700, 6700, 6700, 6700, 6704, 6706, 6717, 6717, 6717, 6717, 6717, 6720, 6720, 6720, 6721, 6723, 6724, 6724, 6724, 6730, 6730, 6730, 6730, 6740, 6740, 6740, 6741, 6742, 6743, 6747, 6747, 6747, 6750, 6750, 6750, 6760, 6760, 6760, 6760, 6761, 6762, 6767, 6767, 6767, 6767, 6767, 6769, 6769, 6769, 6769, 6769, 6780, 6780, 6780, 6781, 6782, 6790, 6791, 6792, 6792, 6800, 6800, 6800, 6800, 6800, 6800, 6800, 6800, 6810, 6810, 6810, 6811, 6812, 6813, 6820, 6820, 6820, 6820, 6821, 6823, 6824, 6830, 6830, 6830, 6830, 6831, 6832, 6833, 6833, 6834, 6836, 6838, 6840, 6840, 6840, 6840, 6840, 6840, 6850, 6850, 6850, 6851, 6852, 6852, 6853, 6856, 6860, 6860, 6860, 6860, 6860, 6870, 6870, 6870, 6870, 6870, 6870, 6880, 6880, 6880, 6880, 6880, 6887, 6887, 6887, 6890, 6890, 6890, 6890, 6890, 6890, 6890, 6900, 6900, 6900, 6900, 6900, 6900, 6900, 6920, 6920, 6921, 6922, 6924, 6927, 6927, 6927, 6927, 6929, 6929, 6929, 6929, 6940, 6940, 6940, 6940, 6940, 6941, 6941, 6941, 6941, 6941, 6941, 6941, 6950, 6950, 6951, 6952, 6953, 6953, 6953, 6953, 6960, 6960, 6960, 6960, 6960, 6960, 6960, 6970, 6971, 6972, 6980, 6980, 6982, 6983, 6984, 6986, 6987, 6987, 6987, 6987, 6990, 6990, 6990, 6990, 6997, 6997, 6997, 6997]
    ORES_MOUSCRON = [7700, 7700, 7711, 7712, 7730, 7730, 7730, 7730, 7730, 7730, 7730, 7740, 7740, 7742, 7743, 7743, 7750, 7750, 7750, 7750, 7750, 7760, 7760, 7760, 7780, 7780, 7781, 7782, 7783, 7784, 7784, 7890, 7910, 7910, 7912, 7912]
    ORES_NAMUR = [5000, 5000, 5001, 5002, 5003, 5004, 5020, 5020, 5020, 5020, 5020, 5020, 5020, 5021, 5022, 5024, 5024, 5030, 5030, 5030, 5030, 5030, 5030, 5031, 5032, 5032, 5032, 5032, 5032, 5060, 5060, 5060, 5060, 5060, 5060, 5060, 5060, 5070, 5070, 5070, 5070, 5070, 5070, 5080, 5080, 5080, 5080, 5080, 5081, 5081, 5081, 5100, 5100, 5100, 5100, 5100, 5101, 5101, 5101, 5140, 5140, 5140, 5140, 5150, 5150, 5150, 5150, 5170, 5170, 5170, 5170, 5170, 5170, 5190, 5190, 5190, 5190, 5190, 5190, 5190, 5190, 5310, 5310, 5310, 5310, 5310, 5310, 5310, 5310, 5310, 5310, 5310, 5310, 5310, 5310, 5310, 5310, 5330, 5330, 5330, 5332, 5333, 5334, 5336, 5360, 5360, 5361, 5361, 5362, 5363, 5364, 5370, 5370, 5370, 5370, 5370, 5370, 5372, 5374, 5376, 5377, 5377, 5377, 5377, 5377, 5377, 5377, 5377, 5377, 5380, 5380, 5380, 5380, 5380, 5380, 5380, 5380, 5380, 5380, 5380, 5500, 5500, 5500, 5500, 5500, 5500, 5500, 5501, 5502, 5503, 5504, 5520, 5520, 5521, 5522, 5523, 5523, 5524, 5530, 5530, 5530, 5530, 5530, 5530, 5530, 5530, 5530, 5537, 5537, 5537, 5537, 5537, 5537, 5537, 5540, 5540, 5540, 5540, 5541, 5542, 5543, 5544, 5550, 5550, 5550, 5550, 5550, 5550, 5550, 5550, 5550, 5550, 5550, 5550, 5555, 5555, 5555, 5555, 5555, 5555, 5555, 5555, 5555, 5555, 5560, 5560, 5560, 5560, 5560, 5560, 5561, 5562, 5563, 5564, 5570, 5570, 5570, 5570, 5570, 5570, 5570, 5570, 5570, 5570, 5571, 5572, 5573, 5574, 5575, 5575, 5575, 5575, 5575, 5575, 5575, 5575, 5575, 5575, 5575, 5575, 5576, 5580, 5580, 5580, 5580, 5580, 5580, 5580, 5580, 5580, 5580, 5580, 5590, 5590, 5590, 5590, 5590, 5590, 5590, 5590, 5590, 5590, 5600, 5600, 5600, 5600, 5600, 5600, 5600, 5600, 5600, 5600, 5600, 5600, 5600, 5600, 5600, 5600, 5600, 5620, 5620, 5620, 5620, 5620, 5620, 5620, 5621, 5621, 5621, 5621, 5630, 5630, 5630, 5630, 5630, 5630, 5640, 5640, 5640, 5640, 5640, 5640, 5641, 5644, 5646, 5650, 5650, 5650, 5650, 5650, 5650, 5650, 5650, 5650, 5651, 5651, 5651, 5651, 5651, 5651, 5651, 5660, 5660, 5660, 5660, 5660, 5680, 5680, 5680, 5680, 5680, 5680, 5680, 5680, 5680, 5680, 6210, 6210, 6210, 6210, 6210, 6211, 6280, 6280, 6280, 6280, 6280, 6280]
    ORES_VERVIERS = [4180, 4180, 4180, 4181, 4190, 4190, 4190, 4190, 4190, 4557, 4557, 4557, 4557, 4557, 4557, 4557, 4560, 4560, 4560, 4560, 4560, 4560, 4590, 4590, 4590, 4606, 4607, 4607, 4607, 4607, 4607, 4608, 4608, 4650, 4650, 4650, 4650, 4651, 4652, 4653, 4654, 4800, 4800, 4800, 4800, 4800, 4801, 4802, 4830, 4831, 4834, 4837, 4837, 4880, 4890, 4890, 4890, 4900, 4910, 4910, 4910, 4980, 4980, 4980, 4983, 4987, 4987, 4987, 4987, 4987, 4990, 4990, 4990]
    RESA = [4000, 4000, 4000, 4000, 4020, 4020, 4020, 4020, 4030, 4031, 4032, 4040, 4041, 4041, 4042, 4050, 4051, 4052, 4053, 4100, 4100, 4101, 4102, 4120, 4120, 4120, 4121, 4122, 4130, 4130, 4140, 4140, 4140, 4140, 4141, 4160, 4161, 4162, 4163, 4170, 4171, 4210, 4210, 4210, 4210, 4210, 4217, 4217, 4217, 4218, 4219, 4219, 4219, 4219, 4250, 4250, 4250, 4250, 4252, 4253, 4254, 4257, 4257, 4257, 4260, 4260, 4260, 4260, 4260, 4260, 4261, 4263, 4280, 4280, 4280, 4280, 4280, 4280, 4280, 4280, 4280, 4280, 4280, 4280, 4280, 4280, 4280, 4280, 4280, 4280, 4300, 4300, 4300, 4300, 4300, 4300, 4300, 4317, 4317, 4317, 4317, 4317, 4317, 4340, 4340, 4340, 4340, 4342, 4347, 4347, 4347, 4347, 4347, 4350, 4350, 4350, 4350, 4351, 4357, 4357, 4357, 4357, 4360, 4360, 4360, 4360, 4360, 4367, 4367, 4367, 4367, 4367, 4400, 4400, 4400, 4400, 4400, 4400, 4400, 4400, 4420, 4420, 4420, 4430, 4431, 4432, 4432, 4450, 4450, 4450, 4450, 4451, 4452, 4452, 4453, 4458, 4460, 4460, 4460, 4460, 4460, 4460, 4470, 4480, 4480, 4480, 4500, 4500, 4500, 4520, 4520, 4520, 4520, 4520, 4520, 4530, 4530, 4530, 4530, 4530, 4537, 4537, 4537, 4540, 4540, 4540, 4540, 4540, 4550, 4550, 4550, 4550, 4570, 4570, 4577, 4577, 4577, 4577, 4577, 4600, 4600, 4600, 4600, 4600, 4601, 4602, 4610, 4610, 4610, 4620, 4621, 4623, 4624, 4630, 4630, 4630, 4630, 4631, 4632, 4633, 4670, 4670, 4670, 4671, 4671, 4671, 4672, 4680, 4680, 4681, 4682, 4682, 4683, 4684, 4690, 4690, 4690, 4690, 4690, 4690, 4820, 4821, 4840, 4841, 4845, 4845, 4860, 4860, 4860, 4861, 4870, 4870, 4870, 4870, 4877, 4920, 4920, 4920, 4920, 4970, 4970]
    REW = [1300, 1300, 1301]

    if (cp in AIEG):
        print("Wallonie GRD: AIEG")
        return "AIEG"
    elif (cp in ORES_BRABANT_WALLON):
        print("Wallonie GRD: ORES_BRABANT_WALLON")
        return "ORES_BRABANT_WALLON"
    elif (cp in ORES_EST):
        print("Wallonie GRD: ORES_EST")
        return "ORES_EST"
    elif (cp in ORES_HAINAUT):
        print("Wallonie GRD: ORES_HAINAUT")
        return "ORES_HAINAUT"
    elif (cp in ORES_Luxembourg):
        print("Wallonie GRD: ORES_Luxembourg")
        return "ORES_Luxembourg"
    elif (cp in ORES_MOUSCRON):
        print("Wallonie GRD: ORES_MOUSCRON")
        return "ORES_MOUSCRON"
    elif (cp in ORES_NAMUR):
        print("Wallonie GRD: ORES_NAMUR")
        return "ORES_NAMUR"
    elif (cp in ORES_VERVIERS):
        print("Wallonie GRD: RES_VERVIERS")
        return "ORES_VERVIERS"
    elif (cp in RESA):
        print("Wallonie GRD: RESA")
        return "RESA"
    elif (cp in REW):
        print("Wallonie GRD: REW")
        return "REW"
    else:
        print("le code postal ", cp, " n'est pas dans les listes des GRD (Wallonie)")
        exit()


def getTarifProsumer(GRD):
    # 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030
    if (GRD == "AIEG"):
        return [67.27, 65.50, 65.50, 65.50, 65.50, 65.50, 65.50, 65.50, 65.50]
    elif (GRD == "AIESH"):
        return [86.5, 86.91, 87.91, 88.91, 89.91, 90.91, 91.91, 92.91, 93.91]
    elif (GRD == "ORES_NAMUR"):
        return [88.5, 88.21, 88.21, 88.21, 88.21, 88.21, 88.21, 88.21, 88.21]
    elif (GRD == "ORES_HAINAUT"):
        return [85.95, 84.86, 84.86, 84.86, 84.86, 84.86, 84.86, 84.86, 84.86]
    elif (GRD == "ORES_EST"):
        return [99.26, 98.53, 99.53, 100.53, 101.53, 102.53, 103.53, 104.53, 105.53]
    elif (GRD == "ORES_Luxembourg"):
        return [90.63, 91.63, 91.63, 91.63, 91.63, 91.63, 91.63, 91.63, 91.63]
    elif (GRD == "ORES_VERVIERS"):
        return [99.07, 97.08, 97.08, 97.08, 97.08, 97.08, 97.08, 97.08, 97.08]
    elif (GRD == "ORES_BRABANT_WALLON"):
        return [79.51, 79.52, 79.52, 79.52, 79.52, 79.52, 79.52, 79.52, 79.52]
    elif (GRD == "ORES_MOUSCRON"):
        return [80.31, 82.26, 82.26, 82.26, 82.26, 82.26, 82.26, 82.26, 82.26]
    elif (GRD == "RESA"):
        return [76.87, 77.19, 77.19, 77.19, 77.19, 77.19, 77.19, 77.19, 77.19]
    elif (GRD == "REW"):
        return [92.1, 88.67, 89.67, 90.67, 91.67, 92.67, 93.67, 94.67, 95.67]
    else:
        print("error Tarif Prosumer")
        exit()


def generateGraphe(pictureFilename, x, y):
    fig = go.Figure(data=[go.Bar(x=x, y=y, marker_color='#6AB5FD')])

    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='grey')
    fig.update_layout(
        plot_bgcolor='rgb(255,255,255)',
        paper_bgcolor='rgb(255,255,255)',
        font_family="Roboto",
        title={
            'text': "Production mensuelle estimée",
            'y': 0.85,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},


        yaxis=dict(
            title='Production (kWh)',
            titlefont=dict(
                family='Roboto',
                size=12,
                color='#000'
            )
        ),


        font=dict(
            family="Roboto",
            size=12,
            color="black"
        )
    )
    # fig.show()

    fig.write_image(pictureFilename, width=500, height=500, scale=4)

    image = Image.open(pictureFilename)
    image.load()
    imageSize = image.size

    # remove alpha channel
    invert_im = image.convert("RGB")

    # invert image (so that white is 0)
    invert_im = ImageOps.invert(invert_im)
    imageBox = invert_im.getbbox()
    imageBox = np.asarray(imageBox)
    # ajout d'un bord blanc
    imageBox[0] -= 10  # distance à gauche
    imageBox[1] -= 10  # distance en haut
    imageBox[2] += 10
    imageBox[3] += 10
    # print(imageBox[0], " ", imageBox[1], " ", imageBox[2], " ", imageBox[3] )
    imageBox = tuple(imageBox)
    cropped = image.crop(imageBox)
    cropped.save(pictureFilename)


def callPVGIS(latitude, longitude, peakPower, loss, slope, azimuth):  # call PVGIS
    pvgis = {}
    pvgis['E_m_value'] = []
    pvgis['E_m_average'] = []
    pvgis['E_y_total'] = []

    if (peakPower == 0):
        pvgis['E_m_value'] = [0] * 12
        pvgis['E_m_average'] = 0
        pvgis['E_y_total'] = 0
    else:
        url = 'https://re.jrc.ec.europa.eu/api/v5_2/PVcalc'
        params = dict(
            lat=latitude,
            lon=longitude,
            peakpower=peakPower,
            loss=loss,
            angle=slope,
            aspect=azimuth,
            outputformat='json'
        )
        try:
            resp = requests.get(url=url, params=params)
        except Exception as e:  # work on python 3.x
            print('error with PVGIS: ' + str(e))
            exit()
        _pvgis = resp.json()
        for i in range(len(_pvgis['outputs']['monthly']['fixed'])):
            pvgis['E_m_value'].append(_pvgis['outputs']['monthly']['fixed'][i]['E_m'])
        pvgis['E_m_average'] = _pvgis['outputs']['totals']['fixed']['E_m']
        pvgis['E_y_total'] = _pvgis['outputs']['totals']['fixed']['E_y']
    return pvgis


def main():

    print("version 1.2")

    # Get arguments
    parser = argparse.ArgumentParser()

    # default_format = "html"
    # default_output = "./graphe_out.html"

    # parser.add_argument("--config", help="config file", type=str, default=default_config)
    # parser.add_argument("--cp", help="select postal code", type=int, required=True)
    # parser.add_argument("--priceHT", help="Price HT", type=str, required=True)
    # parser.add_argument("--slope", help="slope 16°, 35°, 45° ?", type=int, required=True)
    # parser.add_argument("--azimuth", help="Orientation angle of the PV system, 0=south, 90=west, -90=east", type=int, required=True)
    # parser.add_argument("--peakpower", help="peakpower in kWh", type=float, required=True)
    # parser.add_argument("--inverterpower", help="inverter power in kVA", type=float, required=True)
    # parser.add_argument("--vat", help="applicable VAT rule", type=str, choices=["0", "6", "21"], required=True)

    # parser.add_argument("--output", help=f"output file name and path (default: {default_output})", type=str, default=default_output)
    # parser.add_argument("--format", help=f"output file format (default: {default_format})", type=str, default=default_format, choices=["html", "pdf"])
    # args = parser.parse_args()

    # read yaml
    content = read_content_yaml("configv2.yaml")

    # handle str to int issue
    content['consumption'] = float(content['consumption'])
    content['instalPriceHT'] = float(content['instalPriceHT'])
    content['instalVAT'] = float(content['instalVAT']) / 100 + 1
    content['elecVAT'] = float(content['elecVAT']) / 100 + 1
    content['inverterPower'] = float(content['inverterPower']) / 1000
    content['peakPower1'] = float(content['peakPower1']) / 1000
    content['peakPower2'] = float(content['peakPower2']) / 1000
    content['peakPower3'] = float(content['peakPower3']) / 1000
    content['peakPower4'] = float(content['peakPower4']) / 1000

    content['azimuth1'] = content['azimuth1'] - 180  # correction pour PVGIS  (-180°)
    content['azimuth2'] = content['azimuth2'] - 180
    content['azimuth3'] = content['azimuth3'] - 180
    content['azimuth4'] = content['azimuth4'] - 180

    # Get long, lat from City & Contry
    geolocator = Nominatim(user_agent="pvGraph")
    try:
        location = geolocator.geocode(str(content['cp']) + " , Belgium")
    except Exception as e:  # work on python 3.x
        print('error with GEOLOCATOR: ' + str(e))
        exit()

    print(location.address)
    # print((location.latitude, location.longitude))

    content['region'] = getRegion(content['cp'])
    content['city'] = location.address
    content['lat'] = location.latitude
    content['lon'] = location.longitude

    # khW per month
    content['month'] = []
    content['month'] = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    content['monthShort'] = []
    content['monthShort'] = ['jan', 'fév', 'mar', 'avr', 'mai', 'jun', 'jul', 'aoû', 'sep', 'oct', 'nov', 'déc']

    # regroupement zone
    print(" ")
    print("Installed 1: " + str(content['peakPower1']) + " kWc")
    print("Installed 2: " + str(content['peakPower2']) + " kWc")
    print("Installed 3: " + str(content['peakPower3']) + " kWc")
    print("Installed 4: " + str(content['peakPower4']) + " kWc")
    content['peakPower'] = content['peakPower1'] + content['peakPower2'] + content['peakPower3'] + content['peakPower4']
    print("Total installed: " + str(content['peakPower']) + " kWc")

    pvgis1 = callPVGIS(location.latitude, location.longitude, content['peakPower1'], content['loss'], content['slope1'], content['azimuth1'])
    pvgis2 = callPVGIS(location.latitude, location.longitude, content['peakPower2'], content['loss'], content['slope2'], content['azimuth2'])
    pvgis3 = callPVGIS(location.latitude, location.longitude, content['peakPower3'], content['loss'], content['slope3'], content['azimuth3'])
    pvgis4 = callPVGIS(location.latitude, location.longitude, content['peakPower4'], content['loss'], content['slope4'], content['azimuth4'])

    content['E_m_value'] = np.add(np.add(pvgis1['E_m_value'], pvgis2['E_m_value']), np.add(pvgis3['E_m_value'], pvgis4['E_m_value']))
    content['E_m_average'] = pvgis1['E_m_average'] + pvgis2['E_m_average'] + pvgis3['E_m_average'] + pvgis4['E_m_average']
    content['E_y_total'] = pvgis1['E_y_total'] + pvgis2['E_y_total'] + pvgis3['E_y_total'] + pvgis4['E_y_total']

    print(" ")
    print("Production 1: " + str(pvgis1['E_y_total']) + " kWh")
    print("Production 2: " + str(pvgis2['E_y_total']) + " kWh")
    print("Production 3: " + str(pvgis3['E_y_total']) + " kWh")
    print("Production 4: " + str(pvgis4['E_y_total']) + " kWh")
    print("Total production: " + str(content['E_y_total']) + " kWh")

    generateGraphe("./" + content['outputFolder'] + "/" + content['filename'] + ".png", content['monthShort'], content['E_m_value'])

    # Wh/kWc: Rendement par kWc
    # content['WhPerkWc'] = round(content['E_y_total1']/content['peakPower1'],0)

    # €/kWc
    content['PricePerkWcHT'] = round(float(content['instalPriceHT']) / float(content['peakPower']) / 1000, 2)

    # Tableau d'amortissement
    content['investTime'] = 25  # years
    content['shortYearList'] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25]

    content['year'] = []
    content['production'] = []
    content['productionConsummed'] = []
    content['productionSold'] = []
    content['elecPriceBuy'] = []
    content['elecEconomy'] = []
    content['elecPriceSell'] = []
    content['elecGain'] = []
    content['prime'] = []
    content['tarifProsumer'] = []
    content['spending'] = []
    content['revenue'] = []
    content['revenueCumulated'] = []

    for i in range(content['investTime']):
        # year
        content['year'].append(i + 1)
        # production
        _production = (content['E_y_total']) * ((1 - content['moduleDegradationYear'] / 100)**(i))
        content['production'].append(round(_production, 2))
        # production auto-consommée & Production revendue
        # if content['consumption']  content['production'][i]
        if content['consumption'] != 0:
            content['productionConsummed'].append(round(content['consumption'] * content['autoconsommationRate'] / 100, 2))
        else:
            content['productionConsummed'].append(round(content['production'][i] * content['autoconsommationRate'] / 100, 2))

        content['productionSold'].append(round(content['production'][i] - content['productionConsummed'][i], 2))

        # Bought Electricity price
        _elecPriceBuy = content['elecPriceBuyTodayHT'] * content['elecVAT'] * ((1 + content['elecPriceInflation'] / 100)**(i))
        content['elecPriceBuy'].append(round(_elecPriceBuy, 2))

        # Injected Electricity price
        _elecPriceSell = content['elecPriceSellTodayHT'] * content['elecVAT'] * ((1 + content['elecPriceInflation'] / 100) ** (i))
        content['elecPriceSell'].append(round(_elecPriceSell, 2))

       ### START --- DIFFERENCE PAR REGION ##########################
        # BRUXELLES
        # Certificat vert
        # vente de l'elec injecté
        if (content['region'] == "BXL"):
            # Economy
            content['elecEconomy'].append(round(content['productionConsummed'][i] * content['elecPriceBuy'][i], 2))
            # injection
            content['elecGain'].append(round(content['productionSold'][i] * content['elecPriceSell'][i], 2))

            # certificat vert : https://www.brugel.brussels/themes/energies-renouvelables-11/mecanisme-des-certificats-verts-35
            if (content['peakPower'] <= 5):
                content['nbrCertificatParMWH'] = 2.055
            elif (content['peakPower'] <= 36):
                content['nbrCertificatParMWH'] = 1.953
            elif (content['peakPower'] <= 100):
                content['nbrCertificatParMWH'] = 2.1
            elif (content['peakPower'] <= 250):
                content['nbrCertificatParMWH'] = 1.8
            else:
                content['nbrCertificatParMWH'] = 1.5

            if (i <= 9):  # certificat vert pendant 10ans
                _prime = content['production'][i] * content['certificatVertBXL'] * content['nbrCertificatParMWH'] / 1000
                content['prime'].append(round(_prime, 2))
            else:
                content['prime'].append(0)

            content['tarifProsumer'].append(0)

        # FLANDRE
            # vente de l'elec injecté
            # prime one-shot
        if (content['region'] == "FLA"):
            # Economy
            content['elecEconomy'].append(round(content['productionConsummed'][i] * content['elecPriceBuy'][i], 2))
            # injection:
            content['elecGain'].append(round(content['productionSold'][i] * content['elecPriceSell'][i], 2))

            # Prime panneau
            # https://www.energiesparen.be/premie-voor-zonnepanelen-2021
            if (i == 0):
                if (content['peakPower'] <= 4):
                    content['prime'].append(300 * content['peakPower'])
                elif (content['peakPower'] <= 6):
                    content['prime'].append(300 * 4 + 150 * ((content['peakPower'] - 4)))
                else:
                    content['prime'].append(300 * 4 + 150 * 2)
            else:
                content['prime'].append(0)

            content['tarifProsumer'].append(0)

        # WALLONIE
            # tarif prosumer
            # reduction prosumer pendant 2 ans
            # compteur qui tourne à l'envers
        if (content['region'] == "WAL"):

            # check that a right value has been filled for the inverterPower:
            if (content['production'][0] / 3 > content['inverterPower'] * 1000):
                print("ERROR with the inverter power value")
                exit()

        # Economy
            if (i <= 7):  # jusqu'à 2030
                content['elecEconomy'].append(round(content['production'][i] * content['elecPriceBuy'][i], 2))
            else:  # après 2030, 25% de la production compté.
                ###!!!!!!! 25% de la partie réinjecté #### !!!!!!!!!

                content['elecEconomy'].append(round((content['productionConsummed'][i] * content['elecPriceBuy'][i]) + (content['productionSold'][i] * content['elecPriceBuy'][i] * 0.35), 2))
        # injection:
            content['elecGain'].append(0)

        # Tarif capacitaire prosumer: puissance de l'onduleur
            # find GRD and get prosumer tarif
            if (i == 0):
                _tarifProsumer = getTarifProsumer(getGRD(content['cp']))  # only retrieve the info once.
            if (i <= 1):  # jusqu'à 2023
                content['tarifProsumer'].append(round(_tarifProsumer[i] * content['inverterPower'] * (1 - 0.5427), 2))
            elif (i <= 7):  # jusqu'à 2030
                content['tarifProsumer'].append(_tarifProsumer[i] * content['inverterPower'])
            else:  # après 2030, disparition du tarif capacitaire prosumer
                content['tarifProsumer'].append(0)

            content['prime'].append(0)
            # En 2022 et 2023, la Région wallonne continuera à compenser en partie le tarif prosumer mais cette fois à concurrence de 54,27%. Toujours via une prime payée par le GRD. Les 45,73% restants seront donc à charge des prosumers.
        # tarif consumer

        ### END --- DIFFERENCE PAR REGION ##########################

        # Spending (replacement of inverter)
        if (i == 0):
            content['spending'].append(float(content['instalPriceHT']) * content['instalVAT'])
        elif (content['inverterReplacementYear'] == i + 1 and content['inverterType'] == 1):
            content['spending'].append(content['inverterReplacementPriceHT'] * content['instalVAT'])
        else:
            content['spending'].append(0)

        # Total revenue
        content['revenue'].append(round(content['elecEconomy'][i] + content['elecGain'][i] + content['prime'][i] - content['tarifProsumer'][i], 2))
        if (i == 0):
            content['revenueCumulated'].append(round(content['revenue'][i] - content['spending'][i], 2))
        else:
            content['revenueCumulated'].append(round(content['revenueCumulated'][i - 1] + content['revenue'][i] - content['spending'][i], 2))

    content['productionTotal'] = round(sum(content['production']), 0)
    content['productionConsummedTotal'] = round(sum(content['productionConsummed']), 0)
    content['productionSoldTotal'] = round(sum(content['productionSold']), 0)
    content['elecEconomyTotal'] = round(sum(content['elecEconomy']), 0)
    content['elecGainTotal'] = round(sum(content['elecGain']), 0)
    content['primeTotal'] = round(sum(content['prime']), 0)
    content['tarifProsumerTotal'] = round(sum(content['tarifProsumer']), 0)
    content['spendingTotal'] = round(sum(content['spending']), 0)
    content['revenueTotal'] = round(sum(content['revenue']), 0)

    # calculate return on investment
    _return = (content['revenueTotal'] - (content['instalPriceHT'] * content['instalVAT'])) / (content['instalPriceHT'] * content['instalVAT'])
    content['returnRate'] = round(((1 + _return)**(1 / content['investTime']) - 1) * 100, 2)

    # after how many year Am I postive
    _nbrYearPositive = content['revenueCumulated'].index(min([i for i in content['revenueCumulated'] if i >= 0]))
    content['nbrYearPositive'] = round(abs(content['revenueCumulated'][_nbrYearPositive - 1]) / content['revenue'][_nbrYearPositive] + _nbrYearPositive, 2)

    # other
    # charset Win - OSX

    if os.name == "posix":
        content['charset'] = "UTF-8"
    else:
        content['charset'] = "ISO-8859-1"

    invoice_rendered = rendererv2.Renderer(content)
    invoice_rendered.dump(content['outputFolder'], content['filename'])


if __name__ == "__main__":
    main()
