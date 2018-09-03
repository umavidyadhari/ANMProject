from easysnmp import Session
import MySQLdb
import time
ip = '192.168.184.102'
session = Session(hostname=ip, community='public', version=2)
stpver = session.walk('1.3.6.1.2.1.17.2.1')
stppriority = session.walk('1.3.6.1.2.1.17.2.2')
topchangetime = session.walk('1.3.6.1.2.1.17.2.3')
topchangecount = session.walk('1.3.6.1.2.1.17.2.4')
droot = session.walk('1.3.6.1.2.1.17.2.5')
rcost = session.walk('1.3.6.1.2.1.17.2.6')
rport = session.walk('1.3.6.1.2.1.17.2.7')
stpage = session.walk('1.3.6.1.2.1.17.2.8')

sport = session.walk('1.3.6.1.2.1.17.2.15.1.1')
sportstate = session.walk('1.3.6.1.2.1.17.2.15.1.3')
enports = session.walk('1.3.6.1.2.1.17.2.15.1.4')
spathcost = session.walk('1.3.6.1.2.1.17.2.15.1.5')
pdroot = session.walk('1.3.6.1.2.1.17.2.15.1.6')
pdcost = session.walk('1.3.6.1.2.1.17.2.15.1.7')
portchangecount = session.walk('1.3.6.1.2.1.17.2.15.1.10')

conn = MySQLdb.connect(host= "localhost",user="root",passwd="admin123",db="anm")
x = conn.cursor()


bg = x.execute("""select * from stp where ip = %s""",[ip])
conn.commit()
while True:
 for a,b,c,d,e,f,g,h in zip(stpver,stppriority,topchangetime,topchangecount,droot,rcost,rport,stpage):
  a1 = a.value
  b1 = b.value
  c1 = c.value
  d1 = d.value
  e1 = ' '.join('{:02x}'.format(ord(x)) for x in e.value)
  f1 = f.value
  g1 = h.value
  h1 = time.time()

  conn = MySQLdb.connect(host= "localhost",user="root",passwd="admin123",db="anm")
  x = conn.cursor()
  bd1 = x.execute("select * from spanningtree where ip = %s ",[ip])
  conn.commit()
  v2 = x.fetchone()
 
  if bd1 == 0 :

   try:
    x.execute("""INSERT INTO spanningtree(ip,stpver,stppriority,topchangetime,changecount,droot,rcost,rport,time) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""",  
           (ip,a1,b1,c1,d1,e1,f1,g1,h1))
   
    conn.commit()
   except:
    conn.rollback()
    conn.close()
  if bd1 == 1 :
 
   if v2[2] != int(a1) or v2[3] != int(b1)  or v2[5] != int(d1) or v2[6] != e1 or v2[7] != int(f1) or v2[8] != int(g1):
    try:
        x.execute("UPDATE spanningtree SET stpver = %s,stppriority  = %s, topchangetime = %s, changecount=%s, droot=%s ,rcost = %s,rport = %s,updatetime = %s WHERE ip = %s ", 
        (a1,b1,c1,d1,e1,f1,g1,h1,ip))
        conn.commit()
    except:
        conn.rollback()
        conn.close()
  else:

   try:
        x.execute("UPDATE spanningtree SET time = %s WHERE ip = %s ", 
        (h1,ip))
        conn.commit()
   except:
        conn.rollback()
        conn.close() 
   
     
 for x1,x2,x3,x4,x5,x6,x7 in zip(sport,sportstate,enports,spathcost,pdroot,pdcost,portchangecount):
  y1 = x1.value
  y2 = x2.value
  y3 = x3.value
  y4 = x4.value
  y5 = ' '.join('{:02x}'.format(ord(x)) for x in x5.value)
  y6 = x6.value
  y7 = x7.value
  o = time.time()
  conn = MySQLdb.connect(host= "localhost",user="root",passwd="admin123",db="anm")
  x = conn.cursor()
  bd = x.execute("""select * from stp where ip = %s and sports = %s""",([ip],y1))
  conn.commit()
  v1 = x.fetchone()
  
  if bg == 0: 
   try:
    x.execute("""INSERT INTO stp(ip,sports,pstatus,enports,portpathcost,pdroot,pdcost,portchange) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",       
             (ip,y1,y2,y3,y4,y5,y6,y7))
    conn.commit()
   except:
    conn.rollback()
    conn.close()
  if bg != 0: 
  
   if  v1[3] != int(y2) or v1[4] != int(y3) or v1[5] != int(y4) or v1[6] != y5 or v1[7] != int(y6) or v1[8] != int(y7): 
    try:
        x.execute("UPDATE stp SET pstatus = %s,enports = %s, portpathcost = %s,pdroot = %s, pdcost=%s, portchange=%s ,probtime = %s WHERE sports = %s ", 
        (y2,y3,y4,y5,y6,y7,o,y1))
        conn.commit()
    except:
        conn.rollback()
        conn.close()
   else:
    try:
        x.execute("UPDATE stp SET time = %s WHERE sports = %s ", 
        (o,y1))
        conn.commit()
    except:
        conn.rollback()
        conn.close()
 time.sleep(30)
