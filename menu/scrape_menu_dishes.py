import requests
from bs4 import BeautifulSoup
from time import sleep
import csv


class MenuAPIUtils:

    def make_soup(self, url):
        headers = {
            'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) '
                           'Gecko/20100101 Firefox/32.0')}
        response = requests.get(url, headers=headers)
        print('Fetched ', url)
        page = response.text
        soup = BeautifulSoup(page, "lxml")
        return soup

    def __init__(self):
        self.menu_listing_page = 'https://www.allmenus.com/ny/new-york/-/'
        self.all_menu_url = 'https://www.allmenus.com/'
        self.restaurnt_list_tsv = 'menu/menu_data/restaurant_list.tsv'
        self.restaurnt_dish_list_tsv = 'menu/menu_data/restaurant_dish_list.tsv'

    def get_nyc_menu(self, restaurant_url)-> list:
        """
        :param restaurant_url:
        :return: List of dishes, descriptions of dishes, and price for each dish
        """
        soup = self.make_soup(self.all_menu_url + restaurant_url)
        dishes = soup.find_all('li', class_='menu-items')
        restaurant_dishes_output = []
        for dish in dishes:
            dish_name = dish.find('span', class_='item-title').text.strip()
            dish_price = dish.find('span', class_='item-price').text.strip()
            dish_description = dish.find('p', class_='description').text.strip().replace('&comma', ', ')
            restaurant_dishes_output.append([restaurant_url, dish_name, dish_description, dish_price])

        return restaurant_dishes_output


    def write_nyc_menus(self) -> None:
        """
        Iterate through NYC restaurant list and store each restaurant's menu
        """
        all_restaurant_urls = []
        with open(self.restaurnt_list_tsv, 'r') as f:
            tsvreader = csv.reader(f, delimiter='\t')
            for line in tsvreader:
                restaurant_url = line[1]
                all_restaurant_urls.append(restaurant_url)

        with open(self.restaurnt_dish_list_tsv, 'a+') as file:
            writer = csv.writer(file, delimiter='\t')
            for r in all_restaurant_urls:
                menu_dishes = self.get_nyc_menu(r)
                sleep(1)
                for dish in menu_dishes:
                    writer.writerow(dish)

    def write_restaurant_list(self) -> None:
        """
        Store list of top 500 most popular restaurants in NYC:
        https://www.allmenus.com/ny/new-york/-/

        Write to TSV (tab delimited) `menu_data/restaurant_list.tsv`.
        TSV has format restaurant_name, link, cuisine_list, address
        """

        soup = self.make_soup(self.menu_listing_page)
        restaurant_listings = soup.find_all('li', class_='restaurant-list-item')

        with open(self.restaurnt_list_tsv, 'w+') as file:
            for r in restaurant_listings:
                restaurant_name = r.find('h4', class_="name").text.strip()
                address = r.find('div', class_="address-container").text.strip().replace('\n',' ')
                link = r.find('h4', class_="name").find('a')['href']
                cuisine_list = r.find('p', class_="cousine-list").text.strip()
                writer = csv.writer(file, delimiter='\t')
                writer.writerow([restaurant_name, link, cuisine_list, address])


if __name__ == '__main__':
    api = MenuAPIUtils()
    #api.write_restaurant_list()
    #api.write_nyc_menus()



