import os
from requests import post, get
from flask import Flask, request, redirect, url_for, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging


UPLOAD_FOLDER = '/opt/images'
REST_URL = 'http://rest:3000/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)

gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.DEBUG)

def allowed_file(filename):
    return True
#    return '.' in filename and \
#           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_folder(headers):
    #print(headers)
    if 'businessid' in headers and len(headers['businessid']) > 0:
        url = REST_URL+'my_business?id=eq.'+headers['businessid']
        try:
          res = get(url, headers={'Authorization':headers['Authorization']}, timeout=3)
          j = res.json()
          return j[0]['id']
        except Exception:
          pass
    else:
        url = REST_URL+'rpc/me'
        try:
          res = post(url, headers={'Authorization':headers['Authorization']}, timeout=3)
          j = res.json()
          print(j)
          return j['id'][:9]
        except Exception:
          pass


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            app.logger.debug(f"No file part")
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('file')
        print(files)
        # if user does not select file, browser also
        # submit a empty part without filename
        for file in files:
          app.logger.debug(f"File: {file}")
          if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
          if file and allowed_file(file.filename):
            path = get_folder(request.headers)
            if path is None:
                flash('Not allowed')
                return redirect(request.url)
            filename = secure_filename(file.filename)
            if len(path) > 10:
                directory = os.path.join(app.config['UPLOAD_FOLDER'], path)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], path, filename))
            else:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return '''
    <!doctype html>
File service
    '''



if __name__ == "__main__":
    app.run(host='0.0.0.0')
