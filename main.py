from flask import Flask, jsonify , render_template
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
import os
import psycopg2
import pandas as pd

from apiExtraction import eventCollection as ec

app = Flask(__name__)

engine = sqlalchemy.create_engine("postgresql://postgres:NIk2wyo95CVVO6KIMCf4@containers-us-west-109.railway.app:6313/railway")
df = pd.read_sql("shotevents", con=engine)


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

@app.route('/')
def first_player():
    return str(df.columns)

@app.route('/<player_name>')
def get_player(player_name):
    filtered_df = df[df['shooter'].str.contains(player_name,case=False,na=False)]
    return jsonify(filtered_df.to_dict(orient='records'))
    

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
