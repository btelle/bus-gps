import os
import sys
import json
import uuid
import pymysql
import logging
import secrets
import hashlib

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    rds_host = os.environ['RDS_HOST']
    user = os.environ['RDS_USER']
    password = os.environ['RDS_PASS']
    db_name = os.environ['RDS_DB']
except KeyError:
    logger.error('ERROR: Environment variables not set')
    sys.exit()

try:
    conn = pymysql.connect(rds_host, user=user, passwd=password, db=db_name, connect_timeout=5)
except:
    raise
    logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
    sys.exit()

def get_lines(event, context):
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("SELECT * FROM line;")
        
        ret = []
        for row in cur.fetchall():
            tmp = {}
            tmp['id'] = row['id']
            tmp['title'] = row['title']

            ret.append(tmp)
        
        return ret

def post_line(event, context):
    body_obj = json.loads(event['body'])
    body_obj['id'] = str(uuid.uuid4())

    query = """
        INSERT INTO line 
        (id, title, direction_1, direction_2) VALUES
        ('{id}', '{title}', '{direction_1}', '{direction_2}');
    """.format(**body_obj)

    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute(query)
    
    conn.commit()
    conn.close()
    return {
        "message": "Success",
        "uuid": body_obj['id']
    }

def post_bus(event, context):
    body_obj = json.loads(event['body'])
    body_obj['line_id'] = event['pathParameters']['id']
    body_obj['id'] = str(uuid.uuid4())
    body_obj['api_key'] = 'api_' + hashlib.sha1(secrets.token_bytes(32)).hexdigest()

    query = """
        INSERT INTO bus 
        (id, api_key, line_id, created_at) VALUES
        ('{id}', '{api_key}', '{line_id}', UTC_TIMESTAMP());
    """.format(**body_obj)

    with conn.cursor() as cur:
        cur.execute(query)

    conn.commit()
    conn.close()
    return {
        "message": "Success",
        "uuid": body_obj['id']
    }

def get_locations(event, context):
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("""
        SELECT bus_id, line_title, latitude, longitude, direction, published_at
        FROM (
            SELECT
                bus.id as bus_id,
                line.title as line_title,
                location.latitude as latitude,
                location.longitude as longitude,
                location.direction as direction,
                location.published_at as published_at,
                ( 
                    CASE bus.id 
                    WHEN @curType 
                    THEN @curRow := @curRow + 1 
                    ELSE @curRow := 0 AND @curType := bus.id END
                ) + 1 as rownum
            FROM bus INNER JOIN location ON bus.id=location.bus_id INNER JOIN line ON bus.line_id=line.id,
            (SELECT @curRow := 0, @curType := '') as t
            ORDER BY bus.id, location.published_at DESC
        ) as r
        WHERE rownum=1;
        """)

        ret = []
        for row in cur.fetchall():
            tmp = {'gps': {'latitude': {}, 'longitude': {}}, 'bus': {}}
            tmp['bus']['id'] = row['bus_id']
            tmp['bus']['line'] = row['line_title']
            tmp['gps']['latitude']['decimal'] = row['latitude']
            tmp['gps']['latitude']['dms'] = get_dms(row['latitude'], 'latitude')
            tmp['gps']['longitude']['decimal'] = row['longitude']
            tmp['gps']['longitude']['dms'] = get_dms(row['longitude'], 'longitude')
            tmp['direction'] = row['direction']
            tmp['published_at'] = row['published_at'].isoformat() + 'Z'

            ret.append(tmp)
    
    return ret

def post_location(event, context):
    body_obj = json.loads(event['body'])
    body_obj['bus_id'] = event['pathParameters']['id']
    body_obj['id'] = str(uuid.uuid4())
    
    query = """
        INSERT INTO location 
        (id, bus_id, latitude, longitude, direction, published_at) VALUES
        ('{id}', '{bus_id}', {latitude}, {longitude}, '{direction}', UTC_TIMESTAMP());
    """.format(**body_obj)

    with conn.cursor() as cur:
        cur.execute(query)
    
    conn.commit()
    conn.close()
    return {
        'message': 'Success',
        'uuid': body_obj['id']
    }

def get_dms(decimal, type):
    tmp = {}

    if type == 'latitude':
        if decimal < 0:
            tmp['direction'] = 'S'
        else:
            tmp['direction'] = 'N'
    else:
        if decimal < 0:
            tmp['direction'] = 'W'
        else:
            tmp['direction'] = 'E'
    
    tmp['degrees'] = abs(int(decimal))
    
    remainder = abs(decimal) - tmp['degrees']
    tmp['minutes'] = int(remainder * 60)

    remainder = (remainder * 60) - tmp['minutes']
    tmp['seconds'] = remainder * 60

    return tmp
