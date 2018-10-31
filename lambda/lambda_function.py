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


def get_lines(event, context):
    try:
        conn = pymysql.connect(rds_host, user=user, passwd=password, db=db_name, connect_timeout=5)
    except:
        raise
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        sys.exit()

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
    try:
        conn = pymysql.connect(rds_host, user=user, passwd=password, db=db_name, connect_timeout=5)
    except:
        raise
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        sys.exit()
    
    body_obj = json.loads(event['body'])
    body_obj['id'] = str(uuid.uuid4())

    query = """
        INSERT INTO line 
        (id, title, color, direction_1, direction_2) VALUES
        ('{id}', '{title}', '{color}', '{direction_1}', '{direction_2}');
    """.format(**body_obj)

    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute(query)
    
    conn.commit()
    conn.close()
    return {
        'statusCode': 200,
        'isBase64Encoded': False,
        'body': json.dumps({
            "message": "Success",
            "uuid": body_obj['id']
        })
    }

def post_bus(event, context):
    try:
        conn = pymysql.connect(rds_host, user=user, passwd=password, db=db_name, connect_timeout=5)
    except:
        raise
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        sys.exit()
    
    body_obj = {}
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
        'statusCode': 200,
        'isBase64Encoded': False,
        'body': json.dumps({
            "message": "Success",
            "uuid": body_obj['id']
        })
    }

def get_locations(event, context):
    try:
        conn = pymysql.connect(rds_host, user=user, passwd=password, db=db_name, connect_timeout=5)
    except:
        raise
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        sys.exit()

    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("""
            SELECT
                bus.id as bus_id,
                line.title as line_title
            FROM bus INNER JOIN line ON bus.line_id=line.id LEFT JOIN location ON bus.id=location.bus_id
            WHERE location.id IS NOT NULL
            GROUP BY 1,2;
        """)

        ret = []
        for row in cur.fetchall():
            tmp = {'gps': {'latitude': {}, 'longitude': {}}, 'bus': {}}
            tmp['bus']['id'] = row['bus_id']
            tmp['bus']['line'] = row['line_title']
            
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
            
            cur.execute(query)
            loc_row = cur.fetchone();
            
            tmp['gps']['latitude']['decimal'] = loc_row['latitude']
            tmp['gps']['latitude']['dms'] = get_dms(loc_row['latitude'], 'latitude')
            tmp['gps']['longitude']['decimal'] = loc_row['longitude']
            tmp['gps']['longitude']['dms'] = get_dms(loc_row['longitude'], 'longitude')
            tmp['direction'] = loc_row['direction']
            tmp['published_at'] = loc_row['published_at'].isoformat() + 'Z'

            ret.append(tmp)
    
    return ret

def post_location(event, context):
    try:
        conn = pymysql.connect(rds_host, user=user, passwd=password, db=db_name, connect_timeout=5)
    except:
        raise
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        sys.exit()
    
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
        'statusCode': 200,
        'isBase64Encoded': False,
        'body': json.dumps({
            "message": "Success",
            "uuid": body_obj['id']
        })
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
