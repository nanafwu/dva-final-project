import numpy as np
import scipy as sp
import pandas as pd
# from .dir import SimilarDishFinder

def read_similar_dishes(filepath, max_rows=None):
  recipes = pd.read_csv(filepath, index_col=0)
  # df.iloc[:,np.r_[0:2,4:5]]
  r1 = recipes.iloc[:, -4:]
  return r1
  

def display_dishes(dish):
    """
    Display the dishes based on user input string

    :param dish: restaurant dish(food) name
    :type dish: string
    """
    pass



if __name__ == "__main__":
  recipes = read_similar_dishes('Similar_Recipes_man_sub.csv')
  print(recipes.head(5))
  # while(True):
  #   try:
  #     dish = str(input("Enter your favorite dish: "))
  #     display_dishes()
  #   except Exception as e:
  #     print(e)
