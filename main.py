from flask import Flask, jsonify #, render_template
#from flask_sqlalchemy import SQLAlchemy
import os
#import psycopg2

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:9pE5doMyZNcVDSrFtdep@containers-us-west-126.railway.app:7444/railway"
# db = SQLAlchemy(app)

# class Player(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     player_name = db.Column(db.String(100))

# @app.route('/')
# def first_player():
#     # Establish connection to the database using psycopg2
#     conn = psycopg2.connect("postgresql://postgres:9pE5doMyZNcVDSrFtdep@containers-us-west-126.railway.app:7444/railway")
#     cursor = conn.cursor()  # Create a new cursor

#     # Execute the SQL query
#     cursor.execute("SELECT player FROM testtable LIMIT 1;")

#     # Fetch the result
#     result = cursor.fetchone()

#     # Close the database connections
#     cursor.close()
#     conn.close()

#     if result:
#         return result[0]  # Return the name of the player
#     else:
#         return "No players found!"

@app.route('/')
def index():
    return "hello" #r"hello" #flask.PGPORT #os.getenv('Postgres.DATABASE_URL')

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
