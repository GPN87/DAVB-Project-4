#IMPORTS DEPENDENCIES
import numpy as np
import datetime as dt
from flask import Flask, url_for, jsonify, render_template, request, abort, make_response,redirect
import joblib
import datetime as dt
import requests
import webbrowser

app=Flask(__name__, static_folder='static')

#WEB ROUTES
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/smoker')
def smoker():
    return render_template('smoker.html')

@app.route('/non_smoker')
def non_smoker():
    return render_template('non_smoker.html')

#POST ROUTES
@app.route('/result', methods=['POST'])
def result():
    model = joblib.load('model2.joblib')

    features = ['age', 'gender', 'height(cm)', 'systolic', 'hemoglobin', 'triglyceride']
    input_features = [float(request.form[feature]) for feature in features]
    prediction = model.predict([input_features])
    is_smoker = bool(prediction)

    if is_smoker:
        return redirect(url_for('smoker'))
    else:
        return redirect(url_for('non_smoker'))

if __name__ == '__main__':
    app.run(debug=True)