import csv
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json
import re
from time import sleep

class RecipeAPIUtils:

    def __init__(self):
        self.all_dishes = self.get_unique_dishes()
        self.application_key = 'ea72b2a7589d887c4c93f02157fad0e6'
        self.application_id = '2f11e861'
        self.recipe_data_dir = 'recipe_data/'

    def create_dish_filename(self, dish_name)->str:
        """
        returns a filename with non-alphanumeric characters replaced with _
        """
        return self.recipe_data_dir + (re.sub("[^0-9a-zA-Z]+", "_", dish_name)).strip() + '.json'

    def write_recipe(self, dish_name)->None:
        """
        Takes the dish name and runs through Edamen's search
        Example GET request: https://api.edamam.com/search?q=chicken&app_id=2f11e861&app_key=ea72b2a7589d887c4c93f02157fad0e6
        Documentation docs: https://developer.edamam.com/edamam-docs-recipe-api
        :param query: recipe query
        """

        # replace non-alphanumeric characters with a space
        clean_dish_name = re.sub("[^0-9a-zA-Z]+", " ", dish_name).strip()

        query = urlencode([('q', clean_dish_name), ('app_key', self.application_key), ('app_id', self.application_id)])
        req = Request('https://api.edamam.com/search?' + query)
        recipes = json.load(urlopen(req))
        print('Found {} recipes for "{}" dish'.format(len(recipes['hits']), clean_dish_name))

        dish_filename = self.create_dish_filename(dish_name)

        with open(dish_filename, 'w+') as file:
            file.write(json.dumps(recipes))

    def write_recipes_for_all_dishes(self)->None:
        """
        For all dishes found in menus, find recipes for them
        """
        for i, dish_name in enumerate(self.all_dishes):
            print('Processing dish {}: "{}"'.format(i, dish_name))
            self.write_recipe(dish_name)
            sleep(6)

    def get_unique_dishes(self)-> list:
        """
        :return: Set of unique dishes - 36K in total
        """
        dishes = set()
        with open('../menu/menu_data/restaurant_dish_list.tsv', 'r') as f:
            tsvreader = csv.reader(f, delimiter='\t')
            for line in tsvreader:
                dish = line[1]
                dishes.add(dish.lower())

        print('Loading {} unique dishes'.format(len(dishes)))
        return sorted(list(dishes))


if __name__ == '__main__':
    api = RecipeAPIUtils()
    api.write_recipes_for_all_dishes()
