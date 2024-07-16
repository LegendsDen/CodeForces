# Codeforces Helper

Codeforces Helper is a dynamic web application built using Flask that allows users to view past submissions by tag, track recent problems solved by friends on specific topics, and visualize performance and contests. The application uses LSTM for performance prediction, providing insights into future ratings.

# Features
1. User Submissions by Tag: Displays past submissions of any user filtered by specific tags.
2. Friends' Recent Problems: Shows recent problems solved by friends on specific topics.
3. Performance and Contest Visualization: Visualizes user performance and contests using graphs.
4. Future Rating Prediction: Predicts future ratings using LSTM models.

# Installation 
        Clone : https://github.com/LegendsDen/CodeForces.git 
        enivironmnet : python -m venv env
                     : .\env\Scripts\activate.ps1
                     : source env/bin/activate
        run : pip install -r requirements.txt
                : python app.py


# Some images from the website 
### Contest Performance 
<img src="./img/Screenshot 2024-07-17 000723.png" alt="Contest Performance" height ="400" width="700">


### Future Rating
<img src="./img/Screenshot 2024-07-17 000739.png" alt="Future Rating" height ="400" width="700">


### User Probems sort by Tags
<img src="./img/Screenshot 2024-07-17 000834.png" alt="User Problem" height ="400" width="700">

### Friends recent problems sort by tags
<img src="./img/Screenshot 2024-07-17 001025.png" alt="Friends Problem" height ="400" width="700">


# Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

# Acknowledgements
-[Flask](https://flask.palletsprojects.com/en/3.0.x/)
-[CodeForces Api](https://codeforces.com/apiHelp)
-[LSTM](https://www.kaggle.com/code/kmkarakaya/keras-lstm-explained-in-details)








