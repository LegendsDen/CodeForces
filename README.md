# Codeforces Helper

Codeforces Helper is a dynamic web application built using Flask that allows users to view past submissions by tag, track recent problems solved by friends on specific topics, and visualize performance and contests. The application uses LSTM for performance prediction, providing insights into future ratings.

# Features
1. User Submissions by Tag: Displays past submissions of any user filtered by specific tags.
2. Friends' Recent Problems: Shows recent problems solved by friends on specific topics.
3. Performance and Contest Visualization: Visualizes user performance and contests using graphs.
4. Future Rating Prediction: Predicts future ratings using LSTM models.

# Installation 
Clone the repo -->git clone https://github.com/LegendsDen/CodeForces.git 
To run the program
        python -m venv env
        .\env\Scripts\activate.ps1
        source env/bin/activate
        pip install -r requirements.txt
        python app.py


# Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

# Acknowledgements
-[Flask](https://flask.palletsprojects.com/en/3.0.x/)
-[CodeForces Api](https://codeforces.com/apiHelp)
-[LSTM](https://www.kaggle.com/code/kmkarakaya/keras-lstm-explained-in-details)








