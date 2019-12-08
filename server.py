import os
from math import copysign, log10

from app import app
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename

# import the necessary packages
from colordescriptor import ColorDescriptor
from searcher import Searcher
import argparse
import cv2

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # initialize the image descriptor
            cd = ColorDescriptor((8, 12, 3))
            # load the query image and describe it
            photos_result = []
            query = cv2.imread(app.config['UPLOAD_FOLDER']+"/"+filename)
            features = cd.describe(query)

            query_photo = {"score": 100, "photo": "queries/"+filename}
            photos_result.append(query_photo)
            # perform the search
            searcher = Searcher("./index.csv")
            results = searcher.search(features)

            # loop over the results
            for (score, resultID) in results:
                score = log10(abs(score))
                # load the result image and display it
                result = {"score": score, "photo": "dataset/"+resultID}
                photos_result.append(result)
            return render_template('result.html', results=photos_result)

        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect(request.url)

if __name__ == "__main__":
    app.run()