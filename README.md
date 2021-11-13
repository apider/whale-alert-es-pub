# whale-alert-es
Whale Alert crypto transaction scraper to Elasticsearch

Scrapes whale-alert crypto transaction data and ingests to Elasticsearch for further dashboarding/graphing.

Elasticsearch ingest is done asynchronously with asyncio & httpx library.
### Uses data from
Main site: 
https://whale-alert.io/

Docs: 
https://docs.whale-alert.io/

## Config ENV vars
You need to specify a few ENV vars:

<code>TOKEN</code> - your personal Whale Alert API key - mandatory

<code>CURSORPATH</code> - path for <code>cursor</code> file, default <code>/data/</code> - optional

<code>MIN_VALUE</code> - minimum transaction value in $, default <code>500000</code> - optional

<code>ESHOST</code> - Elasticsearch host, default <code>http://elasticsearch:9200</code> - optional

<code>ESINDEX</code> - Elasticsearch index name, default <code>whalealert</code> - optional

### API-key / TOKEN
Register with whale-alert and get your private api key. https://whale-alert.io/

You can store api key in a file if you want. 
Change line <code>11-13</code> in <code>app.py</code> accordingly.

### cursor
Whale Alert API gives you a cursor so you can keep track of where in the event flow you are.

I save this cursor in a file called <code>cursor.json</code> to be loaded on program/container restarts so we dont re-fetch old data.

The <code>manifest.yaml</code> has a PVC & mount defined for this.

If you run pure <code>docker</code> you need to create & use a volume for it.

### Elasticsearch config
See 'Config ENV vars' above.

# Running
## locally
Just run <code>python3 app.py</code> on your workstation/server.

Remember to change the <code>cursorpath</code> on line <code>16</code> in <code>app.py</code> and set the <code>TOKEN</code> (see above).
## Docker
Use <code>Dockerfile</code> to build from, if you want to run in container or Kubernetes.

You will need to create & use a volume for <code>cursorpath</code>

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

## enhancements
Some remaining messy static configs like repository etc can probably be switched for ENV VARS. 

## Dashboard
Dashboard & viz export can be found in file <code>kibana-dashboard-and-viz-export.json</code>

This dash could be done much better ofcourse. Also I have a really old ES/Kibana version.

![alt text](https://github.com/apider/whale-alert-es/blob/master/dashboard.png?raw=true)