import dishes.find_similar_dishes as sdf
import dishes.display_dishes as uinput
import os
from shutil import copy

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, './DEMO')
try:
    os.mkdir(filename)
except OSError as error:
    print("DEMO folder already exists.")

try:
    os.mkdir(filename+'/restaurant_location')
except OSError as error:
    print("restaurant_location folder already exists.")


finder = sdf.SimilarDishFinder(use_health_labels=True)
finder.read_menu_data(['./dishes/Recipes_A.csv', './dishes/Recipes_B.csv', './dishes/Recipes_C.csv'])
recipe_df, restaurant_df = finder.find_closest_matches(test_algos=True)
finder.compare_algorithms()
finder.write_to_csv(recipe_path='./DEMO/recipes_df.csv', restaurant_path='./DEMO/restaurant_df.csv')

ui = uinput.UserInput()
ui.read_recipes_csv('./DEMO/recipes_df.csv')
ui.read_restaurant_tsv('./menu/menu_data/restaurant_list.tsv', restaurant_df_file='./DEMO/restaurant_df.csv')
ui.generate_csv_for_d3_num2(ofn='./DEMO/d3_data.csv')

copy('./viz/index.html', './DEMO/.')
copy('./viz/restaurant_location/updated_restaurant_list.tsv', './DEMO/restaurant_location/.')
