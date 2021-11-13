# whale-alert-es
Whale Alert crypto transaction scraper to Elasticsearch

Program to scrape whale-alert crypto transaction data and ingest to Elasticsearch for further dashboarding/graphing.
### Uses data from
Main site: 
https://whale-alert.io/

Docs: 
https://docs.whale-alert.io/

## Config
### API-KEY
Register with whale-alert and get your private api key. https://whale-alert.io/

You can either use api key from file <code>key.py</code> or ENV variable <code>TOKEN</code>, if running locally.

See & change line 11-13 in <code>app.py</code> accordingly.

### cursor
Whale Alert gives you a cursor so you can keep track of where in the event flow you are.

I save this cursor in a file called <code>cursor.json</code> to be loaded on program/container restarts.

Path for this file can be changed on line <code>16</code> in <code>app.py</code>

The <code>manifest.yaml</code> has a PVC & mount defined for this.

## Elasticsearch config
You need to change to your ES instance host/url on line <code>27, 28</code> in <code>app.py</code>

In this example it uses unsecure http comms on port <code>9200</code>
# Running
### locally
Just run <code>python3 app.py</code> on your workstation/server.
### Docker
Use <code>Dockerfile</code> tu build from if you want to run in container or Kubernetes.

### Kubernetes
### api-key in k8s
If running in Kubernetes, create a secret named <code>token</code>. Deployment will import it as ENV variable <code>TOKEN</code>.

See <code>manifest.yaml</code>

<code>kubectl -n 'namespace' create secret generic whale-alert-es-secret --from-literal=token='your-whale-alert-api-key'</code>

### repository in k8s
You need to change the repository url & port in <code>manifest.yaml</code> on line <code>24</code>, as manifest uses my local one.