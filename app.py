import globals
import local_envoy_reader
import db_functions
import solar_surplus_to_tesla
import tesla_api
import asyncio
import json
import requests

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, redirect, url_for, request

globals.init()

envoy_data = db_functions.write_envoy_data_to_db()
solar_surplus_to_tesla.mainfunction(envoy_data)

sched = BackgroundScheduler(daemon=True)
sched.add_job(db_functions.write_envoy_data_to_db,'interval',seconds=60)
sched.add_job(solar_surplus_to_tesla.mainfunction,'interval',seconds=300)
sched.start()

app = Flask(__name__)

@app.route("/home")
def home():
    out = db_functions.read_envoy_data_from_db()
    return out # TODO print stats on webpage

@app.route('/')
def root():
    if globals.charge_mode == 'solar':
        solar_selected = ' selected'
        grid_selected = ''
    else:
        solar_selected = ''
        grid_selected = ' selected'
    return render_template('index.html', solar_selected=solar_selected, grid_selected=grid_selected)

@app.route('/selectchargemode', methods=['POST'])
def handle_data():
    globals.charge_mode = request.form['charge']
    print(f"charge mode is now {globals.charge_mode}")
    return redirect(url_for('root'))

if __name__ == "__main__":
    app.run(use_reloader=False)
