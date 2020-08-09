import os
import time
import random
import csv
import datetime
import webbrowser
from flask import Flask, render_template, redirect, request, session,flash, send_file
from werkzeug.utils import secure_filename
from messages_tool import *

REPORT_FILE_NAME = 'contacted_users.csv'
UPLOAD_DIRECTORY = 'uploads'
app = Flask(__name__)
app.secret_key = "RANDOM_STRING".encode('utf8')
webbrowser.open('http://localhost:5000', new=1)

@app.route("/")
def index():
    return redirect("/select_friends")

@app.route("/sign_in", methods=["GET","POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email != "" and password != "":
                messages_tool= MessagesTool(email,password)
                if messages_tool.authenticate():   
                    session['sessionCookie'] = messages_tool.client.getSession()
                    return redirect("/select_friends")
                else:
                    return render_template("form.html",feedback="Invalid Credentials")
    return render_template("form.html")

@app.route("/select_friends")
def select_friends(): 
    messages_tool= MessagesTool("","")
    if 'sessionCookie' in session:    
        if messages_tool.getSessionClient(session["sessionCookie"]):
            return render_template("friends.html", friends= messages_tool.fetch_users(), contacted_friends=  get_contacted_friends_by_csv(), report_exitst = report_exitst() )
    session.clear()
    return redirect("/sign_in")

@app.route("/compose_message",methods=["POST","GET"])
def compose_message(): 
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
    old_images = os.listdir(os.path.join(UPLOAD_DIRECTORY))
    selected_users= request.form.getlist("selected_users")
    messages_tool= MessagesTool("","")
    session['selected_users'] = selected_users
    if 'sessionCookie' in session:    
        if messages_tool.getSessionClient(session["sessionCookie"]):
            return render_template("compose_message.html", friends= [(user) for user in messages_tool.fetch_users() if user.uid in selected_users], old_images=old_images )
    session.clear()
    return redirect("/sign_in")

@app.route("/send_message",methods=["POST"])
def send_message():    
    min_time= request.form.get("min_time")
    max_time= request.form.get("max_time")
    message= request.form.get("message")
    messages_sent=0
    if (int(min_time) > int(max_time)):
        flash('Range not allowed!')
        return redirect("/select_friends")
    time_to_sleep = random.randrange(int(min_time),int(max_time))
    messages_tool= MessagesTool("","")
    if 'images' in request.files:
        saved_images= save_files(request.files.getlist("images"))
    if 'old_images' in request.form:
        old_images = get_path_by_old_image(request.form.getlist("old_images"))
        if saved_images:
            saved_images = saved_images + old_images
        else:
            saved_images = old_images
    if 'selected_users' in session:
        selected_users = session['selected_users']
    else:
        return redirect("/select_friends")
    if 'sessionCookie' in session:    
        if messages_tool.getSessionClient(session["sessionCookie"]):
            message_backup= message
            for user in messages_tool.fetch_users():
                if user.uid in selected_users:
                    message=message_backup
                    message= message.replace("{{name}}",user.name)
                    message= message.replace("{{first_name}}",user.first_name)
                    log_message(user,message) 
                    messages_tool.send_message_to_user(user,message)             
                    messages_sent+=1
                    if saved_images :
                        for image in saved_images:
                            time.sleep(2)
                            messages_tool.send_image_to_user(user,image,"")
                    
                    time.sleep(time_to_sleep)
    flash(str(messages_sent)+' Messages sent')
    return redirect("/select_friends")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/report")
def report():
    if os.path.exists(REPORT_FILE_NAME):
        return send_file(REPORT_FILE_NAME, mimetype='text/csv', as_attachment=True)
    return redirect("/")

@app.route('/uploads/<filename>')
def get_image(filename):   
    return send_file(os.path.join(UPLOAD_DIRECTORY, filename), mimetype='image/gif')

def save_files(files):
    saved=[]
    for file in files:
        if file:
            filename = secure_filename(file.filename)
            filename = os.path.join(UPLOAD_DIRECTORY, filename)
            file.save(filename)
            saved.append(filename)
    return saved

def get_path_by_old_image(old_images):
    paths=[]
    for old_image in old_images:
        paths.append(os.path.join(UPLOAD_DIRECTORY, old_image))
    return paths

def log_message(user,message):
    if os.path.exists(REPORT_FILE_NAME):
        mode = 'a' 
    else:
        mode = 'w'
    f = open(REPORT_FILE_NAME, mode)

    with f:
        fnames = ['UID', 'NAME', "MESSAGE", "DATE", "TIME"]
        writer = csv.DictWriter(f, fieldnames=fnames)
        if mode=='w':                
            writer.writeheader()
        now = datetime.datetime.now() 
        writer.writerow({'UID' : user.uid, 'NAME' : user.name,  'MESSAGE': message, 'DATE' : now.strftime("%x"), 'TIME' : now.strftime("%X") })

def get_contacted_friends_by_csv():
    rows =[]
    if os.path.exists(REPORT_FILE_NAME):
        f = open(REPORT_FILE_NAME, 'r')        
        with f:
            reader = csv.DictReader(f)        
            for row in reader:
                rows.append(row['UID'])
    return rows

def report_exitst():
    return os.path.exists(REPORT_FILE_NAME)

if __name__ == "__main__":
    app.run()

