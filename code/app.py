from flask import Flask, request, jsonify, render_template
from cassandra.cluster import Cluster
from flask import  Response, redirect, session, abort,Blueprint
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user

import json
import requests



#cluster = Cluster(contact_points=['172.17.0.2'],port=9042)
#session = cluster.connect()

app = Blueprint('app', __name__)
#app = Flask(__name__)
cluster = Cluster(contact_points=['172.17.0.2'],port=9042)
session = cluster.connect()



@app.route('/home')
@login_required
def hello():
        return render_template('index.html')

@app.route('/best', methods=['GET'])
@login_required
def profile():
        rows = session.execute( """Select * From bestplayer.stats""")
        result=[]
        for r in rows:
                result.append({"year":r.year,"player_name":r.player_name})
        return jsonify(result)


@app.route('/best/external', methods=['GET'])
@login_required
def external():
        football ='https://www.scorebat.com/video-api/v1/'
        resp = requests.get(football)
        if resp.ok:
                return jsonify(resp.json())
        else:
                print(resp.reason)


@app.route('/best', methods=['POST'])
def create():
        session.execute( """INSERT INTO bestplayer.stats(year,player_name) VALUES( {},'{}')""".format(int(request.json['year']),request.json['player_name']))
        return jsonify({'message': 'created: /records/{}'.format(request.json['year'])}), 200
@app.route('/best', methods=['PUT'])
def update():
        session.execute( """UPDATE bestplayer.stats SET player_name= '{}' WHERE year={}""".format(request.json['player_name'],int(request.json['year'])))
        return jsonify({'message': 'updated: /records/{}'.format(request.json['year'])}), 200
@app.route('/best', methods=['DELETE'])
def delete():
        session.execute("""DELETE FROM bestplayer.stats WHERE year={}""".format(int(request.json['year'])))
        return jsonify({'message': 'deleted: /records/{}'.format(request.json['year'])}), 200


#if __name__ == '__main__':
#       app.run(host='0.0.0.0', port=80)


