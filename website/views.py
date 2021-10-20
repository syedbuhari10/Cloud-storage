from warnings import catch_warnings
from flask import Blueprint, render_template, request
from flask.helpers import flash, send_from_directory, url_for
from flask.wrappers import Response
from flask_login import login_required, logout_user, current_user
from werkzeug.utils import redirect, secure_filename
from .models import Note, db
import json
import os
import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash("note is too short", category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash("Note added ", category='success')

    return render_template("uploadFile.html", user=current_user)

@views.route('/delete-note', methods=['POST', 'GET'])
def delete_note():
    noteId = request.args.get('noteId')
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return redirect(url_for('views.home'))

def check(s3, bucket, key):
    try:
        s3.head_object(Bucket=bucket, Key=key)
    except ClientError as e:
        return False
    return True

@views.route('/upload-file', methods=['POST', 'GET'])
def upload_file():
    s3 = boto3.client('s3',
                    aws_access_key_id=os.environ.get('AWSACESSKEYID'),
                    aws_secret_access_key= os.environ.get('AWSSECRETKEY'),
                    region_name="us-east-1")
    files = s3.list_objects(Bucket="file21102021", Prefix= str(current_user.id) + '/')
    filenames= []
    if 'Contents' in files:
        for file in files['Contents']:
            filenames.append(file['Key'].replace(str(current_user.id) + '/', ''))
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(filename)
            s3.upload_file(
                Bucket = 'file21102021',
                Filename = filename,
                Key = str(current_user.id) + '/' + filename
            )
            flag = check(s3, 'file21102021', str(current_user.id) + '/' + filename)
            os.remove(filename)
            if flag:
                flash("File uploaded Successfully!!", category='success')
            else:
                flash("Upload failed", category='error')
    return render_template('uploadFile.html', user=current_user, files=filenames)

@views.route('/delete-file', methods=['POST', 'GET'])
def delete_file():
    userid = request.args.get('id')
    filename = request.args.get('filename')
    s3 = boto3.client('s3',
                    aws_access_key_id=os.environ.get('AWSACESSKEYID'),
                    aws_secret_access_key= os.environ.get('AWSSECRETKEY'),
                    region_name="us-east-1")
    response = check(s3, 'file21102021', str(current_user.id) + '/' + filename)
    s3.delete_object(Bucket= 'file21102021',
                    Key= str(userid) + '/' + filename)
    if response == True:
        flash('File Deleted successfully', category='success')
    else:
        flash("File couldn't be deleted", category='error')
    return redirect(url_for('views.upload_file'))

@views.route('/download-file', methods=['POST', 'GET'])
def download_file():
    userid = request.args.get('id')
    filename = request.args.get('filename')
    s3 = boto3.client('s3',
                    aws_access_key_id=os.environ.get('AWSACESSKEYID'),
                    aws_secret_access_key= os.environ.get('AWSSECRETKEY'),
                    region_name="us-east-1")
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket':'file21102021',
        "Key": str(userid) + '/' + filename
        },
        ExpiresIn=300
    )
    return url

    