#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.

######???? why virtualenv first???
$ virtualenv sqlalchemy-workspace
New python executable in sqlalchemy-workspace/bin/python
Installing distribute....................done.
Installing pip...............done
$ cd sqlalchemy-workspace
$ source bin/activate
######
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111a.eastus.cloudapp.azure.com/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@w4111a.eastus.cloudapp.azure.com/proj1part2"
#
DATABASEURI = "postgresql://yh2791:879@w4111vm.eastus.cloudapp.azure.com/w4111"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. 
#This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
# @app.route('/')
# def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  #print request.args


  #
  # example of a database query
  #
  # cursor = g.conn.execute("SELECT name FROM test")
  # names = []
  # for result in cursor:
  #   names.append(result['name'])  # can also be accessed using result[0]
  # cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  #context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  #return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/')
def home():
  global state
  state = 0
  #return render_template("home.html")
  context = dict(data = "Please Login First To Access Speed Dating Data")
  return render_template("index.html", **context)


@app.route('/login', methods=['POST'])
def login():
  r_name = str(request.form['username'])
  r_role = str(request.form['role'])
  r_id = int(request.form['id'])

  researcher_cursor = g.conn.execute("SELECT name FROM researchers")
  
  for each in researcher_cursor:
    if r_name in each['name']:

        if r_role == 'Analyst':
          analyst_cursor = g.conn.execute("SELECT name, ana_id FROM analysts")
          for each in analyst_cursor:
            a_name, a_id = each
            if r_name in a_name and r_id==a_id:
              state = 1
              analyst_cursor.close()
              researcher_cursor.close()
              return render_template("home.html")

          state = 0
          context = dict(data = "Invalid Login. Please Login Again")
          analyst_cursor.close()
          researcher_cursor.close()
          return render_template("index.html", **context)
          
        if r_role == 'Host':
          host_cursor = g.conn.execute("SELECT name, h_id FROM hosts")
          for each in host_cursor:
            h_name, h_id = each
            if r_name in h_name and r_id==h_id:
              state = 1
              host_cursor.close()
              researcher_cursor.close()
              return render_template("home.html")
    
          state = 0
          context = dict(data = "Invalid Login. Please Login Again")
          host_cursor.close()
          researcher_cursor.close()
          return render_template("index.html", **context)
     
           
  state = 0
  researcher_cursor.close()
  context = dict(data = "Invalid Username. Please Login Again")
  return render_template("index.html", **context)

@app.route('/home')
def homepage():
  return render_template("home.html")

@app.route('/aboutus')
def aboutus():
  cursor1 = g.conn.execute("""SELECT DISTINCT r.name, CASE WHEN r.name=h.name THEN 'host'
    WHEN r.name=a.name THEN 'analyst' END AS role
    FROM hosts h, researchers r, analysts a WHERE r.name=h.name OR r.name=a.name;""") 
  cursor2 = g.conn.execute("""SELECT a.name, a.type FROM analysts a""")
  cursor3 = g.conn.execute("""SELECT h.name, hd.s_id FROM hosts h, hold hd WHERE h.h_id=hd.h_id""")
  # researchers = {}
  # name = []
  # role = []
  # for cur in cursor:
  #   name.append(cur[0])
  #   role.append(cur[1])
  # researchers['name'] = name
  # researchers['role'] = role
  # context = dict(data=researchers)
  result = []
  anainfo = []
  hostinfo = []
  for each1 in cursor1:
    result.append([each1['name'],each1['role']])
  for each2 in cursor2:
    anainfo.append([each2['name'],each2['type']])
  for each3 in cursor3:
    hostinfo.append([each3['name'],each3['s_id']])
  for i in result:
    for j in anainfo:
      if i[0]==j[0]:
        i.append(j[1])
        anainfo.remove(j)
      else:
        for k in hostinfo:
          if i[0] == k[0]:
            i.append(k[1])
            hostinfo.remove(k)
  cursor1.close()
  cursor2.close()
  cursor3.close()
  context = dict(data=result)
  return render_template("aboutus.html", **context)


@app.route('/session')
def session():
  cursor = g.conn.execute("""SELECT COUNT(*) FROM sessions""")
  for i in cursor:
    data = i[0]
  # print '======'
  # print type(data)
  context = dict(data = "Please Input Session Id To Check The Session Info, Total Number of Session is %d" % data)
  cursor.close()
  return render_template('session.html', **context)


@app.route('/show', methods=['POST'])
def show():
  global session_id
  session_id = int(request.form['snum'])
  id_cursor = g.conn.execute("SELECT s_id FROM sessions")

  id_list = []
  for each in id_cursor:
    id_list.append(int(each['s_id']))
  if session_id not in id_list:
    context = dict(data = "Invalid Input. Please Input Again To Check The Session Info")
    return render_template('session.html', **context)

  hosts_cursor = g.conn.execute("SELECT DISTINCT h.h_id FROM hold h WHERE h.s_id = %s", session_id)
  date_cursor = g.conn.execute("SELECT DISTINCT h.date FROM hold h WHERE h.s_id = %s", session_id)
  scale_cursor = g.conn.execute("SELECT s.scale FROM sessions s WHERE s.s_id = %s", session_id)
  scale = scale_cursor.fetchone()[0]
  s_date = date_cursor.fetchone()[0]

  hosts = []
  for each in hosts_cursor:
    hid = each['h_id']
    name_cursor = g.conn.execute("SELECT h.name FROM hosts h WHERE h.h_id = %s", hid)
    hname = name_cursor.fetchone()[0]
    hosts.append(hname)
    name_cursor.close()
  
  s_info = []
  s_info = [session_id, hosts, s_date, scale]
  hosts_cursor.close()
  date_cursor.close()
  scale_cursor.close()
  context = dict(data=s_info)
  return render_template('show.html', **context)


@app.route('/participation')
def participation():
  #session_id = int(request.form['session_num'])
  participation_cursor = g.conn.execute("SELECT male_id, female_id, result FROM pair WHERE session_id = %s", session_id)
  pair = []
  for each in participation_cursor:
    pair.append([each['male_id'], each['female_id'], each['result']])
  participation_cursor.close()
  context = dict(data=["The information is below", pair])
  return render_template('participation.html', **context)


@app.route('/detail',methods=['GET', 'POST'])
def detail():
  m_gender = str(request.form['gender'])
  m_id = int(request.form['id'])


  if m_gender=='male':
    id_cursor = g.conn.execute("SELECT id FROM male")
    id_list = []
    for each in id_cursor:
      id_list.append(int(each['id']))
    if m_id not in id_list:
      participation_cursor = g.conn.execute("SELECT male_id, female_id, result FROM pair WHERE session_id = %s", session_id)
      pair = []
      for each in participation_cursor:
        pair.append([each['male_id'], each['female_id'], each['result']])
      participation_cursor.close()
      context = dict(data=["Invalid Input. Please Input Again To Check The Session Info", pair])
      return render_template('participation.html', **context)

    male_cursor = g.conn.execute("SELECT name, career, race, intelligence, c_id FROM male WHERE id=%s",m_id)
    info1 = []
    for each in male_cursor:
      info1.append([each['name'],each['career'],each['race'],each['intelligence'],each['c_id']])
    c_id = info1[0][4]
    ch_cursor = g.conn.execute("SELECT age, loyalty, appearance FROM character1 WHERE cid=%s",c_id)
    info2 = []
    for each in ch_cursor:
      info2.append([each['age'],each['loyalty'],each['appearance']])
    male_info = []
    male_info.extend(info1[0][:4])
    male_info.extend(info2[0])
    context = dict(data=male_info)
    male_cursor.close()
    ch_cursor.close()
    return render_template("male.html", **context)
  else:
    id_cursor = g.conn.execute("SELECT id FROM female")
    id_list = []
    for each in id_cursor:
      id_list.append(int(each['id']))
    if m_id not in id_list:
      participation_cursor = g.conn.execute("SELECT male_id, female_id, result FROM pair WHERE session_id = %s", session_id)
      pair = []
      for each in participation_cursor:
        pair.append([each['male_id'], each['female_id'], each['result']])
      participation_cursor.close()

      context = dict(data=["Invalid Input. Please Input Again To Check The Session Info", pair])
      return redirect('participation.html', **context)

    female_cursor = g.conn.execute("SELECT name, age, loyalty, appearance, c_id FROM female WHERE id=%s",m_id)
    info1 = []
    for each in female_cursor:
      info1.append([each['name'],each['age'],each['loyalty'],each['appearance'],each['c_id']])
    c_id = info1[0][4]
    ch_cursor = g.conn.execute("SELECT career, race, intelligence FROM character2 WHERE cid=%s",c_id)
    info2 = []
    for each in ch_cursor:
      info2.append([each['career'],each['race'],each['intelligence']])
    female_info = []
    female_info.extend(info1[0][:4])
    female_info.extend(info2[0])
    context = dict(data=female_info)
    female_cursor.close()
    ch_cursor.close()
    return render_template("female.html", **context)
  

@app.route('/result')
def result():
  results = []
  result_cursor = g.conn.execute("SELECT * FROM conclusion")
  for each in result_cursor:
    results.append(each['type']+': '+each['description'])
  result_cursor.close()
  context = dict(data=results)
  return render_template("result.html", **context)


# Example of adding new data to the database
"""@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  return redirect('/')"""




if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
