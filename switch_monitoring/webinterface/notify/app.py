import pusher
import os

from flask import Flask, render_template, request
import MySQLdb
app = Flask(__name__)
# MySQL configurations
conn = MySQLdb.connect(host="localhost",user="root",passwd="admin123",db="anm")
x = conn.cursor()
p = pusher.Pusher(
  app_id='434914',
  key='12b541724b1f5b880fc1',
  secret='5894aee4deab260562e3',
  cluster='eu',
  ssl=True
)

@app.route("/")
def show_index():
    return render_template('index.html')

@app.route("/notification", methods=['POST'])
def trigger_notification():
        x.execute('''select * from macs''')
        conn.commit()
        data = x.fetchall()
        
        
	p.trigger('notifications','new_notification', {'message': data})
	return "Notification triggered!"

if __name__ == "__main__":
    app.run(host = '0.0.0.0',port = 8000,debug=True)

