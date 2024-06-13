import requests
from functools import lru_cache
import json
from codeforces_func import (get_contests, get_contest_problems,
                            get_user_submissions, build_table_data,
                            generate_html_table)

# codeforces_id='Sushant81'
# submissions = get_user_submissions(codeforces_id)
def filter_submissions_by_tag(submissions, given_tag):
    filtered_problems_dict = {}

    for submission in submissions:
        problem = submission.get("problem", {})
        
        # Check if "tags" is in problem and is a list
        if "tags" in problem and isinstance(problem["tags"], list):
            if given_tag in problem["tags"]:
                problem_key = (problem["contestId"], problem["index"])
                verdict = submission["verdict"]

                # If the problem is already in the dictionary, update the verdict
                if problem_key in filtered_problems_dict:
                    if verdict == "OK":
                        filtered_problems_dict[problem_key]["verdict"] = "OK"
                else:
                    filtered_problems_dict[problem_key] = {
                        "contestId": problem["contestId"],
                        "index": problem["index"],
                        "name": problem["name"],
                        "rating":problem["rating"],
                        "verdict": verdict,
                        "problem_url": f"https://codeforces.com/problemset/problem/{problem['contestId']}/{problem['index']}"
                    }
        else:
            print(f"Problem {problem.get('name', 'unknown')} does not have valid tags.")
    
    # Convert the dictionary to a list
    filtered_problems = list(filtered_problems_dict.values())

    return filtered_problems

# given_tag = "binary search"

# filtered_problems = filter_submissions_by_tag(submissions, given_tag)

# for problem in filtered_problems:
#     print(f"Problem: {problem['contestId']}{problem['index']} - {problem['name']}, Verdict: {problem['verdict']}, Problem URL: {problem['problem_url']}")


