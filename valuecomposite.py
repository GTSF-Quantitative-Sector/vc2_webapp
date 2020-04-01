from flask import Flask, render_template, send_file,url_for, make_response, request, flash, redirect
from calc_vc2 import *
from threading import Thread
import concurrent.futures
import pandas as pd 
import numpy as np
import requests
import json
import csv
import time
import itertools
import io
from werkzeug.utils import secure_filename
import urllib.request


app = Flask(__name__)
app.config['SECRET_KEY'] = 'fook me'
curr_excel_file = None

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

def slow_function(some_object):
    time.sleep(5)
    print(some_object)
    return render_template("home.html") 

@app.route("/about")
def about():
    #df = pd.DataFrame(np.random.randn(20,5))
    #x = df.style.highlight_max(color='lightgreen').highlight_min(color='#cd4f39').render()
    #return render_template("about.html", data=df)
    

    x = pd.DataFrame(np.random.randn(25, 8))
    x.to_excel(r'static/vc2_results.xlsx')
    cp_df = x.copy(deep=True)
    
    cp_df.drop(cp_df.columns.difference([7]), 1, inplace=True)
    cp_df.to_excel(r'static/vc2_scores.xlsx')
    x = x.head(5)
    return render_template("about.html",  data=x)

@app.route("/yeet")
def yeet():
    time.sleep(5)
    return ("<h1> AJAX is zaddy </h1>")

@app.route("/download")
def downloadFile():
    path = "static/vc2_results.xlsx"
    return send_file(path, as_attachment=True)

@app.route("/download_scores")
def downloadScore():
    path = "static/vc2_scores.xlsx"
    return send_file(path, as_attachment=True)

def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'red' if val < 0 else 'black'
    return 'color: %s' % color


@app.route("/test")
def test():
    return render_template("upload.html")

def transform(text_file_contents):
    return text_file_contents.replace("=", ",")

def calculate_table(stocks):
    req_attr = ["PS Ratio",
            "PB Ratio" ,
            "EBITDA to EV",
            "Dividend Yield",
            "PE Ratio",
            "Price to Cashflow",
            "Net Debt Change"
           ]
    
    df = build_dataset(stocks)
    replace_zero_mean(df)
    rank_ratio(df)
    result_df = rank_ticker(df)
    result_df.to_excel(r'static/vc2_results.xlsx')
    cp_df = result_df.copy(deep=True)
    cp_df.drop(cp_df.columns.difference(['VC2_Score']), 1, inplace=True)
    cp_df.to_excel(r'static/vc2_scores.xlsx')
    return result_df.head(5)

ALLOWED_EXTENSIONS = set(['csv', 'xlsx'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload():
    
    if 'data_file' not in request.files:
            flash('No file part')
            return render_template("upload.html")
    
    f = request.files['data_file']
    print(allowed_file(f.filename))

    if f.filename == '':
        flash('No selected file')
        return render_template("upload.html")
    
    if not allowed_file(f.filename):
        flash("Filetype not allowed")
        print("NOT ALLOWED")
        return render_template("file_error.html")

    if f and allowed_file(f.filename):
        stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        stocks = []
        for row in csv_input:
            stocks.append(row[0])

        print(stocks)
        result_df = calculate_table(stocks)
        result_df = result_df.head(5)
    
    return render_template("table.html",  data=result_df)



if __name__ == '__main__':
    app.run(debug=True)
