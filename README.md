# BoardGameForum

This is the final project for course EEN060 Applied Object-Oriented Programming in Chalmers.

# Project description:

This project is designed for board games sharing and discussing. There are three services provided by this forum:
1. Board games sharing. The user can post their favorite board games and other users can add comments and discussions.
2. Second-hand board games selling. Users can sell their second-hand board games through this forum.

# The service is accessible at http://ec2-18-224-246-171.us-east-2.compute.amazonaws.com/

# How to use it locally:
Once you have Anaconda installed, in your terminal, run:

conda create --yes --name boardgameforum -c conda-forge python=3.7 flask flask-sqlalchemy flask-bcrypt flask-login flask-wtf flask-markdown Pillow

Then, you should activate the environment:

conda activate boardgameforum

Then, you can run the project:

python main.py

There is one user included in the database in file forum.db with username default@test.com and password testing.

