import requests
from functools import lru_cache
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures, MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau



@lru_cache(maxsize=None)
# def get_contests(handle):
#     # Fetch all contests
#     contest_url = "https://codeforces.com/api/contest.list"
#     contest_response = requests.get(contest_url)
#     if contest_response.status_code != 200:
#         print("Failed to load contests.")
#         return []

#     contest_data = contest_response.json()
#     if contest_data["status"] != "OK":
#         print(f"Error: {contest_data['comment']}")
#         return []

#     all_contests = contest_data["result"]

#     # Fetch user's contest participation history
#     user_url = f"https://codeforces.com/api/user.rating?handle={handle}"
#     user_response = requests.get(user_url)
#     if user_response.status_code != 200:
#         print("Failed to load user's contest history.")
#         return []

#     user_data = user_response.json()
#     if user_data["status"] != "OK":
#         print(f"Error: {user_data['comment']}")
#         return []

#     user_contests = user_data["result"]
#     user_contest_ids = {contest['contestId'] for contest in user_contests}

#     # Filter contests to include only finished contests the user has participated in
#     finished_user_contests = [
#         contest for contest in all_contests
#         if contest['id'] in user_contest_ids and contest['phase'] == 'FINISHED'
#     ]

#     # Sort contests by start time in descending order (most recent first)
#     finished_user_contests.sort(key=lambda x: x['startTimeSeconds'], reverse=True)

#     # Limit the number of contests
#     return finished_user_contests
def get_contests(contest_num):                                      
    
    url = "https://codeforces.com/api/contest.list"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to load contests.")
        return []

    data = response.json()
    if data["status"] != "OK":
        print(f"Error: {data['comment']}")
        return []
    
    contests = data["result"]
    finished_contests = [contest for contest in contests if contest['phase'] == 'FINISHED']
    return finished_contests[:contest_num]

@lru_cache(maxsize=None)
def get_contest_problems(contest_id):
    print(contest_id)

    url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=1"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to load contest problems for contest {contest_id}.")
        return []

    data = response.json()
    if data["status"] != "OK":
        print(f"Error: {data['comment']}")
        return []
    
    return data["result"]["problems"]
    # return []



# Define a function to get user submissions data from the Codeforces API:
@lru_cache(maxsize=None)
def get_user_submissions(handle):
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to load user submissions for {handle}.")
        return []

    data = response.json()

    if data["status"] != "OK":
        print(f"Error: {data['comment']}")
        return []

    return data["result"]

def build_table_data(contests, submissions):
    
    
    table_data = []
    problems_status = {}

    for submission in submissions:
        problem_key = (submission["problem"]["contestId"],
                    submission["problem"]["index"])
        if submission["verdict"] == "OK":
            problems_status[problem_key] = "green"
        elif submission["verdict"] != "OK" and problem_key not in problems_status:
            problems_status[problem_key] = "red"

    contest_problems_dict = {}
    for contest in contests:
        print(contest)
        if contest["phase"] != "FINISHED":
            continue

    #     # if contest["id"] > 30:
    #     #     continue

        contest_problems = get_contest_problems(contest["id"])
        for problem in contest_problems:
            if contest["id"] is None or contest["name"] is None or problem["index"] is None:
                continue
            problem_key = (contest["id"], problem["index"])
            problem_status = problems_status.get(problem_key, "white")
            formatted_problem_name = f"{problem['index']}"
            # problem.get("index", "N/A")
            problem_rating = problem.get("rating", "N/A")
            if contest["id"] not in contest_problems_dict:
                contest_problems_dict[contest["id"]] = {
                    "name": contest["name"],
                    "problems": [(formatted_problem_name, problem_rating, problem_status)],
                }
            else:
                contest_problems_dict[contest["id"]]["problems"].append(
                    (formatted_problem_name, problem_rating, problem_status))

    for contest_id, contest_data in contest_problems_dict.items():
        problems_str = ", ".join(
            [f"{p[0]} ({p[1]}) [{p[2]}]" for p in contest_data["problems"]])
        row = [contest_id, contest_data["name"], problems_str]
        table_data.append(row)
    
    return table_data


def generate_html_table(table_data):
    headers = ["Contest ID", "Contest Name", "Problems"]

    # Create the opening and closing HTML tags for the table and the header row
    html_table = '<table>\n<thead>\n<tr>\n'
    for header in headers:
        html_table += f'<th style="border-bottom: thick double #32a1ce;">{header}</th>\n'
    html_table += '</tr>\n</thead>\n<tbody>\n'

    # Create the table rows and cells
    for row in table_data:
        html_table += '<tr">\n'
        for i, cell in enumerate(row):
            if i == 2:  # The Problems column
                html_table += '<td>'
                problems = cell.split(', ')
                for problem in problems:
                    problem_parts = problem.strip().split(' ')
                    problem_name = problem_parts[0]
                    problem_rating = problem_parts[1].strip('()')
                    problem_status = problem_parts[2].strip('[]')
                    html_table += f'<span style="display: inline-block; text-align: center; width: 80px; margin-right: 5px; padding: 2px; background-color: {problem_status};">{problem_name} \n ({problem_rating})</span>'
                html_table += '</td>\n'
            else: # The Contest ID and Contest Name columns
                html_table += f'<td>{cell}</td>\n'
        html_table += '</tr>\n'

    # Close the HTML table tag
    html_table += '</tbody>\n</table>'

    return html_table


def save_plot_as_image(df, y_pred, all_contest_ids, all_ratings):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Contest Number'], df['Rating'], 'o', label='Actual Ratings')
    plt.plot(df['Contest Number'], y_pred, label='Expected Ratings', linestyle='solid')
    plt.plot(all_contest_ids, all_ratings, label='Predicted Ratings (LSTM)', linestyle='--')
    plt.xlabel('Contest ID')
    plt.ylabel('Rating')
    plt.title('User Skill Progression Analysis using LSTM')
    plt.legend()
    plt.savefig('static/plot.png')
    plt.close()

def fetch_user_ratings(user_handle):
    url = f"https://codeforces.com/api/user.rating?handle={user_handle}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch data from Codeforces API")
    
    data = response.json()
    if data['status'] != 'OK':
        raise Exception("Failed to fetch data: " + data['comment'])
    
    return data['result']

def process_and_predict(codeforces_id, contest_num):
    # Fetch data for a specific user
    ratings_data = fetch_user_ratings(codeforces_id)
    
    # Process data into a DataFrame
    df = pd.DataFrame(ratings_data)
    df = df[['contestId', 'newRating']]
    df.rename(columns={'contestId': 'Contest ID',  'newRating': 'Rating'}, inplace=True)
    df['Contest Number'] = range(1, len(df) + 1)

    # Apply Polynomial Regression
    X = df[['Contest Number']]
    y = df['Rating']
    poly = PolynomialFeatures(degree=3)
    X_poly = poly.fit_transform(X)
    model = LinearRegression()
    model.fit(X_poly, y)
    y_pred = model.predict(X_poly)

    # Scale the ratings for LSTM model
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df['Rating'].values.reshape(-1, 1))

    # Prepare the data for LSTM
    def create_dataset(data, time_step=1):
        X, Y = [], []
        for i in range(len(data) - time_step):
            a = data[i:(i + time_step), 0]
            X.append(a)
            Y.append(data[i + time_step, 0])
        return np.array(X), np.array(Y)

    time_step = 5
    X, y = create_dataset(scaled_data, time_step)
    X = X.reshape(X.shape[0], X.shape[1], 1)

    # Split the data into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    # Build the LSTM model
    model = Sequential()
    model.add(Bidirectional(LSTM(50, return_sequences=True), input_shape=(time_step, 1)))
    model.add(Dropout(0.2))
    model.add(Bidirectional(LSTM(50, return_sequences=False)))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Implement Early Stopping and Learning Rate Reduction
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=0.0001)

    # Train the LSTM model
    history = model.fit(X_train, y_train, epochs=100, batch_size=1, verbose=2, validation_data=(X_val, y_val), callbacks=[early_stop, reduce_lr])

    # Predict ratings for the existing data
    train_predict = model.predict(X)
    train_predict = scaler.inverse_transform(train_predict)

    # Predict ratings for the next 5 contests
    future_contests = 5
    input_data = scaled_data[-time_step:].reshape(1, time_step, 1)
    predicted_ratings = []

    for _ in range(future_contests):
        predicted_rating = model.predict(input_data)
        predicted_ratings.append(predicted_rating[0, 0])
        input_data = np.append(input_data[:, 1:, :], predicted_rating.reshape(1, 1, 1), axis=1)

    predicted_ratings = scaler.inverse_transform(np.array(predicted_ratings).reshape(-1, 1))

    # Combine current and future data for plotting
    all_contest_ids = np.arange(1, len(df) + 1 + future_contests)
    all_ratings = np.concatenate([df['Rating'].values, predicted_ratings.flatten()])

    # Save the plot
    save_plot_as_image(df, y_pred, all_contest_ids, all_ratings)

    # Generate the table data
    contests = get_contests(contest_num)
    print(5)
    submissions = get_user_submissions(codeforces_id)

    print(6)
    table_data = build_table_data(contests, submissions)

    # Generate HTML table
    html_table = generate_html_table(table_data)
    print(4)

    return html_table

