import requests
from functools import lru_cache
import json
from codeforces_func import (get_contests, get_contest_problems,
                            get_user_submissions, build_table_data,
                            generate_html_table)
import time
import secrets
import hashlib
import random
import string
from bs4 import BeautifulSoup

# codeforces_id='akkafakka'
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
                        "rating": problem.get("rating", "N/A"),
                        "verdict": verdict,
                        "problem_url": f"https://codeforces.com/problemset/problem/{problem['contestId']}/{problem['index']}",
                        "submission_time": submission["creationTimeSeconds"]
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

def generate_api_sig(api_key, secret, method_name, params):
    # Generate a random 6-character string
    rand = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    
    # Add apiKey and time to parameters
    params['apiKey'] = api_key
    params['time'] = str(int(time.time()))
    
    # Sort parameters lexicographically
    sorted_params = sorted(params.items())
    
    # Create the base string
    base_string = f"{rand}/{method_name}?" + '&'.join([f"{k}={v}" for k, v in sorted_params]) + f"#{secret}"
    
    # Generate SHA-512 hash
    hash_object = hashlib.sha512(base_string.encode('utf-8'))
    hash_hex = hash_object.hexdigest()
    
    # Construct the apiSig
    api_sig = f"{rand}{hash_hex}"
    
    return api_sig

def get_friends(api_key, secret, only_online):
    method_name = "user.friends"
    params = {}

    if only_online:
        params["onlyOnline"] = "true"
    
    api_sig = generate_api_sig(api_key, secret, method_name, params)
    current_time = str(int(time.time()))

    request_url = f"https://codeforces.com/api/{method_name}?apiKey={api_key}&time={current_time}&apiSig={api_sig}"

    # If onlyOnline parameter is needed, add it to the request URL
    if "onlyOnline" in params:
        request_url += f"&onlyOnline={params['onlyOnline']}"

    # Make the API call
    response = requests.get(request_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        if data['status'] == 'OK':
            # Extract friends list
            friends = data['result']
            return friends
        else:
            print(f"Error: {data['comment']}")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None

# Example usage
api_key = "e47bcf1700ce426e704a885be232b5209fb58abf"
secret = "e25410caed229ba87bc07e545ccd0eec759f03fc"

# friends = get_friends(api_key, secret, False)
# if friends is not None:
#     print(friends)

def get_recent_submissions(handle):
    url = f"https://codeforces.com/api/user.status?handle={handle}&from=1&count=1000"
    response = requests.get(url)
    data = response.json()
    if data["status"] == "OK":
        return data["result"]
    return []


def check_user_submissions_for_problems(user_submissions, problems):
    user_solved_problems = set()
    
    for submission in user_submissions:
        if submission["verdict"] == "OK":
            problem = submission.get("problem", {})
            problem_key = (problem["contestId"], problem["index"])
            user_solved_problems.add(problem_key)
    
    for problem in problems:
        problem_key = (problem["contestId"], problem["index"])
        problem["user_solved"] = problem_key in user_solved_problems


def get_recent_solved_problems_by_friends(api_key, secret, only_online, given_tag,codeforces_id):
    friends = get_friends(api_key, secret, only_online)
    unique_problems = {}

    for friend in friends:
        submissions = get_recent_submissions(friend)
        filtered_problems = filter_submissions_by_tag(submissions, given_tag)

        for problem in filtered_problems:
            problem_key = (problem["contestId"], problem["index"])
            if problem_key not in unique_problems:
                unique_problems[problem_key] = {
                    "contestId": problem["contestId"],
                    "index": problem["index"],
                    "name": problem["name"],
                    "rating": problem["rating"],
                    "friend_handle": friend,
                    "problem_url": problem["problem_url"],
                    "submission_time": problem["submission_time"]
                }

    # Sort by most recent submission time
    sorted_problems = sorted(unique_problems.values(), key=lambda x: x["submission_time"], reverse=True)
    
    # Get the most recent 30 problems
    # print(sorted_problems)
    most_recent_30_problems = sorted_problems[:30]
    print(most_recent_30_problems)
    user_submissions=get_user_submissions(codeforces_id)
    check_user_submissions_for_problems(user_submissions, most_recent_30_problems)
    return most_recent_30_problems


# def get_problem_links(contest_id):
#     url = f"https://codeforces.com/contest/{contest_id}"
#     response = requests.get(url)
#     if response.status_code != 200:
#         return None

#     soup = BeautifulSoup(response.content, 'html.parser')
#     problem_links = []
#     for link in soup.find_all('a', href=True):
#         href = link['href']
#         if href.startswith(f"/contest/{contest_id}/problem/"):
#             problem_links.append(f"https://codeforces.com{href}")
#     return problem_links

# def scrape_editorial(problem_url):
#     response = requests.get(problem_url)
#     if response.status_code != 200:
#         return None

#     soup = BeautifulSoup(response.content, 'html.parser')
#     editorial_section = soup.find('div', class_='ttypography')
    
#     if editorial_section:
#         return editorial_section.get_text()
#     else:
#         return None



# import re
# def convert_latex_to_plain_text(latex_text):
#     # Replace LaTeX math symbols with plain text
#     plain_text = latex_text

#     # Replace common LaTeX symbols and commands
#     replacements = [
#         (r'\$\$\$', ''),  # Remove triple dollar signs
#         (r'\$\$', ''),  # Remove double dollar signs
#         (r'\$', ''),  # Remove single dollar signs
#         (r'\\le', '<='),  # Replace \le with <=
#         (r'\\ge', '>='),  # Replace \ge with >=
#         (r'\\lt', '<'),  # Replace \lt with <
#         (r'\\gt', '>'),  # Replace \gt with >
#         (r'\\ldots', '...'),  # Replace \ldots with ...
#         (r'\\dagger', ''),  # Remove \dagger
#         (r'\{', ''),  # Remove {
#         (r'\}', ''),  # Remove }
#         (r'\\,', ' '),  # Replace \, with a space
#         (r'\\;', ' '),  # Replace \; with a space
#         (r'\\ ', ' '),  # Replace \ with a space
#         (r'\\n', '\n'),  # Replace \n with a newline
#         (r'\\t', '\t'),  # Replace \t with a tab
#         (r'\\textbf\{(.*?)\}', r'\1'),  # Remove \textbf
#         (r'\\textit\{(.*?)\}', r'\1'),  # Remove \textit
#         (r'\\text\{(.*?)\}', r'\1'),  # Remove \text
#         (r'_', '_'),  # Replace _ with _
#         (r'\^', '^'),  # Replace ^ with ^
#         (r'\\cdot', '·'),  # Replace \cdot with ·
#         (r'\\times', '×'),  # Replace \times with ×
#         (r'\\div', '÷'),  # Replace \div with ÷
#         (r'\\pm', '±'),  # Replace \pm with ±
#         (r'\\sqrt\{([^}]*)\}', r'√(\1)'),  # Replace \sqrt{} with √()
#         (r'\\frac\{([^}]*)\}\{([^}]*)\}', r'(\1/\2)'),  # Replace \frac{}{} with ()
#         (r'\\left\(', '('),  # Replace \left( with (
#         (r'\\right\)', ')'),  # Replace \right) with )
#         (r'\\left\{', '{'),  # Replace \left{ with {
#         (r'\\right\}', '}'),  # Replace \right} with }
#         (r'\\left\[', '['),  # Replace \left[ with [
#         (r'\\right\]', ']'),  # Replace \right] with ]
#         (r'\\begin\{.*?\}', ''),  # Remove \begin{...}
#         (r'\\end\{.*?\}', ''),  # Remove \end{...}
#         (r'\\sum', '∑'),  # Replace \sum with ∑
#         (r'\\int', '∫'),  # Replace \int with ∫
#     ]

#     for pattern, replacement in replacements:
#         plain_text = re.sub(pattern, replacement, plain_text)

#     return plain_text

# # LaTeX input
# latex_text = """

# "C. Lexicographically Largesttime limit per test2 secondsmemory limit per test256 megabytesinputstandard inputoutputstandard outputStack has an array $$$a$$$ of length $$$n$$$. He also has an empty set $$$S$$$. Note that $$$S$$$ is not a multiset.He will do the following three-step operation exactly $$$n$$$ times:  Select an index $$$i$$$ such that $$$1 \\leq i \\leq |a|$$$.  Insert$$$^\\dagger$$$ $$$a_i + i$$$ into $$$S$$$.  Delete $$$a_i$$$ from $$$a$$$. Note that the indices of all elements to the right of $$$a_i$$$ will decrease by $$$1$$$. Note that after $$$n$$$ operations, $$$a$$$ will be empty.Stack will now construct a new array $$$b$$$ which is $$$S$$$ sorted in decreasing order. Formally, $$$b$$$ is an array of size $$$|S|$$$ where $$$b_i$$$ is the $$$i$$$-th largest element of $$$S$$$ for all $$$1 \\leq i \\leq |S|$$$.Find the lexicographically largest$$$^\\ddagger$$$ $$$b$$$ that Stack can make.$$$^\\dagger$$$ A set can only contain unique elements. Inserting an element that is already present in a set will not change the elements of the set.$$$^\\ddagger$$$ An array $$$p$$$ is lexicographically larger than a sequence $$$q$$$ if and only if one of the following holds:   $$$q$$$ is a prefix of $$$p$$$, but $$$p \\ne q$$$; or  in the first position where $$$p$$$ and $$$q$$$ differ, the array $$$p$$$ has a larger element than the corresponding element in $$$q$$$. Note that $$$[3,1,4,1,5]$$$ is lexicographically larger than $$$[3,1,3]$$$, $$$[\\,]$$$, and $$$[3,1,4,1]$$$ but not $$$[3,1,4,1,5,9]$$$, $$$[3,1,4,1,5]$$$, and $$$[4]$$$.InputEach test contains multiple test cases. The first line contains a single integer $$$t$$$ ($$$1 \\leq t \\leq 10^4$$$) — the number of test cases. The description of the test cases follows.The first line of each test case contains a single integer $$$n$$$ ($$$1 \\leq n \\leq 3 \\cdot 10^5$$$) — the length of array $$$a$$$.The second line of each test case contains $$$n$$$ integers $$$a_1,a_2,\\ldots,a_{n}$$$ ($$$1 \\leq a_i \\leq 10^9$$$) — the elements of array $$$a$$$.The sum of $$$n$$$ over all test cases does not exceed $$$3 \\cdot 10^5$$$.OutputFor each test case, output the lexicographically largest $$$b$$$.ExampleInput\n322 151 100 1000 1000000 100000000036 4 8Output\n3 2 \n1000000005 1000004 1003 102 2 \n11 7 6 \nNoteIn the first test case, select $$$i=1$$$ in the first operation, insert $$$a_1 + 1 = 3$$$ in $$$S$$$, and delete $$$a_1$$$ from $$$a$$$. After the first operation, $$$a$$$ becomes $$$a=[1]$$$. In the second operation, we select $$$i=1$$$ again and insert $$$a_1 + 1 = 2$$$ in $$$S$$$. Thus $$$S=\\{2, 3\\}$$$, and $$$b = [3, 2]$$$.Note that if you select $$$i=2$$$ in the first operation, and $$$i=1$$$ in the second operation, $$$S=\\{3\\}$$$ as $$$3$$$ will be inserted twice, resulting in $$$b=[3]$$$.As $$$[3,2]$$$ is lexicographically larger than $$$[3]$$$, we should select $$$i=1$$$ in the first operation.In the second test case, in each operation, select the last element.
# """

# # Convert LaTeX to plain text
# plain_text = convert_latex_to_plain_text(latex_text)

# # Print the plain text
# print(plain_text)
