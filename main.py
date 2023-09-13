from flask import Flask, jsonify , render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
import os
import psycopg2
import pandas as pd

from apiExtraction import eventCollection as ec

app = Flask(__name__)

engine = sqlalchemy.create_engine("postgresql://postgres:NIk2wyo95CVVO6KIMCf4@containers-us-west-109.railway.app:6313/railway")
# df = pd.read_sql("shotevents", con=engine)

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/update_table',methods=['GET'])
def update_table():
    try:
        existing = pd.read_sql("shotevents", con=engine)
    except:
        existing = pd.DataFrame()

    try:
        shot_df = ec.shotDataFrame(existing)
        shot_df.update_over_season(2022)
        shot_df.df.to_sql('shotevents', con=engine, if_exists='replace', index=False)
        return "Table updated successfully", 200
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/players/',methods=['GET', 'POST'])
def players():
    if request.method == 'POST':
        player_name = request.form['player_name']
        return redirect(url_for('player', player_name=player_name))
    return render_template('players.html')

@app.route('/players/<player_name>', methods=['GET'])
def player(player_name):
    query = """
    SELECT * FROM shotevents WHERE shooter ILIKE %s
    """
    params = ('%' + player_name + '%',)  # Convert the single parameter into a tuple

    filtered_df = pd.read_sql_query(query, engine, params=params)

    return filtered_df.to_html(classes=["table-bordered", "table-striped", "table-hover"])

    #return render_template('players.html')
    # filtered_df = df[df['shooter'].str.contains(player_name,case=False,na=False)]
@app.route('/teams/')
def teams():
    return render_template('teams.html')

@app.route('/teams/<team_name>')
def team(team_name):
    return render_template('team.html',team_name = team_name)
    

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
