import time
import random
import datetime
from bus_api import get_lines, post_bus, post_location

config = {
    "line_id": "602a028f-48cb-4fdc-a3d6-e557c53fded9",
    "directions": ["eastbound", "westbound"],
    "routes": {
        "eastbound": [
            (34.2208266,-118.6280644),
            (34.2191804,-118.6444577),
            (34.2192244,-118.6427737),
            (34.2192374,-118.6373987),
            (34.2192814,-118.6323457),
            (34.2194144,-118.6263157)
        ],
        "westbound": [
            (34.2194144,-118.6263157),
            (34.2192814,-118.6323457),
            (34.2192374,-118.6373987),
            (34.2192244,-118.6427737),
            (34.2191804,-118.6444577),
            (34.2208266,-118.6280644)
        ]
    },
    "buses": 2,
    "delay_seconds": 60*15
}

buses = []

for i in range(0, config.get('buses')):
    bus = {}

    resp = post_bus(config.get('line_id'))
    bus['id'] = resp.get('uuid')
    bus['direction'] = random.choice(config.get('directions'))
    bus['location'] = config.get('routes').get(bus['direction'])[0]
    bus['next_update'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=random.randrange(30, 90))

    post_location(bus['id'], bus['location'][0], bus['location'][1], bus['direction'])
    print('Created bus {}'.format(bus['id']))

    buses.append(bus)

while(True):
    for bus in buses:
        if datetime.datetime.utcnow() >= bus['next_update']:
            if bus['location'] == config['routes'][bus['direction']][-1]:
                if bus['direction'] == config['directions'][0]:
                    bus['direction'] = config['directions'][1]
                else:
                    bus['direction'] = config['directions'][0]

                bus['location'] = config['routes'][bus['direction']][0]
                bus['next_update'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=config['delay_seconds'])
            else:
                i = 0
                for location in config['routes'][bus['direction']]:
                    i += 1
                    if bus['location'] == location:
                        bus['location'] = config['routes'][bus['direction']][i]
                        break

                bus['next_update'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=random.randrange(30, 90))
            
            post_location(bus['id'], bus['location'][0], bus['location'][1], bus['direction'])
            print('Updated location for {}'.format(bus['id']))
    
    time.sleep(5)

