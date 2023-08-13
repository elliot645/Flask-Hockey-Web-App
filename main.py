from flask import Flask, jsonify , render_template
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
import os
import psycopg2
import pandas as pd

app = Flask(__name__)

engine = sqlalchemy.create_engine("postgresql://postgres:NIk2wyo95CVVO6KIMCf4@containers-us-west-109.railway.app:6313/railway")
df = pd.read_sql("players", con=engine)

@app.route('/')
def first_player():
    return df.to_json()

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
