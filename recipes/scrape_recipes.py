import csv
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json
import re
from time import sleep
import pandas as pd
import numpy as np



class RecipeAPIUtils:

    def __init__(self):
        self.all_dishes = self.get_unique_dishes()
        self.all_restaurants = self.get_unique_restaurant()
        # TODO: It is recommended to generate your own Application key and ids when running locally
        self.application_key = '1142d26a83e96564985116d973a6dfd3'
        self.application_id = '61bb0021'
        self.recipe_data_dir = 'recipe_search_data/'

    def create_dish_filename(self, dish_name)->str:
        """
        returns a filename with non-alphanumeric characters replaced with _
        """
        return self.recipe_data_dir + (re.sub("[^0-9a-zA-Z]+", "_", dish_name)).strip() + '.json'

    def write_recipe(self, dish_name, restaurant_name):
        """
        Takes the dish name and runs through Edamen's search
        Example GET request: https://api.edamam.com/search?q=chicken&app_id=2f11e861&app_key=ea72b2a7589d887c4c93f02157fad0e6
        Documentation docs: https://developer.edamam.com/edamam-docs-recipe-api
        """


        query = urlencode([('q', dish_name), ('app_key', self.application_key), ('app_id', self.application_id)])
        try:
            req = Request('https://api.edamam.com/search?' + query)
            recipes = json.load(urlopen(req))
            print('Found {} recipes for "{}" dish'.format(len(recipes['hits']), dish_name))
            column_names = ["Restaurant_URL", "Dish_Name", "Recipe", "Recipe_ID", "Health_Label"]
            matched_recipe = []
            recipe_uri = []
            health_label = []

            for a in recipes['hits']:
                matched_recipe.append(a['recipe']['ingredientLines'])
                recipe_uri.append(a['recipe']['uri'])
                health_label.append(a['recipe']['healthLabels'])
                

            if len(matched_recipe) == 0:
                temp = pd.DataFrame(columns = column_names)
                
            else:
                
                matched_recipe = pd.Series(matched_recipe)
                dishes = [dish_name]*len(matched_recipe)
                restaurant = [restaurant_name]*len(matched_recipe)
                temp = pd.DataFrame({'Restaurant_URL' : restaurant, 'Dish_Name': dishes, 'Recipe' : matched_recipe, 'Recipe_ID' : recipe_uri, "Health_Label" : health_label })
                
            return temp
        except:
            column_names = ["Restaurant_URL", "Dish_Name", "Recipe", "Recipe_ID", "Health_Label"]
            temp = pd.DataFrame(columns = column_names)
            return temp
            

    def write_recipes_for_all_dishes(self):
        """
        For all dishes found in menus, find recipes for them
        """
        column_names = ["Restaurant_URL", "Dish_Name", "Recipe", "Recipe_ID", "Health_Label"]
        df = pd.DataFrame(columns = column_names)
        

        d_sample = self.all_dishes[:3000]
        r_sample = self.all_restaurants[:3000]
        num = 0
        den = len(d_sample)
        for dish_name, restaurant_name in zip(d_sample,r_sample):
            # cleanse / standardize dish name
            dish_name = dish_name.replace('?','')
            dish_name = dish_name.replace('1b.','')
            dish_name = dish_name.replace('0','')
            dish_name = dish_name.replace('"','')
            dish_name = dish_name.replace('&comma','')
            dish_name = dish_name.replace(';','')
            dish_name = dish_name.replace('','')
            dish_name = re.sub("[0-9]", "", dish_name)
            dish_name = dish_name.replace('awesome','')
            dish_name = dish_name.replace('assorted','')
            dish_name = dish_name.replace('cb','')
            dish_name = dish_name.replace('\\','')
            dish_name = dish_name.replace('/','')
            dish_name = dish_name.replace('#','')
            dish_name = dish_name.replace('.','')
            dish_name = ''.join(i for i in dish_name if not i.isdigit())
            dish_name = dish_name.replace('  ',' ')
            dish_name = dish_name.replace('the','')
            dish_name = dish_name.replace('nduja','')
            dish_name = dish_name.replace('\'','')
            dish_name = dish_name.replace('boars head meat','')
            dish_name = dish_name.replace('ampania','')
            dish_name = dish_name.replace('platter','')
            dish_name = dish_name.strip()
            df = pd.concat([df, self.write_recipe(dish_name, restaurant_name)])
            num += 1
            pct_done = (num / den)*100
            pct_done = round(pct_done,2)
            print('Program is  {}% complete'.format(pct_done))
            sleep(10)
        df = df.reset_index()
        df = df.drop('index', axis = 1)
        return df

    def get_unique_dishes(self)-> list:
        """
        :return: list of unique dishes - 36K in total
        """
        dishes = []
        with open('restaurant_dish_list.tsv', 'r') as f:
            tsvreader = csv.reader(f, delimiter='\t')
            for line in tsvreader:
                dish = line[1]
                dishes.append(dish.lower())
                
        print('Loading {} unique dishes'.format(len(dishes)))
        return dishes
                
    def get_unique_restaurant(self)-> list:
        """
        :return: list of restaurant url's
        """
        restaurants = []
        with open('restaurant_dish_list.tsv', 'r') as f:
            tsvreader = csv.reader(f, delimiter='\t')
            for line in tsvreader:
                restaurant_url = line[0]
                restaurants.append(restaurant_url)
                
        return restaurants
                                          


if __name__ == '__main__':
    api = RecipeAPIUtils()
    # TODO: uncomment when ready
    apple = api.write_recipes_for_all_dishes()
