import numpy as np
import scipy as sp
import pandas as pd
import re
# from .dir import SimilarDishFinder

class UserInput(object):

  def __init__(self):
    # dataframe that contains entire recipe database with the similar matches
    self.recipe_df = None
    # dataframe
    self.matches_df = []
    self.matched_dish = None
    self.similar_dishes = []

  def read_recipes_csv(self, filepath):
    '''
    Read in CSV file and store in class member
    '''
    self.recipe_df = pd.read_csv(filepath, index_col=0)
    # df.iloc[:,np.r_[0:2,4:5]]
    return

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
      self.similar_dishes = [int(x) for x in self.matches_df.iloc[0]['Dishes_in_Cluster'][1:-1].split(',')]

    return len(self.matches_df)


  def display_dishes(self):
    print(self.recipe_df.iloc[self.similar_dishes]['Dish_Name'].to_string(index=False))

if __name__ == "__main__":
  ui = UserInput()
  ui.read_recipes_csv('Similar_Recipes_man_sub.csv')
  while(True):
    try:
      search_recipe = str(input("Enter your favorite dish: "))
      if(search_recipe == '\n' or search_recipe == "" or search_recipe == " "):
        print("Please enter a valid recipe")
      else:
        num_results = ui.find_best_match(search_recipe)
        if(num_results > 0):
          ui.display_dishes()
        else:
          print("No matches found")
    except Exception as e:
      print(e)
