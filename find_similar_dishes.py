import numpy as np
import scipy as sp
import pandas as pd
import regex as re
import ast
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans

class SimilarDishFinder(object):

    def __init__(self, method = 'tfidf', use_health_labels = False):
        """
        Constructor

        :param method: Method to be used to compare recipes, options are 'tfidf' or 'manual'.
        tfidf creates a sparse vector by considering each word in a list of ingredients (all words are concatenated together into a single string)
        manual considers each ingredient in a list of ingredients (ingredients can be multiple words long)
        :type method: string
        :param use_health_labels: if True and 'tfidf' method is selected, adds health labels to concatenated string
        :type use_health_labels: boolean, default False
        """
        self.recipe_df = None
        self.method = method
        self.use_health_labels = use_health_labels
        self.cos_sim_list = []
        self.kmeans_list = []

        if self.method not in ['tfidf', 'manual']:
            raise ValueError("method must be \'tfidf\' or \'manual\'")
        elif self.method != 'tfidf' and use_health_labels:
            raise ValueError("can only use_health_labels when method = \'tfidf\'")

    def clean_ingredients(self, ingredient_list):
        """
        Isolate the ingredients from a list of ingredient strings

        :param ingredient_list: A list of ingredients that needs to be cleaned.
        :type ingredient_list: list of strings
        :return: Cleaned list of strings
        :rtype: list of strings
        """
        stemmer = PorterStemmer() #used to stem ingredient strings
        measurements = [' c ','ounce', 'ounces', 'oz ', 'cups', 'cup', 'tbsp', 'tsp', 'teaspoon', 'teaspoons',\
                        'tablespoon', 'tablespoons', 'bunch', 'bunches', ' can ']
        descriptors = ['ground', 'chopped', 'sliced', 'minced', 'diced', 'grated', 'shredded', 'peeled', 'canned'\
                       'small', 'medium', 'large', ' cold ', ' hot ', ' dry ', ' sweet ', 'toasted', 'plain',\
                       'fresh ', 'frozen', 'thin ', 'thick ', 'creamy', 'whole', 'regular', 'cooked', 'raw ', 'dried',\
                       'purpose', 'unsalted', 'salted', 'frozen', 'sweetened', 'unsweetened']
        inglist = []
        for ingredient in ingredient_list:
            ingredient = ingredient.lower()
            ingredient = ingredient.split(',')[0] #stuff after commas is usually unnecessary description
            ingredient = re.sub(r'\(.+\)', '', ingredient) #remove anything in parentheses
            ingredient = ingredient.split(':')[-1] #take only the portion of the ingredient after a colon
            #an ingredient is usually formatted {units} {measurement} {ingredient} this regex pattern looks for units and measurements
            #it splits on them, only preserving the right-hand side (ingredients)
            ingredient = re.split(r'\d+[\s-]*[\w-]+\s',ingredient)[-1]
            ingredient = re.split(r'[\d\/*\d*]+', ingredient)[-1] #remove any leftover numbers or fractions
            ingredient = re.sub(r'[^a-zA-Z\s]*', '', ingredient)  # remove any characters that aren't letters
            #split on a variety of prepositions, take either the left or right-hand side depending on how it is typically used
            ingredient = ingredient.split('.')[-1]\
                                   .split('(')[0]\
                                   .split('of ')[-1]\
                                   .split(' in ')[0]\
                                   .split(' for ')[0]\
                                   .split(' or ')[0]\
                                   .split(' with ')[0]\
                                   .split('such as ')[0]
            ingredient = re.sub(r'[^a-zA-Z\s]*', '', ingredient) #remove any characters that aren't letters or whitespace
            #each of the measurements and descriptors usually precedes the actual ingredient (with a few exceptions)
            #we split on each of the words in each list and take the second part, which is what we really want
            for i in measurements + descriptors:
                ingredient = ingredient.split(i)[-1]
            ingredient = ingredient.replace('chilli', 'chili').strip() #small manual cleanup and strip whitespace
            #Use PorterStemmer to regularize the words and improve matches
            ingredient = ' '.join([stemmer.stem(word) for word in ingredient.split() if len(word)>1])

            if ingredient:
                inglist.append(ingredient)

        return inglist

    def read_menu_data(self, filepath, max_rows=None):
        """
        read in menu data from csv

        :param filepath: filepath for menu data
        :type filepath: str
        :return: Pandas dataframe with cleaned recipe data
        :rtype: list of strings
        """
        recipes = pd.read_csv(filepath, index_col=0)

        if max_rows:
            np.random.seed(47)
            randrows = np.random.choice(recipes.shape[0],max_rows,replace=False)
            recipes = recipes.iloc[randrows,:]

        recipes.reset_index(inplace=True)
        recipes.drop(columns='index', inplace=True)
        recipes['Health_Label'] = recipes['Health_Label'].apply(lambda x: ast.literal_eval(x))
        recipes['Recipe'] = recipes['Recipe'].apply(lambda x: ast.literal_eval(x))

        if self.method == 'tfidf':
            if self.use_health_labels:
                recipes['Ingredients'] = recipes.apply(lambda x: ' '.join(self.clean_ingredients(x['Recipe'])+x['Health_Label']), axis=1)
            else:
                recipes['Ingredients'] = recipes['Recipe'].apply(lambda x: ' '.join(self.clean_ingredients(x)))
        else:
            recipes['Ingredients'] = recipes['Recipe'].apply(lambda x: self.clean_ingredients(x))

        self.recipe_df = recipes
        return recipes

    def create_ingredient_vectors(self, recipe_df):
        """
        create sparse ingredient matrix - helper function for find_closest_matches

        :param recipe_df: dataframe with cleaned recipe data
        :type recipe_df: Pandas dataframe
        :return: sparse array of ingredients (each row represents the ingredient vector for a dish)
        :rtype: sparse matrix
        """
        if self.method == 'tfidf':
            vectorizer = TfidfVectorizer()
            sparse = vectorizer.fit_transform(recipe_df['Ingredients'])

        else:
            #MANUAL MATRIX CREATION METHOD
            recipes = recipe_df['Ingredients']
            ingredient_list = []
            #create list of all ingredients
            for recipe in recipes:
                ingredient_list.extend(recipe)
            #find unique ingredients
            uniques = np.unique(ingredient_list)
            #create matrix of ingredients, each row represents one recipe
            mat = []
            for recipe in recipes:
                mat.append([1 if ingredient in recipe else 0 for ingredient in uniques])
            mat = np.array(mat)
            # scale ingredients by inverse frequency of appearance
            row_sum = np.sum(mat, axis=1)+.000000001
            col_sum = np.log(np.sum(mat, axis=0)+.000000001)
            scaled = mat/(row_sum[:,None]*col_sum)
            #create sparse ingredient matrix
            sparse = sp.sparse.csr_matrix(scaled)

        return sparse

    def find_closest_matches(self, num_matches=5, num_clusters=None, num_SVD_components=10, test_algos=False):
        """
        find similar ingredients

        :param num_matches: number of matching ingredients to return, default 5
        :type num_matches: int
        :param num_clusters: number of clusters, default = number of recipes/num_matches
        :type num_matches: int
        :param num_SVD_components: number of SVD components to use, default 10
        :type num_SVD_components: int
        :param test_algos: If True, will store list of mean cosine_similarities to evaluate algorithms
        :type test_algos: bool, default False
        :return: sparse array of ingredients (each row represents the ingredient vector for a dish)
        :rtype: Scipy sparse CSR matrix
        """
        # if number of clusters is not passed default to num_recipes/num_matches
        if not num_clusters:
            num_clusters = int(self.recipe_df.shape[0]/(num_matches))

        dish_names = self.recipe_df['Dish_Name'].to_numpy()

        #create sparse matrix and calculate cosine similarities
        sparse = self.create_ingredient_vectors(self.recipe_df)
        similarities = cosine_similarity(sparse)

        # get indices of the top 5 most similar dishes (including the dish itself)
        top_6 = np.argsort(similarities)[:,-1:-2-num_matches:-1]
        #add mean cosine similarities for dishes within top 6 to list if we are testing algos
        if test_algos:
            for row in top_6:
                self.cos_sim_list.append(np.mean(cosine_similarity(sparse[row])))

        # get indices of the top 5 most similar dishes (excluding the dish itself)
        top_5 = top_6[:,1:]
        top_5_names = dish_names[top_5]
        self.recipe_df[f'Top_{num_matches}_Indices'] = top_5.tolist() #add top dish indices
        self.recipe_df[f'Top_{num_matches}_Dish_Names'] = top_5_names.tolist() #add top dish names

        #use SVD to reduce dimensions of data
        svd = TruncatedSVD(n_components=num_SVD_components)
        reduced = svd.fit_transform(sparse)

        #find clusters of reduced data
        clusters = KMeans(n_clusters=num_clusters).fit_predict(reduced)

        #create lists to hold the indices and names of other dishes in a dish's cluster
        cluster_indices = []
        cluster_names = []
        for i, cluster in enumerate(clusters):
            ixs = np.where(clusters==cluster)[0]

            #if we are comparing algos, add mean cosine similarity to list
            if test_algos:
                self.kmeans_list.append(np.mean(cosine_similarity(sparse[ixs,:])))

            ixs = ixs[ixs!=i] #remove recipe from cluster
            cluster_indices.append(ixs.tolist())
            cluster_names.append(dish_names[ixs].tolist())

        self.recipe_df['Dishes_in_Cluster'] = cluster_indices
        self.recipe_df['Cluster_Dish_Names'] = cluster_names

        return self.recipe_df

    def compare_algorithms(self, verbose = True):
        '''
        compares average of the average cosine similarities for the dishes recommended for each recipe

        :param: verbose - if True, prints out a comparison between the cosine similarity and kmeans algorithms
        :type: bool, default True
        :return: cos_sim_average, kmeans_average
        :rtype: float
        '''
        cos_avg = np.mean(self.cos_sim_list)
        kmeans_avg = np.mean(self.kmeans_list)
        if verbose:
            print('The average cosine similarity for the cosine similarity algorithm is '\
                  +f'{cos_avg:.2f}'+'\n'\
                  +'The average cosine similarity for the kmeans algorithm is '\
                  +f'{kmeans_avg:.2f}')

        return cos_avg, kmeans_avg

    def write_to_csv(self, filepath):
        """
        write updated dataframe to csv

        :param filepath: path of file to be written
        :type filepath: str
        """
        self.recipe_df.to_csv(path_or_buf=filepath)

if __name__ == "__main__":
    finder = SimilarDishFinder(use_health_labels=True)
    finder.read_menu_data('Recipes_A.csv')
    finder.find_closest_matches(test_algos=True)
    cos_avg, kmeans_avg = finder.compare_algorithms()
    finder.write_to_csv('Similar_Recipes_man_sub.csv')
