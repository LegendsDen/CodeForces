from flask import Flask, render_template_string, request,render_template,redirect,session,jsonify
from codeforces_func import (get_contests, get_contest_problems,
                            get_user_submissions, build_table_data,
                            generate_html_table)

from tags_search import (filter_submissions_by_tag,get_recent_submissions,get_recent_solved_problems_by_friends)
from flask_sqlalchemy import SQLAlchemy

                            

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///problems.db'
db = SQLAlchemy(app)

class StarredProblem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codeforces_id = db.Column(db.String(50), nullable=False)
    contestId = db.Column(db.String(10), nullable=False)
    index = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<StarredProblem {self.codeforces_id}-{self.contestId}{self.index}>'



@app.route("/hi",methods=['POST','GET'])
def display_html_table():
    if request.method=='POST':
        codeforces_id=request.form['content']# Replace with your Codeforces handle
        given_tag = request.form['option']
        # starred_problems = StarredProblem.query.filter_by(codeforces_id=codeforces_id).all()
        # starred_set = set((problem.contestId + problem.index) for problem in starred_problems)
        # first_element = next(iter(starred_set), None)
        try:    
            submissions = get_user_submissions(codeforces_id)
            filtered_problems = filter_submissions_by_tag(submissions, given_tag)
            #here  database if exits then problem.starred=true
            # for problem in filtered_problems:
            #     problem['starred'] = (str(problem['contestId']) + problem['index']) in starred_set
            print  (filtered_problems)
            return render_template('tag_problem.html', problems=filtered_problems,tag=given_tag,codeforces_id=codeforces_id)
        except:
            return'There was some Error'
    else:
        print(2)
        return render_template("first_page.html")

@app.route('/gg',methods=['POST','GET'])
def user():
    if request.method=='POST':
        codeforces_id=request.form['content']
        # return render_template('second_page.html')
        try:
            print(3)
            contests = get_contests(codeforces_id)
            print(contests)
            submissions = get_user_submissions(codeforces_id)
            table_data = build_table_data(contests, submissions)
            html_table = generate_html_table(table_data)
            return render_template_string(html_table)
        except:
            return'There was some Error'
    else:
        print(4)
        return render_template("first_page.html")
    

@app.route('/kk',methods=['POST','GET'])
def data():
    # codeforces_handle="Sushant81"
    if request.method=='POST':
        api_key = request.form['API_KEY']
        secret = request.form['API_SECRET']
        given_tag=request.form['option']
        codeforces_id=request.form['content']
        starred_problems = StarredProblem.query.filter_by(codeforces_id=codeforces_id).all()
        starred_set = set((problem.contestId + problem.index) for problem in starred_problems)
        try:
            recent=get_recent_solved_problems_by_friends(api_key,secret,False,given_tag,codeforces_id)  
            for problem in recent:
                problem['starred'] = ((str(problem['contestId'])) + problem['index']) in starred_set
            return render_template('problems_by_friend_and_tag.html', problems=recent, tag=given_tag ,codeforces_id=codeforces_id)
        except:
            return'There was some Error'
    else:
        return render_template("first_page.html") 

@app.route("/add_star", methods=['POST'])
def add_star():
    data = request.get_json()
    codeforces_id = data['codeforces_id']
    contestId = data['contestId']
    index = data['index']
    name = data['name']
    print(name)
    
    if not StarredProblem.query.filter_by(codeforces_id=codeforces_id,contestId=contestId, index=index).first():
        new_problem = StarredProblem(codeforces_id=codeforces_id,contestId=contestId, index=index, name=name)
        db.session.add(new_problem)
        db.session.commit()
    return jsonify({'status': 'success'}) 

@app.route("/remove_star", methods=['POST'])
def remove_star():
    data = request.get_json()
    codeforces_id = data['codeforces_id']
    contestId = data['contestId']
    index = data['index']

    
    problem = StarredProblem.query.filter_by(codeforces_id=codeforces_id,contestId=contestId, index=index).first()
    if problem:
        db.session.delete(problem)
        db.session.commit()
    return jsonify({'status': 'success'})
    

# @app.route('/get_editorials', methods=['GET'])
# def get_editorials():
#     contest_id = request.args.get('contest_id')
    
#     if not contest_id:
#         return jsonify({'error': 'Contest ID is required'}), 400

#     problem_links = get_problem_links(contest_id)
    
#     if not problem_links:
#         return jsonify({'error': 'Unable to fetch problem links'}), 404

#     editorials = {}
#     for problem_url in problem_links:
#         problem_id = problem_url.split('/')[-1]
#         editorial = scrape_editorial(problem_url)
#         if editorial:
#             editorials[problem_id] = editorial
#         else:
#             editorials[problem_id] = "Editorial not found or unable to scrape"
    
#     return jsonify(editorials), 200

       


    




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)