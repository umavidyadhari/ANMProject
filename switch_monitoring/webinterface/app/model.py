from app import db


class credentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    devname = db.Column(db.String(10),unique=True)
    devip = db.Column(db.String(16),unique=True)
    devcommunity = db.Column(db.String(30))
    devversion = db.Column(db.String(10))
    devtype = db.Column(db.String(5))


class inventory(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    creation_date=db.Column(db.DateTime)
    devname= db.Column(db.String(10))
    mac=db.Column(db.String(50))
    port=db.Column(db.Integer)
    status=db.Column(db.Integer)
    modif_date=db.Column(db.DateTime)

class enterpriseoid(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    vendor=db.Column(db.String(200))
    macoid=db.Column(db.String(50))
    portoid=db.Column(db.String(50))
    statusoid=db.Column(db.String(50))


class router(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime)
    devname = db.Column(db.String(10))
    ip= db.Column(db.String(30),unique=True)
    ifname = db.Column(db.String(30))
    modif_date = db.Column(db.DateTime)




