    DESCRIPTION - Describe the package in a few paragraphs
    This package scrapes the menus of the top 500 most popular restaurants 
    in NYC according to https://www.allmenus.com/ny/new-york/-/ to generate
    a list of restaurant dishes.

    The restaurant dishes are compared with known recipes using the Edamam
    Recipe Search API(https://developer.edamam.com/edamam-recipe-api).
    Combining the two datasets, the package generates a CSV file compiling
    a 1:1 ratio between recipes and restaurant dishes with supporting
    information including nutritional data and ingredients.

    We took the matched restaurant dish and recipe data and converted it into 
    vector representations of ingredients that can be used to calculate 
    recipe similarity. We then took the sparse ingredient matrix and found the 
    most similar dishes to each recipe by using two methods: 
    cosine similarity and kmeans clustering. We then compared the results 
    of the two methods to determine which recommended the most similar dishes. 
    For instance, a mocha frappe cappucino may map to almond milk latte, 
    mocha chocolate coffee, etc from a variety of restaurants. The code for 
    ingredient vector creation and finding the most similar dishes can be found in 
    find_similar_dishes.py.
    
    The similar dish data is formatted to csv files and eventually
    visualized in an interactive html page as a list and a map. When a user
    searches and selects a dish, similar dishes and the restaurants that carry 
    the similar dishes are shown in the map. The restaurants are color coded 
    to show the average similarity score of the similar dishes they serve. 
    Clicking on a similar dish highlights the restaurants carrying it in the 
    list and the map. The technologies used in visualization are Bootstrap, 
    D3, Leaflet, OpenStreetMap and jQuery. 
    
    A more detailed walkthrough of the code is located README.md.

    INSTALLATION - How to install and setup your code
    1. `python scrape_menu_dishes.py`
    2. Create developer account at [Edamam Recipe Search API](https://developer.edamam.com/edamam-recipe-api)
    3. Modify application key and application ID in scrape_recipes.py __init__ function.
    4. `python scrape_recipes.py` to generate CSV's with Recipe Data.
    5. `python find_similar_dishes.py` to generate a restaurant dishes and its similar results.
    6. `python display_dishes.py` to generate file to be used in d3 visualization

    EXECUTION - How to run a demo on your code
    To run the d3 visualization using python3:
    Navigate to ./viz folder
    Run a python server (`python -m http.server 8888`)
    Navigate to http://localhost:8888/index.html in chrome browser.
    Type in dishes to see local restaurants in New York and similar foods.
