#IMPORTS DEPENDENCIES
import numpy as np
import datetime as dt
from flask import Flask, url_for, jsonify, render_template, request, abort, make_response,redirect
import joblib
import requests
import webbrowser
import dash
import dash_core_components as dcc
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State, MATCH
from dash import html
from dash import dcc
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from flask import session
import sys

#Read data from CSV
df = pd.read_csv('data/visualisation.csv')
df2 = pd.read_csv('data/nonsmoking.csv')

app=Flask(__name__, static_folder='static')
app.secret_key = 'GP-SmART'

#Initialize the Dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dash_app = dash.Dash(
    __name__,
    server=app,
    external_stylesheets=external_stylesheets,
    url_base_pathname='/dash/'
)

# Define the layout of the Dash app
dash_app.layout = html.Div(
    [
        html.H4("Bio-signal Analysis to Detect Smoking Status "),
        html.P("Select a Chart:"),
        dcc.RadioItems(
            id="selection",
            options=["Systolic - Scatter", "Fasting Blood Sugar - Scatter"],
            value="Systolic - Scatter",
        ),
        dcc.Loading(dcc.Graph(id="graph"), type="cube"),
    ]
)

# Add controls to build the interaction
@dash_app.callback(
    Output("graph", "figure"), Input("selection", "value")
)
def display_animated_graph(selection):
    animations = {
        "Systolic - Scatter": px.scatter(
            df,
            x="weight(kg)",
            y="systolic",
            animation_frame="age",
            animation_group="height(cm)",
            hover_name="height(cm)",
            color="smoking",
            log_x=True,
            size_max=55,
        ),
        "Fasting Blood Sugar - Scatter": px.scatter(
            df,
            x="waist(cm)",
            y="fasting blood sugar",
            animation_frame="age",
            animation_group="height(cm)",
            hover_name="height(cm)",
            color="smoking",
            log_x=True,
            size_max=55,
        )
    }
    return animations[selection]

# Dash landing page
@app.route('/')
def dash_index():
    return redirect('/index')

# Dash visualization page
@app.route('/dash/visualization')
def dash_visualization():
    # Return the layout of the Dash app
    return dash_app.layout


#WEB ROUTES
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/casual_smoker')
def casual_smoker():
    return render_template('casual_smoker.html')

@app.route('/heavy_smoker')
def heavy_smoker():
    return render_template('heavy_smoker.html')

@app.route('/non_smoker')
def non_smoker():
    user_input = session.get('user_input', None)
    if user_input is None:
        abort(404)  # User's input not found in session variable

    x_feature = 'Hemoglobin Levels'

    y_feature = 'Systolic Blood Pressure'
    x = df2['hemoglobin']
    y = df2['systolic']

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='markers', name='Non-Smoker Data'))

    #non-smoker's data added to plot
    user_x = user_input[5]
    user_y = user_input[4]
    fig.add_trace(go.Scatter(x=[user_x], y=[user_y], mode='markers', name='User'))      

    fig.update_layout(title=f"Patient report for {user_input[1]} aged {user_input[0]}, {user_input[2]} cm tall, and {user_input[3]} kg",
                  xaxis_title=x_feature,
                  yaxis_title=y_feature)
    
    plot_div = fig.to_html(full_html=False)
    return render_template('non_smoker.html', plot_div=plot_div)

#POST ROUTES
@app.route('/result', methods=['POST'])

def result():
    model_dict = joblib.load('model3.joblib')
    model = model_dict['model']
    categories = model_dict['categories']

    features = ['age', 'gender', 'height(cm)', 'weight(kg)','systolic', 'hemoglobin', 'triglyceride','HDL','serum creatinine','Gtp']
    input_features = [float(request.form[feature]) for feature in features]

    y_prob = model.predict_proba([input_features])[0][1]
    y_cat = categories[np.digitize(y_prob, [0.0, 0.4, 0.65, 1.0]) - 1]

    session['user_input'] = input_features
    print("y_prob value:", y_prob)
    print("y_cat value:", y_cat)

    sys.stdout.flush()  # Flush the output to ensure it appears in the terminal immediately


    if y_prob <= 0.39:
        return redirect(url_for('non_smoker'))
    elif y_prob >= 0.7:
        return redirect(url_for('heavy_smoker'))
    else:
        return redirect(url_for('casual_smoker'))

if __name__ == '__main__':
    app.run(debug=True)