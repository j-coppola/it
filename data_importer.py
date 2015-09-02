
from __future__ import division
import random
#import cProfile
#import pstats
import os
import yaml
from collections import defaultdict

import libtcodpy as libtcod

YAML_DIRECTORY = os.path.join(os.getcwd(), 'data')



######## FOR ECONOMY ##########

class Resource(object):
    def __init__(self, name, category, resource_class, gather_amount, break_chance, app_chances, app_amt):
        self.name = name
        self.category = category
        self.resource_class = resource_class
        self.gather_amount = gather_amount
        self.break_chance = break_chance
        self.app_chances = app_chances
        self.app_amt = app_amt


class FinishedGood(object):
    def __init__(self, category, material, in_amt, out_amt):
        # Type, i.e. tools
        self.category = category
        # The resource type that makes this specific good
        self.material = material
        self.break_chance = self.material.break_chance

        self.name = self.material.name + ' ' + self.category

        # How many of the input materials produce how many of this good
        self.in_amt = in_amt
        self.out_amt = out_amt


######## FOR PHYSICS ##########

class Material:
    ''' Basic material instance '''
    def __init__(self, name, rgb_color, density, rigid, force_diffusion, slice_resistance):
        self.name = name
        self.density = density
        self.color = libtcod.Color(*rgb_color)
        self.rigid = rigid
        self.force_diffusion = force_diffusion
        # 0 = soft (like flesh), 1 = very likely to shatter
        self.slice_resistance = slice_resistance






class CommodityManager:
    def __init__(self):

        # These 3 contain the actual Resource / Good classes in the list
        self.resources = []
        self.goods = []
        self.all_commodities = []

        # These are dicts of category --> list of matching commodities
        self.commodity_type_to_actual_tokens = defaultdict(list)
        self.commodity_type_to_token_names = defaultdict(list)

        self.commodity_name_to_actual_tokens = {}

        # Finally these are the goods that can be made from a paricular resource
        self.goods_by_resource_token = defaultdict(list)

        # Temp - this has got to go!
        self.strategic_types = defaultdict(list)

        ###### For materials in physics module ######
        self.materials = {}



        self.load_yaml()


    def add_commodity(self, commodity):
        self.all_commodities.append(commodity)
        self.commodity_type_to_actual_tokens[commodity.category].append(commodity)
        self.commodity_type_to_token_names[commodity.category].append(commodity.name)
        self.commodity_name_to_actual_tokens[commodity.name] = commodity

    def get_strategic_resources(self):
        return [r for r in self.resources if resource.resource_class == 'strategic']

    def load_yaml(self):
        ''' Load the yaml file containing resource info '''
        with open(os.path.join(YAML_DIRECTORY, 'resources.yml')) as r:
            resource_info = yaml.load(r)

        # Loop through all resources in the yaml, creating resources and their associated reactions as we go
        for rname in resource_info:
            resource = Resource(name=rname, category=resource_info[rname]['category'], resource_class=resource_info[rname]['resource_class'],
                               gather_amount=resource_info[rname]['gather_amount'], break_chance=resource_info[rname]['break_chance'],
                               app_chances=resource_info[rname]['app_chances'], app_amt=resource_info[rname]['app_amount'])

            self.resources.append(resource)

            # "Reactions" for each resource - e.g. we can turn 2 copper into 1 copper tools, or something
            for reaction_type in resource_info[rname]['reactions']:
                finished_good = FinishedGood(category=reaction_type, material=resource, in_amt=resource_info[rname]['reactions'][reaction_type]['input_units'], out_amt=resource_info[rname]['reactions'][reaction_type]['output_units'])
                self.goods.append(finished_good)


        #### Now build more info about each of these into the class ####
        for commodity in self.resources:
            self.add_commodity(commodity=commodity)

            if resource.resource_class == 'strategic':
                self.strategic_types[resource.category].append(resource)

        for good in self.goods:
            self.goods_by_resource_token[good.material.name].append(good)
            self.add_commodity(commodity=good)


        ###################### Materials for physics simulation ##############################

        # Grab yaml file and convert it to a dictionary
        with open(os.path.join(YAML_DIRECTORY, 'materials.yml')) as m:
            loaded_materials = yaml.load(m)

        for material_name in loaded_materials:
            self.materials[material_name] = Material(name=material_name, rgb_color=loaded_materials[material_name]['rgb_color'],
                                           density=loaded_materials[material_name]['density'],
                                           rigid=loaded_materials[material_name]['rigid'],
                                           force_diffusion=loaded_materials[material_name]['force_diffusion'],
                                           slice_resistance=loaded_materials[material_name]['slice_resistance'])


    def get_commodities_of_type(self, commodity_type):
        return self.commodity_type_to_actual_tokens[commodity_type]

    def get_names_of_commodities_of_type(self, commodity_type):
        return self.commodity_type_to_token_names[commodity_type]

    def get_actual_commodity_from_name(self, commodity_name):
        return self.commodity_name_to_actual_tokens[commodity_name]

    def get_goods_by_resource_token(self):
        goods_by_material_token = defaultdict(list)
        for good in self.goods:
            goods_by_material_token[good.material.name].append(good)

        return goods_by_material_token



def import_data():
    global AGENT_INFO, CITY_INDUSTRY_SLOTS, CITY_RESOURCE_SLOTS, commodity_manager, materials

    with open(os.path.join(YAML_DIRECTORY, 'agents.yml')) as a:
        AGENT_INFO = yaml.load(a)

    CITY_RESOURCE_SLOTS = {'foods':20, 'cloths':6, 'clays':4, 'ores':6, 'woods':6}
    CITY_INDUSTRY_SLOTS = {'tools':10, 'clothing':12, 'pottery':10, 'furniture':8, 'armor':2, 'weapons':2}

    commodity_manager = CommodityManager()
