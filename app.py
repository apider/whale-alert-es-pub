import json
import asyncio
import httpx
import time
import logging
import os
from datetime import datetime

# Parameters and setup

# get ans set whale-alert-api-key (token)
# from key import TOKEN
TOKEN = os.environ.get('TOKEN')

# set cursor file path
cursorpath = '/data/'

# Set up logging
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.INFO)

# min individual transaction dollar value (free plan: 500k minimum)
min_value = 500000
logging.info('Individual transaction minimal value: $%s', min_value)

# Elasticearch params
eshost = 'http://elasticsearch.home:9200'
esindex = 'whalealert'
esurl = eshost + '/' + esindex + '/_doc/'
esheaders = {'Content-Type': 'application/json'}

# whale alert vars
url = 'https://api.whale-alert.io'
transactionUri = '/v1/transactions'
diff = 3599


async def getWhaleData(cursor):
    timestamp = int(time.time()) - diff

    params = {
        'api_key': TOKEN,
        'min_value': min_value,
        'start': timestamp,
        'cursor': cursor
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(url=url + transactionUri, params=params)
        return r.json()


# for initial tests
# def writeToFileJson(payload):
#     with open("api-example-output.json", "w") as f:
#         f.write(json.dumps(payload, indent=4))


def writeToFileCursor(cursor):
    with open(cursorpath + "cursor.json", "w") as f:
        logging.info('Updating cursor file, cursor: %s', payload['cursor'])
        cursorj = {'cursor': cursor}
        f.write(json.dumps(cursorj, indent=4))


def fetchLatestCursor():
    try:
        with open(cursorpath + "cursor.json", "r") as f:
            cursor = json.load(f)['cursor']
    except:
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

            ### Post to Elasticsearch async
            tasks.append(asyncio.ensure_future(postEs(client, item)))

        asyncresponse = await asyncio.gather(*tasks)

        logging.info("--- Async total time: %s sec ---" %
                     (time.time() - start_time))
        logging.info('Posting to ES finished')

        # optional logging, of async post operations, remove if you want
        for i in asyncresponse:
            logging.info(i)


# Try to fetch old cursor from file at startup
cursor = fetchLatestCursor()

while True:
    payload = asyncio.run(getWhaleData(cursor))

    if payload and payload['result'] == 'success':
        # save new cursor
        cursor = payload['cursor']

        if payload['count'] > 0:
            logging.info('Got new transactions! Trans count: %s',
                         payload['count'])

            asyncio.run(elasticsearchSend(payload))

            # update new cursor in file for restarts
            # only needed if there is new data, otherwise cursor will be unchanged
            writeToFileCursor(cursor)

        else:
            logging.info('No transactions...')
            logging.info('Unchanged cuursor: %s', payload['cursor'])

    else:
        logging.info('Error...')
        logging.info(payload)

    # wait X sec and run again
    time.sleep(10)