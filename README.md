# whale-alert-es
[![Lint with flake8](https://github.com/apider/whale-alert-es-pub/actions/workflows/flake8-lint.yml/badge.svg)](https://github.com/apider/whale-alert-es-pub/actions/workflows/flake8-lint.yml)
[![CI Pipeline](https://github.com/apider/whale-alert-es-pub/actions/workflows/ci.yaml/badge.svg)](https://github.com/apider/whale-alert-es-pub/actions/workflows/ci.yaml)

Whale Alert crypto transaction scraper to Elasticsearch

Dockerhub: https://hub.docker.com/r/apider/whale-alert-es-pub

Scrapes whale-alert crypto transaction data and ingests to Elasticsearch for further dashboarding/graphing.

This project was done for learning more about async functionality and as a fun crypto project.

Elasticsearch ingest is done asynchronously with asyncio & httpx library.
### Uses data from
Main site: 
https://whale-alert.io/

Docs: 
https://docs.whale-alert.io/

## Config ENV vars
Runtime ENV vars (mandator/optional):

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

If the cursor is older than 3600 seconds, API throws an error and the code handles that and removes the outdated/incorrect cursor.

The <code>manifest.yaml</code> has a PVC & mount defined for this.

If you run pure <code>docker</code> you need to create & use a volume for it.

### Elasticsearch config
See 'Config ENV vars' above.

# Running
## locally
Just run <code>python3 app.py</code> on your workstation/server.

Remember to set the <code>TOKEN</code> and optionally <code>CURSORPATH</code> ENV vars (see above).
## Docker
Use <code>Dockerfile</code> to build from, if you want to run in container or Kubernetes.

You will need to create & use a volume for <code>cursorpath</code> for pure docker.

## Kubernetes
There is a basic <code>manifest.yaml</code> containing Deployment & PVC.
### Name space
The <code>manifest.yaml</code> uses name space <code>prod</code>
### api-key in k8s
Before deploying in Kubernetes, first create a secret named <code>token</code>

Deployment will import it as ENV variable <code>TOKEN</code>

<code>kubectl -n YOUR-NAME-SPACE create secret generic whale-alert-es-secret --from-literal=token='your-whale-alert-api-key'</code>

### k8s image repository
You need to change the repository url & port in <code>manifest.yaml</code> on line <code>29</code>, as manifest uses my local repo.

## Dashboard
A simple Kibana dashboard & viz export can be found in <code>kibana/kibana-dashboard-and-viz-export.json</code>

This dash could be done much better ofcourse. Also I have a really old ES/Kibana version.

![alt text](https://github.com/apider/whale-alert-es/blob/master/kibana/dashboard.png?raw=true)
# whale-alert-priv
