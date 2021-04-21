    DESCRIPTION - Describe the package in a few paragraphs
    This package scrapes the menus of the top 500 most popular restaurants 
    in NYC according to https://www.allmenus.com/ny/new-york/-/ to generate
    a list of restaurant dishes.

    The restaurant dishes are compared with known recipes using the Edamam
    Recipe Search API(https://developer.edamam.com/edamam-recipe-api).
    Combining the two datasets, the package generates a CSV file compiling
    a 1:1 ratio between recipes and restaurant dishes with supporting
    information including nutritional data and ingredients.

    Using the ingredients and nutritional data, the package determines 
    similar restaurant dishes. For instance, a mocha frappe cappucino may
    map to almond milk latte, mocha chocolate coffee, etc.. from a variety
    of restaurants. The dish similarities are determined using cosine 
    similarity.
    
    The similar dish data is formatted to csv files and eventually
    visualized using d3.

    INSTALLATION - How to install and setup your code
    1. python scrape_menu_dishes.py
    2. Create developer account at [Edamam Recipe Search API](https://developer.edamam.com/edamam-recipe-api)
    3. Modify application key and application ID in scrape_recipes.py __init__ function.
    4. python scrape_recipes.py to generate CSV's with Recipe Data.
    5. python find_grouped_dishes.py to generate a restaurant dishes and its similar results.
    6. python display_dishes.py to generate file to be used in d3 visualization

    EXECUTION - How to run a demo on your code
    To run the d3 visualization using python3:
    Navigate to ./viz folder
    Run a python server (python -m http.server 8888)
    Navigate to http://localhost:8888/index.html in chrome browser.
    Type in dishes to see local restaurants in New York and similar foods.
