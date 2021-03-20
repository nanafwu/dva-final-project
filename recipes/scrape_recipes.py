import csv
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json



class RecipeAPIUtils:

    def __init__(self):
        #self.all_dishes = self.get_unique_dishes()
        self.application_key = 'ea72b2a7589d887c4c93f02157fad0e6'
        self.application_id = '2f11e861'


    def search_recipe(self, query)->None:
        """
        Example GET request: https://api.edamam.com/search?q=chicken&app_id=2f11e861&app_key=ea72b2a7589d887c4c93f02157fad0e6
        Documentation docs: https://developer.edamam.com/edamam-docs-recipe-api
        :param query: recipe query
        """
        query = urlencode([('q', query), ('app_key', self.application_key), ('app_id', self.application_id)])
        print(query)
        req = Request('https://api.edamam.com/search?' + query)
        data = json.load(urlopen(req))
        print('loaded data')
        print(data)



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
    api.search_recipe('toast')
