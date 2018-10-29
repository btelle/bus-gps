#! /usr/bin/python3

import os
import pymysql
import pprint
from flask import Flask, render_template, jsonify
from DBUtils.PersistentDB import PersistentDB

def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	return app

app = create_app()

def connect_db():
	return PersistentDB(
		creator=pymysql,
		host=os.environ['RDS_HOST'],
		user=os.environ['RDS_USER'],
		password=os.environ['RDS_PASS'],
		database=os.environ['RDS_DB'],
		cursorclass=pymysql.cursors.DictCursor
	)

def get_db():
	if not hasattr(app, 'db'):
		app.db = connect_db()
	return app.db.connection()

@app.route('/')
def index():
	return render_template(
		'index.html',
		title="bus tracker",
		line_id="602a028f-48cb-4fdc-a3d6-e557c53fded9",
		start={
			"lat": 34.219,
			"long": -118.642
		}
	)

@app.route('/api/locations/<id>', methods=['GET'])
def api_get_locations(id):
	cursor = get_db().cursor()

	query = """
		SELECT
			bus.id as bus_id,
			line.title as line_title
		FROM bus INNER JOIN line ON bus.line_id=line.id LEFT JOIN location ON bus.id=location.bus_id
		WHERE location.id IS NOT NULL AND line.id='{}'
		GROUP BY 1,2;
	""".format(id)

	cursor.execute(query)

	ret = {"buses": []}
	for row in cursor.fetchall():
		tmp = {'location': {}}
		tmp['id'] = row['bus_id']
		tmp['line'] = row['line_title']
		
		query = """
			SELECT
				latitude,
				longitude,
				direction,
				published_at
			FROM location
			WHERE location.bus_id='{bus_id}'
			ORDER BY published_at DESC
			LIMIT 1;
		""".format(bus_id=row['bus_id'])
		
		cursor.execute(query)
		loc_row = cursor.fetchone();
		
		tmp['location']['latitude'] = loc_row['latitude']
		tmp['location']['longitude'] = loc_row['longitude']
		tmp['direction'] = loc_row['direction']
		tmp['published_at'] = loc_row['published_at'].isoformat() + 'Z'

		ret['buses'].append(tmp)

	return jsonify(ret)
