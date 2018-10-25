import os
import sys
import json
import logging
import requests


class ApiException(Exception):
    """ API Exception class. """
    pass


logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    api_url = os.environ['BUS_API_URL']
    if api_url[-1] == '/':
        api_url = api_url[0:-1]
except KeyError:
    logger.error('Missing required environment variables')
    sys.exit()


def get_lines():
    """ Get a list of bus lines. """

    resp = requests.get(api_url + '/lines')

    if resp.status_code == 200:
        return resp.json()
    else:
        logger.error(resp.text)
        raise ApiException(resp.text)


def get_locations():
    """ Get a list of bus lines. """

    resp = requests.get(api_url + '/locations')

    if resp.status_code == 200:
        return resp.json()
    else:
        logger.error(resp.text)
        raise ApiException(resp.text)


def post_line(title, direction_1, direction_2):
    """ Create a bus line. """

    body = {
        'title': title,
        'direction_1': direction_1,
        'direction_2': direction_2
    }

    resp = requests.post(api_url + '/lines', json=body)

    if resp.status_code == 200:
        return resp.json()
    else:
        logger.error(resp.text)
        raise ApiException(resp.text)


def post_bus(line_id):
    """ Create a bus. """
    resp = requests.post(api_url + '/lines/' + line_id + '/bus')

    if resp.status_code == 200:
        return resp.json()
    else:
        logger.error(resp.text)
        raise ApiException(resp.text)


def post_location(bus_id, latitude, longitude, direction):
    """ Update the bus's location. """
    body = {
        'latitude': latitude,
        'longitude': longitude,
        'direction': direction
    }

    resp = requests.post(api_url + '/bus/' + bus_id + '/location', json=body)

    if resp.status_code == 200:
        return resp.json()
    else:
        logger.error(resp.text)
        raise ApiException(resp.text)
