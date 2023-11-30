# app.py
from flask import Flask, render_template, request
from sklearn.preprocessing import StandardScaler
import pandas as pd
import pickle
import os

import math # To round values.

app = Flask(__name__)

# Load the models at startup
parent_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
win_prediction_model_path = os.path.join(
    parent_directory, 'NbaPredict', 'checkpoints', 'nba_win_prediction_model.pkl')
score_prediction_model_path = os.path.join(
    parent_directory, 'NbaPredict', 'checkpoints', 'nba_score_prediction_model.pkl')

with open(win_prediction_model_path, 'rb') as model_file:
    win_model = pickle.load(model_file)

with open(score_prediction_model_path, 'rb') as model_file:
    points_model = pickle.load(model_file)

data_file_path = os.path.join(
    parent_directory, 'NbaPredict', 'team_box_all_merged.csv')


def preprocess_outcome_data():
    # Work with only the items from the 2023-24 season
    all_data = pd.read_csv(data_file_path)
    teams = all_data["TEAM"].values.tolist()
    web_data = all_data.loc[all_data['season'] == '2023-24'].drop(
        columns=['Unnamed: 0', 'GAME DATE', 'MATCH UP', 'season', 'TEAM', 'NETRTG', '+/-', 'PIE'])
    web_data_x = web_data.drop(columns=['W/L'])
    return teams[:10], web_data_x.values.tolist()


def preprocess_score_data():
    # Work with only the items from the 2023-24 season
    all_data = pd.read_csv(data_file_path)
    teams = all_data["TEAM"].values.tolist()
    web_data = all_data.loc[all_data['season'] == '2023-24'].drop(
        columns=['Unnamed: 0', 'GAME DATE', 'MATCH UP', 'season', 'TEAM', 'FGM', 'FGA', '3PM', '3PA', 'FTM', 'FTA'])
    web_data_x = web_data.drop(columns=['PTS'])
    return teams[:34], web_data_x.values.tolist()



def predict_team_outcome(data_item):
    prediction = win_model.predict(data_item)
    return prediction


def predict_team_points(data_item):
    prediction = points_model.predict(data_item)
    return prediction


# Get data users will select to make predictions on
outcome_data_listings = preprocess_outcome_data()
scores_data_listings = preprocess_score_data()


@app.route('/')
def home():
    outcome_teams = outcome_data_listings[0]
    scores_teams = scores_data_listings[0]
    return render_template('index.html', outcome_data_listings=outcome_teams, scores_data_listings=scores_teams)


@app.route('/predict_outcome', methods=['POST'])
def predict_outcome():
    team_index = int(request.form['selected_team_data'])
    selected_team = outcome_data_listings[0][team_index]
    selected_data = outcome_data_listings[1][team_index]
    
    # Perform actions or return information related to the selected team
    prediction = predict_team_outcome([selected_data])

    outcome_teams = outcome_data_listings[0]
    scores_teams = scores_data_listings[0]

    return render_template(
        'index.html',
        outcome_prediction=("WIN" if int(prediction[0]) == 1 else "LOOSE"),
        selected_team=selected_team,
        outcome_data_listings=outcome_teams,
        scores_data_listings=scores_teams)


@app.route('/predict_score', methods=['POST'])
def predict_score():
    team_index = int(request.form['selected_score_data'])
    selected_team = scores_data_listings[0][team_index]
    selected_data = scores_data_listings[1][team_index]
    
    # Perform actions or return information related to the selected player
    prediction = predict_team_points([selected_data])

    outcome_teams = outcome_data_listings[0]
    scores_teams = scores_data_listings[0]

    return render_template(
        'index.html',
        score_prediction=math.ceil(prediction[0]),
        selected_team=selected_team,
        outcome_data_listings=outcome_teams,
        scores_data_listings=scores_teams)


if __name__ == '__main__':
    app.run(debug=True)
