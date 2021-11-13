# whale-alert-es
Whale Alert crypto transaction scraper to Elasticsearch

Scrapes whale-alert crypto transaction data and ingests to Elasticsearch for further dashboarding/graphing.

Elasticsearch ingest is done asynchronously with asyncio & httpx library.
### Uses data from
Main site: 
https://whale-alert.io/

Docs: 
https://docs.whale-alert.io/

## Config envs and vars
### API-KEY
Register with whale-alert and get your private api key. https://whale-alert.io/

You can either use api key from file <code>token.py</code> or ENV variable <code>TOKEN</code>, if running locally.

See & change line 11-13 in <code>app.py</code> accordingly.

### cursor
Whale Alert gives you a cursor so you can keep track of where in the event flow you are.

I save this cursor in a file called <code>cursor.json</code> to be loaded on program/container restarts so we dont re-fetch old data.

Path for this file can be changed on line <code>16</code> in <code>app.py</code>

The <code>manifest.yaml</code> has a PVC & mount defined for this.

If you run pure <code>docker</code> you need to create & use a volume for it.

### Elasticsearch config
You need to change to your ES instance host/url & index on line <code>27, 28</code> in <code>app.py</code>

In this example it uses unsecure http comms on port <code>9200</code>
# Running
## locally
Just run <code>python3 app.py</code> on your workstation/server.

Remember to change the cursor file path on line <code>16</code> in <code>app.py</code> and set the <code>TOKEN</code> (see above).
## Docker
Use <code>Dockerfile</code> to build from, if you want to run in container or Kubernetes.

## Kubernetes

### Name space
By default the <code>manifest.yaml</code> uses name space <code>prod</code>
### api-key in k8s
There is a basic <code>manifest.yaml</code> containing Deployment & PVC.

Before running in Kubernetes, first create a secret named <code>token</code>

Deployment will import it as ENV variable <code>TOKEN</code>

<code>kubectl -n YOUR-NAME-SPACE create secret generic whale-alert-es-secret --from-literal=token='your-whale-alert-api-key'</code>

### k8s image repository
You need to change the repository url & port in <code>manifest.yaml</code> on line <code>24</code>, as manifest uses my local repo.