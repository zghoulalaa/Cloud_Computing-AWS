from flask import Flask, url_for, request, redirect, jsonify, json
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from cassandra.cluster import Cluster
from flask import Blueprint
from passlib.apps import custom_app_context as pwd_context
from app import app


auth_api = Flask(__name__)
# user blueprint functin to call another file
auth_api.register_blueprint(app)
auth_api.secret_key = 'MINI_PROJECT_SECRET_KEY'
login_manager = LoginManager(auth_api)

cluster = Cluster(contact_points=['172.17.0.2'],port=9042)
session = cluster.connect()

template_page = """   <form  style='position: absolute;top: 50%;left: 50%; -moz-transform: translateX(-50%) translateY(-50%);-webkit-transform: translateX(-50%) translateY(-50%);
                      -transform: translateX(-50%) translateY(-50%);' action={} method='POST'>
                      <input style='text-align: center' type='text' name='username' id='username' placeholder='username'/>
                      <input style='text-align: center' type='password' name='password' id='password' placeholder='password'/>
                      <input style='text-align: center' type='submit' name='submit'/> <br> <br> <br>
		      </form> <body style="background-color: #000000;color: #FFFFFF;"></body>"""
             

#if want to add more judgement, modify from here
class User(UserMixin):
    pass


# When user sign up, this function will be called
class Create:
    # save username and hashed password into database
    def new_user(self, name, password):
        password = self.hash_password(password)
        insert_cql = """INSERT INTO bestplayer.users (username, password_hash) VALUES
                    ('{}','{}');""".format(name,password)
        session.execute(insert_cql)

    # trigger this function when a new user registers or a user changes the password
    # convert original password to  a hashed one and store it
    def hash_password(self, password):
        password_hash = pwd_context.encrypt(password)
        return password_hash

# flask_login save current user id
@login_manager.user_loader
def user_loader(email):
    user = User()
    user.id = email
    return user


#login 
@auth_api.route('/login', methods=['GET', 'POST'])
@auth_api.route('/')
def login():
    if current_user.is_active:
        return ("""<body style="background-color: #000000;color: #FFFFFF;"></body><h2 style="font-size: 45px;position: absolute;top: 50%;left: 50%; -moz-transform: translateX(-50%) translateY(-50%);-webkit-transform: translateX(-50%) translateY(-50%);-transform: translateX(-50%);translateY(-50%);">Already Login</h2><br><br><br><footer style="text-align: center;" ><a style="font-size: 35px;text-decoration: none;font-weight: bold;color: #F15B31;"  href="home">Home</a>"""), 201

    #username and password page
    if request.method == 'GET':
        log_in_page = """<br> <br> <br> <br> <h2 style="text-transform: uppercase;text-align: center;font-size: 45px;letter-spacing: 1px;">Login</h2> """ + template_page.format('login') + \
                  """<footer style="text-align: center;" > <h2></h2> <a style="font-size: 35px;text-decoration: none;font-weight: bold;color: #F15B31;" href='http://ec2-54-88-212-181.compute-1.amazonaws.com/signup'>Sign-up</a> </footer>"""
        return log_in_page


    username = request.form['username']
    password = request.form['password']
    rows = session.execute("SELECT password_hash FROM bestplayer.users where username = %s LIMIT 1", ([username]))
    if not rows: #username not exists
        return ("""<h1 style="text-align: center;position: absolute;top: 50%;left: 50%; -moz-transform: translateX(-50%) translateY(-50%);-webkit-transform: translateX(-50%) translateY(-50%);-transform: translateX(-50%);translateY(-50%);">username: {} is not exist</h1><body style="background-color: #000000;color: #FFFFFF;"></body>""".format(username)), 404
    elif pwd_context.verify(password, rows[0].password_hash)==False:
        #wrong password
        return ("""<body style="background-color: #000000;color: #FFFFFF;"></body><h2 style="font-size: 45px; position: absolute;top: 50%;left: 50%; -moz-transform: translateX(-50%) translateY(-50%);-webkit-transform: translateX(-50%) translateY(-50%);-transform: translateX(-50%) translateY(-50%);">Wrong password. Please Log in again</h2>"""), 404
    else:
        user = User()
        user.id = username 
        login_user(user) 
        return ("""<body style="background-color: #000000;color: #FFFFFF;"></body><h2 style="position: absolute;top: 50%;left: 50%; -moz-transform: translateX(-50%) translateY(-50%);-webkit-transform: translateX(-50%) translateY(-50%);-transform: translateX(-50%) translateY(-50%);font-size: 45px;" >Hello, {}.You have successfully logged in.</h2><br><br><br><footer style="text-align: center;" > <a style="font-size: 35px;text-decoration: none;font-weight: bold;color: #F15B31;"  href="home">Home</a></footer>""".format(username)), 201
    return ('Bad login'),404


#logout 
@auth_api.route('/logout')
def logout():
    logout_user()
    return ("<body style='background-color: #000000;color: #FFFFFF;'></body><h1 style='position: absolute;top: 50%;left: 50%; -moz-transform: translateX(-50%) translateY(-50%);-webkit-transform: translateX(-50%) translateY(-50%);-transform: translateX(-50%) translateY(-50%); font-size: 45px;'>Logged out</h1>")


# Add new user name and password to Cassandra Database
@auth_api.route('/signup', methods=['GET', 'POST'])
def new_user():
    #Sign-up page front end
    sign_up_page ="<br> <br> <br> <br> <h2 style='text-transform: uppercase;text-align: center;font-size: 45px;letter-spacing: 1px;'>Sign-up</h2> " + template_page.format('signup') + "<footer style='text-align: center;' > <h2></h2> <a style='font-size: 35px;text-decoration: none;font-weight: bold;color: #F15B31;'<a href='http://ec2-54-88-212-181.compute-1.amazonaws.com/login'>Log in</a> </footer>"
    if request.method == 'GET':
        return sign_up_page
    username = request.form['username']
    password = request.form['password']
    # username already exists
    rows = session.execute("SELECT * FROM bestplayer.users where username = %s ", ([username]))
    if rows:
         return ("<h1 style='text-align: center;position: absolute;top: 50%;left: 50%; -moz-transform: translateX(-50%) translateY(-50%);-webkit-transform: translateX(-50%) translateY(-50%);-transform: translateX(-50%);translateY(-50%);'>username: {} already exists</h1><body style='background-color: #000000;color: #FFFFFF;'></body> ".format(username)), 404
    #save username and hashed password into database
    Create().new_user(username, password)
    user = User()
    user.id = username
    login_user(user)
    return ("""<h2 style='font-size: 45px; text-align: center;position: absolute;top: 50%;left: 50%; -moz-transform: translateX(-50%) translateY(-50%);-webkit-transform: translateX(-50%) translateY(-50%);-transform: translateX(-50%);translateY(-50%);'>Hello, {}</h2><br><br><br><footer style='text-align: center;'><h2></h2><a style='font-size: 35px;text-decoration: none;font-weight: bold;color: #F15B31;' href='http://ec2-54-88-212-181.compute-1.amazonaws.com/home'>Home </a> </footer><body style='background-color: #000000;color: #FFFFFF;'> </body> """.format(user.id)), 201

if __name__ == '__main__':
    auth_api.run(host='0.0.0.0',port=80)
