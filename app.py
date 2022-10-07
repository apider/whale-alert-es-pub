import json
import asyncio
import time
import logging
import os
from datetime import datetime
import httpx

# Parameters and setup

# set whale-alert-api-key (token)
# from key import TOKEN     # if from file
TOKEN = os.environ.get('TOKEN')

# set cursor file path
cursorpath = os.environ.get('CURSORPATH', '/data/')

# Set up logging
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.INFO)

# min individual transaction dollar value (free plan: 500k minimum)
min_value = os.environ.get('MIN_VALUE', 500000)
logging.info('Individual transaction minimal value: $%s', min_value)

# Elasticearch params
eshost = os.environ.get('ESHOST', 'http://elasticsearch:9200')
esindex = os.environ.get('ESINDEX', 'whalealert')
esurl = eshost + '/' + esindex + '/_doc/'
esheaders = {'Content-Type': 'application/json'}

# whale alert vars
URL = 'https://api.whale-alert.io'
TRANSACTIONURI = '/v1/transactions'
# diff = 3599


def getWhaleData(cursor):

    # timestamp = int(time.time()) - diff

    params = {'api_key': TOKEN, 'min_value': min_value, 'cursor': cursor}

    # Probably not best idea to make this call async
    # async with httpx.AsyncClient() as client:
    #     r = await client.get(url=URL + TRANSACTIONURI, params=params)
    #     return r.json()

    # sync call
    try:
        with httpx.Client() as sync_client:
            r = sync_client.get(url=URL + TRANSACTIONURI, params=params)
            return r.json()
    except httpx.ConnectTimeout as e:
        logging.error(e)
        return False
    except httpx.ReadTimeout as e:
        logging.error(e)
        return False
    except httpx.TimeoutException as e:
        logging.error(e)
        return False
    except httpx.HTTPError as e:
        logging.error(e)
        return False
    except Exception as e:
        logging.error(e)
        return False


# for initial tests
# def writeToFileJson(payload):
#     with open("api-example-output.json", "w") as f:
#         f.write(json.dumps(payload, indent=4))


def removeCrusorFile():
    try:
        logging.warning('Cursor to old, trying remove cursor file...')
        os.remove(cursorpath + "cursor.json")
        return True
    except Exception as e:
        return e


def writeToFileCursor(cursor):
    with open(cursorpath + "cursor.json", "w", encoding=None) as f:
        logging.info('Updating cursor file, cursor: %s', payload['cursor'])
        cursorj = {'cursor': cursor}
        f.write(json.dumps(cursorj, indent=4))


def fetchLatestCursor():
    try:
        with open(cursorpath + "cursor.json", "r") as f:
            cursor = json.load(f)['cursor']
    except FileNotFoundError:
        # if no file, return empty cursor
        logging.info('No cursor file found, returning empty cursor')
        return '0-0-0'
    else:
        logging.info('Found recent cursor in file, cursor: %s', cursor)
        return cursor


async def postEs(client, item):
    try:
        r = await client.post(esurl, data=json.dumps(item), headers=esheaders)
        return r
    except Exception as e:
        return e


async def elasticsearchSend(payload):
    logging.info('Posting whale alert data to Elasticsearch...')

    async with httpx.AsyncClient() as client:

        start_time = time.time()
        tasks = []
        for item in payload['transactions']:

            esdate = datetime.utcfromtimestamp(
                item['timestamp']).strftime('%Y-%m-%dT%H:%M:%S')

            item['@timestamp'] = esdate

            # Post to Elasticsearch async
            tasks.append(asyncio.ensure_future(postEs(client, item)))

        responses = await asyncio.gather(*tasks)

        logging.info("--- Async total time: %s sec ---",
                     (time.time() - start_time))
        logging.info('Posting to ES finished')

        return responses


# Try to fetch old cursor from file at startup
cursor = fetchLatestCursor()

while True:
    # payload = asyncio.run(getWhaleData(cursor))
    payload = getWhaleData(cursor)

    if payload and payload['result'] == 'success':
        # save new cursor
        cursor = payload['cursor']

        if payload['count'] > 0:
            logging.info('Got new transactions! Trans count: %s',
                         payload['count'])

            r = asyncio.run(elasticsearchSend(payload))

            # optional logging, of async post operations, remove if you want
            for call in r:
                logging.info(call)

            # update new cursor in file for restarts
            # only if new data, otherwise cursor will be unchanged
            writeToFileCursor(cursor)

        else:
            logging.info('No transactions...')
            logging.info('Unchanged cursor: %s', payload['cursor'])

    else:
        logging.info('Error...')
        logging.info(payload)
        if '3600' in payload['message']:
            cursorRm = removeCrusorFile()
            logging.info('Old cursor removed: %s', cursorRm)

    # wait X sec and run again
    # For the free plan the number of requests is limited to 10 per minute.
    time.sleep(10)
