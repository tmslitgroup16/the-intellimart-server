from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from itertools import combinations
import pickle

food_df = pickle.load(open('dish_1.pkl', 'rb'))


def generate_combinations(ingredients, iteration):
    return list(combinations(ingredients, len(ingredients) - iteration))


def recommend_dishes(ingredients_group1, ingredients_group2, previous_recommendations):
    # Use TfidfVectorizer to convert ingredients into TF-IDF vectors
    vectorizer = TfidfVectorizer()
    ingredients_matrix = vectorizer.fit_transform(food_df['Ingredients'])

    # Combine ingredients from both groups
    all_ingredients = ingredients_group1 + ingredients_group2

    # Calculate cosine similarity between input ingredients and all dishes
    cosine_sim = cosine_similarity(vectorizer.transform(
        [' '.join(all_ingredients)]), ingredients_matrix)

    # Get dish recommendations sorted by similarity
    recommendations = food_df.iloc[cosine_sim.argsort()[0][::-1]]

    # Filter out dishes recommended in previous iterations
    recommendations = recommendations[~recommendations['Dishes'].isin(
        previous_recommendations)]

    return recommendations['Dishes'].tolist()


def main_recommendation(input_ingredients):
    input_ingredients = input_ingredients.split(", ")
    all_recommendations = []
    final_dishes = []

    for iteration in range(len(input_ingredients)):
        group1 = input_ingredients[:len(input_ingredients) - iteration]
        group2 = input_ingredients[len(input_ingredients) - iteration:]

        combinations_list = generate_combinations(group1, iteration)

        for combination in combinations_list:
            recommended_dishes = recommend_dishes(
                list(combination), group2, all_recommendations)
            all_recommendations += recommended_dishes

            # Check if at least 5 dishes are recommended
            if len(all_recommendations) >= 5:
                final_dishes = all_recommendations[:5]
                recc_df = food_df[food_df['Dishes'].isin(final_dishes) & food_df['Ingredients'].apply(
                    lambda x: any(ingredient in x for ingredient in input_ingredients))]
                resultant_dishes = recc_df['Dishes'].tolist()
                resultant_dishes.reverse()
                return resultant_dishes


def final_recommendation_2(input_ingredients):
    x = main_recommendation(input_ingredients)
    return x


def diet_2(input_ingredients):
    x = main_recommendation(input_ingredients)
    y = []
    for dish in x:
        for index, row in food_df.iterrows():
            if (row['Dishes'] == dish):
                y.append(row['Diet'])
    return y
