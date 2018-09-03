from flask import Flask, render_template, json, request, jsonify
from flask_restful import Resource, Api
from flask_bootstrap import Bootstrap
import MySQLdb



app=Flask(__name__)
Bootstrap(app) 
# MySQL configurations
conn = MySQLdb.connect(host = "localhost",user = "root" ,passwd = "admin123", db="anm")
x = conn.cursor()

@app.route('/')
def index ():
	return render_template('index.html')

@app.route('/newswitch',methods=['POST','GET'])
def newswitch ():
    
        switchs = request.form['switch']
        ips = request.form['ip']
        

        # validate the received values
        if switchs and ips :
            
            # All Good, let's call MySQL
            
            
            
            x.execute("""INSERT INTO switch_cred(name,ip) VALUES (%s,%s)""",(switchs,ips))
            conn.commit()
            
            
            
    
            
            conn.close()
        return 'ok' 

	
@app.route('/macs')
def get():
    
        

        
        x.execute("select * from macs")
        conn.commit()
        data = x.fetchall()

        #return jsonify(data)

        return render_template("macs.html", data=data)

    
  
@app.route('/spt')
def get1():




        x.execute("select * from stp")
        conn.commit()
        data = x.fetchall()

        #return jsonify(data)

        return render_template("stp.html", data=data)


@app.route('/spanning')
def get2():




        x.execute("select * from spanningtree")
        conn.commit()
        data = x.fetchall()

        #return jsonify(data)

        return render_template("spanning.html", data=data)
@app.route('/spt1',methods=['GET'])
def gt():
  x.execute("select * from stp ")
  conn.commit()
  r=[dict((x.description[i][0],value)for i,value in enumerate(row))for row in x.fetchall()]
  return jsonify({'myCollection':r})
@app.route('/spanning1',methods=['GET'])
def gta():
  x.execute("select * from spanningtree ")
  conn.commit()
  r=[dict((x.description[i][0],value)for i,value in enumerate(row))for row in x.fetchall()]
  return jsonify({'myCollection':r})	
if __name__ == '__main__':
	app.run(host='0.0.0.0',port=8000,debug=True)



            
    
            
        
