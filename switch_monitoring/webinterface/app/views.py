from flask import render_template,flash, redirect,url_for,request,jsonify,abort,send_from_directory,after_this_request
from app import app,db
from .model import *
from sqlalchemy import exc

@app.route('/')
@app.route('/index')
def index():
    return "<h1>My Inventory List</h1>"

# API for Insert the credentials into the DB
@app.route('/api/v1.0/credential',methods=['POST'])
def credential():
    if not request.json :
        abort(400)
    json_dict = request.get_json()
    #We make sure all the key values are present in the dictionary
    if not all(k in json_dict for k in ('ip','name','community','version','device')):
        abort(400)

    #we proceed to insert the data into the Data Base
    name=json_dict['name']
    ip=json_dict['ip']
    community=json_dict['community']
    version=json_dict['version']
    type=json_dict['device']
    #we proceed to insert the data into the DataBase
    try:
        #
        new_device=credentials(devname=name,devip=ip,devcommunity=community,devversion=version,devtype=type)
        db.session.add(new_device)
        db.session.commit()
        data=[{'name':name,'ip':ip,'community':community,'version':version,'type':type}]
        return jsonify(data),201
    except exc.IntegrityError:
        abort(409) #Conflict because the entry exist in the DB already


#API to Delete devices to probe
@app.route('/api/v1.0/delete_credential/<string:name>',methods=['DELETE','GET'])
def delete_credential(name):
    device=credentials.query.filter(credentials.devname==name).first()
    if not device:
        abort(404) # If the entry is not found in the DataBase
    data = {'name': device.devname, 'ip': device.devip, 'community':device.devcommunity, 'version': device.devversion, 'type': device.devtype}
    db.session.delete(device)
    db.session.commit()
    return jsonify(data),200

#API to List one device information
@app.route('/api/v1.0/device_name/<string:name>',methods=['GET'])
def device_name(name):
    device=credentials.query.filter(credentials.devname==name).first()
    if not device:
        abort(404) # If the entry is not found in the DataBase
    data = {'name': device.devname, 'ip': device.devip, 'community':device.devcommunity, 'version': device.devversion, 'type': device.devtype}
    return jsonify(data),200

#API to List all devices information
@app.route('/api/v1.0/devices_names',methods=['GET'])
def devices_names():
    devices=credentials.query.all()
    if not devices:
        abort(404)
    data=list()
    for device  in devices:
        data.append({'name': device.devname, 'ip': device.devip, 'community':device.devcommunity, 'version': device.devversion, 'type': device.devtype})
    return jsonify(data),200

#API to Update any entry:
# All parameters can be changed at one except on the name, or just a single
@app.route('/api/v1.0/update_device/<string:name>',methods=['PUT'])
def update_device(name):
    device = credentials.query.filter(credentials.devname == name).first()
    if not device:
        abort(404) # If the entry is not found in the DataBase
    if not request.json:
        abort(400)
    json_dict = request.get_json()

    # we collect the values to update
    if not 'ip' in json_dict:
        ip=device.devip
    else:
        ip=json_dict['ip']

    if not 'community' in json_dict:
        community=device.devcommunity
    else:
        community=json_dict['community']

    if not 'version' in json_dict:
        version=device.devversion
    else:
        version=json_dict['version']

    if not 'type' in json_dict:
        type=device.devversion
    else:
        type=json_dict['type']

    try:
        #
        device.devip=ip
        device.devcommunity=community
        device.devversion=version
        device.devtype=type
        db.session.commit()
        data={'name': device.devname, 'ip': ip, 'community':community, 'version': version, 'type':type}
        return jsonify(data),201
    except exc.IntegrityError:
        abort(409) #Conflict because the entry exist in the DB already


####################################################################################################################
#API to search for information base on device_name
@app.route('/api/v1.0/searchdevice/<string:name>',methods=['GET'])
def searchdevice(name):
    entries=inventory.query.filter(inventory.devname==name).all()
    if not entries:
        abort(404)
    data=list()
    for entry  in entries:
        data.append({'MAC': entry.mac, 'port': entry.port, 'status':entry.status})
    return jsonify(data),200

#API to search for information base on MAC
@app.route('/api/v1.0/searchmac/<string:mac>',methods=['GET'])
def searchmac(mac):
    entries=inventory.query.filter(inventory.mac==mac).all()
    if not entries:
        abort(404)
    data=list()
    for entry  in entries:
        data.append({'Device':entry.devname,'MAC': entry.mac, 'port': entry.port, 'status':entry.status})
    return jsonify(data),200
