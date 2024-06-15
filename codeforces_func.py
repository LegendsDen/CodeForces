import requests
from functools import lru_cache
import json


@lru_cache(maxsize=None)
def get_contests(handle):
    # Fetch all contests
    contest_url = "https://codeforces.com/api/contest.list"
    contest_response = requests.get(contest_url)
    if contest_response.status_code != 200:
        print("Failed to load contests.")
        return []

    contest_data = contest_response.json()
    if contest_data["status"] != "OK":
        print(f"Error: {contest_data['comment']}")
        return []

    all_contests = contest_data["result"]

    # Fetch user's contest participation history
    user_url = f"https://codeforces.com/api/user.rating?handle={handle}"
    user_response = requests.get(user_url)
    if user_response.status_code != 200:
        print("Failed to load user's contest history.")
        return []

    user_data = user_response.json()
    if user_data["status"] != "OK":
        print(f"Error: {user_data['comment']}")
        return []

    user_contests = user_data["result"]
    user_contest_ids = {contest['contestId'] for contest in user_contests}

    # Filter contests to include only finished contests the user has participated in
    finished_user_contests = [
        contest for contest in all_contests
        if contest['id'] in user_contest_ids and contest['phase'] == 'FINISHED'
    ]

    # Sort contests by start time in descending order (most recent first)
    finished_user_contests.sort(key=lambda x: x['startTimeSeconds'], reverse=True)

    # Limit the number of contests
    return finished_user_contests[:5]
# def get_contests(contest_num):                                      
    
#     url = "https://codeforces.com/api/contest.list"
#     response = requests.get(url)
#     if response.status_code != 200:
#         print("Failed to load contests.")
#         return []

#     data = response.json()
#     if data["status"] != "OK":
#         print(f"Error: {data['comment']}")
#         return []
    
#     contests = data["result"]


#     return contests[:contest_num]

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

