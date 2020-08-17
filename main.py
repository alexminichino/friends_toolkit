import os
import time
import random
import csv
import datetime
import webbrowser
import math
import sys
import json
from flask import Flask, render_template, redirect, request, session,flash, send_file
from werkzeug.utils import secure_filename
from messages_tool import *

REPORT_FILE_NAME = 'contacted_users.csv'
UPLOAD_DIRECTORY = 'uploads'
FRIENDS_DUMP_FILE ="friends.dump"
app = Flask(__name__)
app.secret_key = "RANDOM_STRING".encode('utf8')
webbrowser.open('http://localhost:5000', new=1)
messages_tool= MessagesTool()

@app.before_request
def before_request():
    if request.endpoint != 'sign_in':        
        if not 'sessionCookie' in session :
            return logout()
        if not messages_tool.getSessionClient(session["sessionCookie"]):
            return logout()

@app.route("/")
def index():
    return redirect("/select_friends")

@app.route("/sign_in", methods=["GET","POST"])
def sign_in():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email != "" and password != "":
                messages_tool= MessagesTool(email,password)
                if messages_tool.authenticate():   
                    session['sessionCookie'] = messages_tool.client.getSession()
                    return redirect("/select_friends")
                else:
                    flash('Invalid Credentials')
                    return render_template("form.html")
    return render_template("form.html")

@app.route("/select_friends")
def select_friends():  
    limit= request.args.get('limit', default = 100, type = int)
    reset= request.args.get('reset', default = False, type = bool)
    page= request.args.get('page', default = 1, type = int)
    name_to_search= request.args.get('name_to_search', default = "", type = str)
    offset = (page - 1) * limit
    selected_users= request.args.getlist("selected_users")
    unselected_users = request.args.getlist("unselected_users")
    if 'selected_users' in session and not reset:
        selected_users = selected_users + list( set(session['selected_users']) - set(selected_users))
    if len(unselected_users)>0:
         selected_users = list(set(selected_users) - set(unselected_users))
    session['selected_users'] = selected_users 
    friends = get_serialized_friends_or_fetch_all()
    update_lists(request, friends)
    friends = [(user) for user in friends if name_to_search.lower() in user.name.lower()]
    number_friends = len(friends)
    friends = friends[offset:(limit + offset if limit is not None else None)]
    return render_template("friends.html", friends=  friends , contacted_friends=  get_friends_by_csv(REPORT_FILE_NAME), report_exitst = report_exitst(), number_friends= number_friends, selected_users=selected_users, number_pages=math.ceil(number_friends/limit), current_page = page, limit_friends_per_page=limit, name_to_search=name_to_search)
    
@app.route("/compose_message",methods=["POST","GET"])
def compose_message(): 
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
    old_images = os.listdir(os.path.join(UPLOAD_DIRECTORY))
    selected_users= request.form.getlist("selected_users")  
    if 'selected_users' in session :
         selected_users = selected_users + list( set(session['selected_users']) - set(selected_users))
    session['selected_users'] = selected_users  
    if len(selected_users) < 1:
        flash("Select at least 1 friend!")
        return redirect("/select_friends") 
    friends= get_serialized_friends_or_fetch_all()
    update_lists(request, friends)
    return render_template("compose_message.html", friends= [(user) for user in friends if user.uid in selected_users], old_images=old_images )

@app.route("/send_messages",methods=["POST"])
def send_messages():    
    min_time= request.form.get("min_time")
    max_time= request.form.get("max_time")
    message= request.form.get("message")
    messages_sent=0
    if (int(min_time) > int(max_time)):
        flash('Range not allowed!')
        return redirect("/select_friends")
    time_to_sleep = random.randrange(int(min_time),int(max_time))
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
    message_backup= message
    for user in get_serialized_friends_or_fetch_all():
        if user.uid in selected_users:
            message=message_backup
            message= message.replace("{{name}}",user.name)
            message= message.replace("{{first_name}}",user.first_name)
            if not messages_tool.send_message(user,message):
                flash("Problem with facebook API "+str(messages_sent)+' messages sent of '+str(len(selected_users)))
                return redirect("/select_friends")
            messages_sent+=1
            log_message(user,message, messages_sent, len(selected_users))
            if saved_images :
                for image in saved_images:
                    time.sleep(2)
                    messages_tool.send_image(user,image,"")
            if messages_sent < len(selected_users):
                time.sleep(time_to_sleep)
    flash(str(messages_sent)+' Messages sent')
    return redirect("/select_friends?reset=True")

@app.route("/logout")
def logout():
    if 'sessionCookie':
        session.pop("sessionCookie", None)
    remove_dump_if_exists()
    return redirect("/sign_in")

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

def log_message(user,message, messages_sent, total):
    put_friend_in_csv(REPORT_FILE_NAME, user,message)
    #LOG IN CONSOLE
    print("\n\n\n******\n******Sent "+ str(messages_sent)+ " of "+ str(total) + " to user "+ user.name+ " at "+ now.strftime("%X") +"******\n******\n\n\n", file=sys.stdout )

def get_friends_by_csv(filename):
    rows =[]
    if os.path.exists(filename):
        f = open(filename, 'r')        
        with f:
            reader = csv.DictReader(f)        
            for row in reader:
                rows.append(row['UID'])
    return rows

def put_friend_in_csv(filename,user,message):
    if os.path.exists():
        mode = 'a' 
    else:
        mode = 'w'
    f = open(filename, mode, encoding="utf-8")
    now = datetime.datetime.now() 
    with f:
        fnames = ['UID', 'NAME', "MESSAGE", "DATE", "TIME"]
        writer = csv.DictWriter(f, fieldnames=fnames)
        if mode=='w':                
            writer.writeheader()
        writer.writerow({'UID' : user.uid, 'NAME' : user.name.encode("utf-8"),  'MESSAGE': message.encode("utf-8"), 'DATE' : now.strftime("%x"), 'TIME' : now.strftime("%X") })

def update_lists(request, friends):
    excluded_users= request.args.getlist("excluded_users")
    pre_contacted_users = request.args.getlist("pre_contacted_users")    
    unselected_excluded_users = request.args.getlist("unselected_excluded_users")
    unselected_pre_contacted_users = request.args.getlist("unselected_pre_contacted_users")
    
    if len(pre_contacted_users) > 0 or len(excluded_users) > 0 or len(unselected_excluded_users) > 0 or len(unselected_pre_contacted_users)> 0:
        for i,friend in enumerate(friends):
            if friend.uid in excluded_users:
                friends[i].is_excluded = True
            elif friend.uid in unselected_excluded_users and friend.is_excluded :
                friends[i].is_excluded = False
            if friend.uid in pre_contacted_users:
                friends[i].is_precontacted = True
            elif friend.uid in unselected_pre_contacted_users and friend.is_precontacted :
                friends[i].is_precontacted = False
        save_friends_list_in_json(friends)

def report_exitst():
    return os.path.exists(REPORT_FILE_NAME)

def get_serialized_friends_or_fetch_all():
    if os.path.exists(FRIENDS_DUMP_FILE):
        return read_friends_from_dump_file()
    friends=[]
    for friend in messages_tool.fetch_users():
        if friend.is_friend:
            friends.append(
                SimplifiedUser(
                        uid=friend.uid,
                        name=friend.name,
                        first_name = friend.first_name,
                        gender = friend.gender,
                        photo = friend.photo,
                        url = friend.url
                    ))
    save_friends_list_in_json(friends)
    return friends

def save_friends_list_in_json(friends):
    json_values= json.dumps(friends, default=convert_to_dict) 
    write_friends_on_dump_file(json_values)

def read_friends_from_dump_file():
     f = open(FRIENDS_DUMP_FILE, "r")
     with f:
         return json.loads(f.read(), object_hook=dict_to_obj)

def write_friends_on_dump_file(json_values):
     f = open(FRIENDS_DUMP_FILE, "w")
     with f:
         f.write(json_values)

def remove_dump_if_exists():
    if os.path.exists(FRIENDS_DUMP_FILE):
        os.remove(FRIENDS_DUMP_FILE)

if __name__ == "__main__":
    app.run(debug=False)

