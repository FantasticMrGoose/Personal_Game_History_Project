from steam import Steam
from decouple import config
import pandas as pd
import requests

KEY = config("STEAM_API_KEY")
steam = Steam(KEY)

# loading csv into data frame
games_df = pd.read_csv('personal_games_history.csv')

# Steam Web-API to return game review score
def get_game_reviews(app_id):

    # parameters to query steam reviews to get total # of reviews instead of in batches
    params = {
        'json': 1,
        'filter': 'all',
        'language': 'all',
        'review_type': 'all',
        'purchase_type': 'all',
        'dat_range': 9223372036854775807
    }

    overall_rating = ''
    total_positive = 0
    total_reviews = 0

    url = f"https://store.steampowered.com/appreviews/{app_id}"
    response = requests.get(url, params=params)

    if response.status_code == 200:

        reviews = response.json()

        overall_reviews = reviews["query_summary"]

        overall_rating = overall_reviews["review_score_desc"]
        total_positive = overall_reviews["total_positive"]
        total_reviews = overall_reviews["total_reviews"]

    else:
        overall_rating = "Game Not Found"

    return overall_rating, total_reviews, total_positive

# Return game info (categories, genres, etc)


def get_game_info(app_id):

    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&cc=cdn"
    response = requests.get(url)

    developers = ''
    publishers = ''
    currency = ''
    base_price = 0
    genre = []
    categories = []
    metacritic = None

    if response.status_code == 200:
        info = response.json()
        if "data" in info[f"{app_id}"]:
            developers = info[f"{app_id}"]["data"]["developers"]
            publishers = info[f"{app_id}"]["data"]["publishers"]
            genre = info[f"{app_id}"]["data"]["genres"]
            categories = info[f"{app_id}"]["data"]["categories"]
            if "metacritic" in info[f"{app_id}"]["data"]:
                metacritic = info[f"{app_id}"]["data"]["metacritic"]["score"]

        genre_list = []
        categories_list = []

        # only gets the values from dict list
        for tags in genre:
            value = tags["description"]
            genre_list.append(value)

        for tags in categories:
            value = tags["description"]
            categories_list.append(value)

        if "data" in info[f"{app_id}"]:
            if info[f"{app_id}"]["data"]["is_free"] == False \
                and "price_overview" in info[f"{app_id}"]["data"]:
                base_price = info[f"{app_id}"]["data"]["price_overview"]["initial"] / 100

        

    return developers, publishers, currency, base_price, genre_list, categories_list, metacritic

# main function
def main():

    num_games = len(games_df)
    
    dev_col = []
    pub_col = []
    base_price_col = []
    genre_col = []
    categories_col = []
    metacritic_col = []
    ratings_col = []
    total_reviews_col = []
    positive_reviews_col = []

    i = 0

    while i < num_games:
        steam_id = games_df.at[i, 'Steam ID']

        # Retrieve general info for all games using steam id
        dev, pub, curr, base_price, genre, categories, metacritic = get_game_info(
        steam_id)

        # Retrieve review score for all games using steam id
        ratings, total_reviews, positive_reviews = get_game_reviews(steam_id)

        # adding info to new column
        dev_col +=[dev] 
        pub_col += [pub]
        base_price_col += [base_price]
        genre_col += [genre]
        categories_col += [categories]
        metacritic_col += [metacritic]
        ratings_col += [ratings]
        total_reviews_col += [total_reviews]
        positive_reviews_col += [positive_reviews]

        i = i + 1

    #load columns to data frame
    games_df["Developer"] = dev_col
    games_df["Publisher"] = pub_col
    games_df["Base Price (CDN)"] = base_price_col
    games_df["Genre"] = genre_col
    games_df["Categories"] = categories_col
    games_df["Metacritic"] = metacritic_col
    games_df["Overall Rating"] = ratings_col
    games_df["Total Reviews"] = total_reviews_col
    games_df["Positive Reviews"] = positive_reviews_col

    #removing square brackets 
    games_df["Developer"] = games_df["Developer"].apply(lambda x: ', '.join(x)\
                                                         if isinstance(x, list) else x)
    games_df["Publisher"] = games_df["Publisher"].apply(lambda x: ', '.join(x) \
                                                        if isinstance(x, list) else x)
    games_df["Genre"] = games_df["Genre"].apply(lambda x: ', '.join(x) \
                                                if isinstance(x, list) else x)
    games_df["Categories"] = games_df["Categories"].apply(lambda x: ', '.join(x) \
                                                          if isinstance(x, list) else x)
                                                            
    #testing
    # column_names = ["Item", "Developer", "Publisher",
    #                 "Base Price (CDN)", "Genre",
    #             "Total Reviews"]
    
    # print(games_df[column_names])

    games_df.to_csv('game_info_main.csv')

main()
