from flask import Flask, render_template_string, request,render_template,redirect,session
from codeforces_func import (get_contests, get_contest_problems,
                            get_user_submissions, build_table_data,
                            generate_html_table)

from tags_search import (filter_submissions_by_tag)

                            

app = Flask(__name__)

@app.route("/hi",methods=['POST','GET'])
def display_html_table():
    if request.method=='POST':
        codeforces_id=request.form['content']# Replace with your Codeforces handle
        given_tag = request.form['option']
        try:
            submissions = get_user_submissions(codeforces_id)
            filtered_problems = filter_submissions_by_tag(submissions, given_tag)
            return  (filtered_problems)
        except:
            return'There was some Error'
    else:
        print(2)
        return render_template("first_page.html")



@app.route('/gg',methods=['POST','GET'])
def user():
    if request.method=='POST':
        codeforces_id=request.form['content']
        con=int(request.form['some_number'])
        # return render_template('second_page.html')
        try:
            print(3)
            contests = get_contests(con)
            # print(contests)
            submissions = get_user_submissions(codeforces_id)
            table_data = build_table_data(contests, submissions)
            html_table = generate_html_table(table_data)
            return render_template_string(html_table)
        except:
            return'There was some Error'
    else:
        print(4)
        return render_template("first_page.html")
       


    




if __name__ == "__main__":
    app.run(debug=True)