from easysnmp import Session
import binascii
import time
import MySQLdb
from ctypes import *
from collections import Counter
#retrive the device ip from the database
conn1 = MySQLdb.connect(host= "localhost",user="root",passwd="admin123",db="anm")
x1 = conn.cursor()
bsa = x.execute("SELECT ip FROM devices")
conn.commit()
ip = x.fetchone()
conn.commit()
for ip1 in ip:

 session = Session(hostname=ip1, community='public', version=2)
 mac     = session.walk('.1.3.6.1.2.1.17.4.3.1.1')
 port    = session.walk('.1.3.6.1.2.1.17.4.3.1.2')
 status  = session.walk('.1.3.6.1.2.1.17.4.3.1.3')
 inoct  = session.walk('iso.3.6.1.2.1.2.2.1.10')
 outoct = session.walk('iso.3.6.1.2.1.2.2.1.16')
 index  = session.walk('iso.3.6.1.2.1.2.2.1.1')
 index1  = session.walk('1.3.6.1.2.1.2.2.1.1')
 duplex = session.walk('1.3.6.1.2.1.10.7.2.1.19')
 linkspeed = session.walk('1.3.6.1.2.1.2.2.1.5')
 vlanindex = session.walk('1.3.6.1.2.1.17.7.1.4.3.1.2')
 vlan = session.walk('1.3.6.1.2.1.17.7.1.4.3.1.1')
 a = []
 bd = []
 c = []
 d = []
 e = []
 f = []
 g = []
 aa = []
 bb= []
 cc = []
 dd = []

 a2 = []
 b2 = []
 c2 = []
 d2 = []
 d3 = []
 while True:
 #Auto detection of macs
  for macs,ports,statu in zip (mac,port,status):
    pmac=':'.join('{:02x}'.format(ord(x)) for x in macs.value)
    pmacoid=macs.oid
    pport=ports.value
    pportoid=ports.oid
    pstatus=statu.value
    pstatusoid=statu.oid
    ptime= time.time()
    
    a.append(pmac)
    bd.append(str(pmacoid))
    c.append(pport)
    d.append(pportoid)
    e.append(pstatus)
    f.append(pstatusoid)
    g.append(ptime)
    
  bridge=Counter(c)
  print bridge
  for bport, bcount in bridge.items():
    if bcount == 1:
      for amac,aoid,aport,astatus,atime in zip(a,bd,c,e,g):
         if aport == bport: 
           print aport
           conn = MySQLdb.connect(host= "localhost",user="root",passwd="admin123",db="anm")
           x = conn.cursor()
           b = x.execute("SELECT * FROM macs WHERE mac = %s",[amac])
           conn.commit()
           dbmac = x.fetchone()
           conn.commit()
           if b == 0:
            try:
             x.execute("""INSERT INTO macs(mac,port,status,time,oid,notify,ip) VALUES(%s,%s,%s,%s,%s,%s,%s)""",       
             (amac,aport,astatus,atime,aoid,0,ip))
             conn.commit()
            except:
             conn.rollback()
             conn.close()
           if b == 1 and dbmac[7] == aoid and dbmac[2]==int(aport) :
            try:
             x.execute("UPDATE macs SET probertime=%s WHERE mac = %s", (atime,amac))
             conn.commit()
            except:
             conn.rollback()
             conn.close()
           if b == 1 and dbmac[7] == aoid and dbmac[2]!=int(aport) :
            try:
             x.execute("UPDATE macs SET port=%s,updatetime=%s,probertime=%s WHERE mac = %s", (aport,atime,atime,amac))
             conn.commit()
            except:
             conn.rollback()
             conn.close()
#collision detection
           if b == 1 and dbmac[7] != aoid:
            try:
             x.execute("INSERT INTO collision(mac,port,time,oid,ip) VALUES(%s,%s,%s,%s,%s)",(amac,aport,atime,aoid,ip))
             conn.commit()
            except:
             conn.rollback()
             conn.close()
#to finde bridge ports
    if bcount > 1:
      print "bridge port is :", bport
      for amacs,aoids,aports,astatuss,atimes in zip(a,bd,c,e,g):
       if aports == bport:
        print amacs
 for a1,b1,c1 in zip(index,inoct,outoct):
  aa.append(a1.value)
  bb.append(int(b1.value))
  cc.append(int(c1.value))
  d1 = time.time()
  dd.append(d1)
#to find bitrates
 if len(a2) == len(a):
  for y,i1,i2,o1,o2,t1,t2 in zip(aa,bb,b2,cc,c2,dd,d3):
   df =  i1 - i2
   fd = t1 - t2
   in1 = df/fd 
   df1 =  o1 - o2
   fd1 = t1 - t2
   out1 = df1/fd1
   print y,"|",in1,"|",out1
#linkspeed
 for at,bt,ct in zip(index1,duplex,linkspeed):
  a1t = at.value
  b1t = bt.value
  c1t = ct.value
  print a1t, "|" ,b1t, "|" ,c1t
  cmd = "curl -i -XPOST 'http://localhost:8086/write?db=datalink&u=admin&p=admin' --data-binary 'speed,index=%s,Duplex=%s LinkSpeed=%s'"%(str(a1),str(b1),str(c1))
  os.system(cmd)  
#to track vlans in switch
 for a,b in zip(vlanindex,vlan):
  a1=''.join('{:02x}'.format(ord(x)) for x in a.value)
  a2 = b.value
  b2.append(a1)
  b3.append(a2)
  print a1,a2
  print b2
  print b3
 
 a2 = aa[:]
 b2 = bb[:]
 c2 = cc[:]
 d3 = dd[:]
 
 del aa[:]
 del bb[:]
 del cc[:]
 del dd[:]
    

 del a[:]
 del bd[:]
 del c[:]
 del d[:]
 del e[:]
 del f[:]
 del g[:]
 time.sleep(5)

