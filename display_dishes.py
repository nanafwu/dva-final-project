import numpy as np
import scipy as sp
import pandas as pd
import re
# from .dir import SimilarDishFinder

class UserInput(object):

  def __init__(self):
    # dataframe that contains entire recipe database with the similar matches
    self.recipe_df = None
    self.restaurants_df = None
    # dataframe
    self.matches_df = []
    self.matched_dish = None
    self.similar_dishes = []

  def read_recipes_csv(self, filepath):
    '''
    Read in CSV file and store in class member
    '''
    self.recipe_df = pd.read_csv(filepath, index_col=0)
    # print(self.recipe_df.columns.values)
    # df.iloc[:,np.r_[0:2,4:5]]
    return

  def read_restaurant_tsv(self, filepath):
    self.restaurants_df = pd.read_table(filepath)
    # print(self.restaurants_df)
    # print(self.restaurants_df.columns.values) # file header

  def find_best_match(self, search_str):
    '''
    Find the best match given the user's 
    '''
    #Remove filler words. May be an easier to find and remove.
    removed_words = re.sub(r' and ', " ", search_str)
    removed_words = re.sub(r' and', "", search_str)
    removed_words = re.sub(r' it ', " ", removed_words)
    removed_words = re.sub(r'The ', "", removed_words)
    removed_words = re.sub(r' the ', " ", removed_words)
    removed_words = re.sub(r' an ', " ", removed_words)
    removed_words = re.sub(r' an', "", removed_words)
    removed_words = re.sub(r'An ', "", removed_words)
    removed_words = re.sub(r' a ', " ", removed_words)
    removed_words = re.sub(r'A ', "", removed_words)

    self.matches_df = []

    modified_str = removed_words.strip().split()
    # print(modified_str)
    base = r'^{}'
    expr = '(?=.*{})'
    regex_str = base.format(''.join(expr.format(w) for w in modified_str))
    self.matches_df = self.recipe_df[self.recipe_df['Dish_Name'].str.contains(regex_str, case=False, regex=True)]

    if(len(self.matches_df) is not 0):
      self.matched_dish = self.matches_df.iloc[0]

      # Index of the similar dishes converted to int and placed into a list.
      self.similar_dishes = [int(x) for x in self.matched_dish['Top_5_Indices'][1:-1].split(',')]

    return len(self.matches_df)


  def display_dishes(self):
    print(self.recipe_df.iloc[self.similar_dishes]['Dish_Name'].to_string(index=False))

  def generate_csv_for_d3(self):
    '''
    DISH_ID, DISH_NAME, SIM_DISH_ID1,...,SIM_DISH_ID5, SIM_DISH_NAME_1,...,SIM_DISH_NAME5,REST_NAME1,...,REST_NAME5
    '''

    data = []
    

    # restaurant url (Restaurant_URL):
    # /ny/new-york/375922-america-s-finest-deli/menu/
  
    # print(self.restaurants_df.loc[:, ['Restaurant_Name']])

    for row in self.recipe_df.itertuples():
      # print(row.Top_5_Indices)
      dish_rest_ids = [int(x) for x in row.Top_5_Indices[1:-1].split(',')]
      dish_rest_names = [x.replace("'", "") for x in row.Top_5_Dish_Names[1:-1].split(', ')]
      new_row = [row.Index,row.Dish_Name]
      new_row.append(dish_rest_ids)
      new_row.append(dish_rest_names)

      rest_names = []
      for id in dish_rest_ids:
        restaurant_url = self.recipe_df.iloc[id]['Restaurant_URL']
        # print(restaurant_url)
        restaurant_name = self.restaurants_df.loc[self.restaurants_df['Restaurant_URL'].str.contains(restaurant_url)]['Restaurant_Name'].to_string(index=False).strip()
        # print(restaurant_name)

        rest_names.append(restaurant_name)
      
      new_row.append(rest_names)
      # print(new_row)
      data.append(new_row)
      np_arr = np.array(data, dtype=object)
    # print(np_arr.shape)

    # Create pandas df
    df = pd.DataFrame(np_arr)
    # print(df)
    headers = ['Index', 'Dish_Name', 'Similar_Index', 'Similar_Dishes', 'Location_of_Similar']
    df.columns = ['Index', 'Dish_Name', 'Similar_Index', 'Similar_Dishes', 'Location_of_Similar']
    df.to_csv('d3_data.csv', index=False, columns=headers)



    

if __name__ == "__main__":
  ui = UserInput()
  ui.read_recipes_csv('Similar_Recipes_man_sub.csv')
  ui.read_restaurant_tsv('./menu/menu_data/restaurant_list.tsv')
  ui.generate_csv_for_d3()
  # while(True):
  #   try:
  #     search_recipe = str(input("Enter your favorite dish: "))
  #     if(search_recipe == '\n' or search_recipe == "" or search_recipe == " "):
  #       print("Please enter a valid recipe")
  #     else:
  #       num_results = ui.find_best_match(search_recipe)
  #       if(num_results > 0):
  #         ui.display_dishes()
  #       else:
  #         print("No matches found")
  #   except Exception as e:
  #     print(e)
