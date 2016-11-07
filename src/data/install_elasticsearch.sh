#!/bin/bash
echo "prepare to download $ELASTICSEARCH_HTTP"

export ELASTICSEARCH_VERSION=2.4.0
export ELASTICSEARCH_NAME=elasticsearch-${ELASTICSEARCH_VERSION}
export ELASTICSEARCH_FILE=${ELASTICSEARCH_NAME}.tar.gz
echo $ELASTICSEARCH_FILE
export ELASTICSEARCH_HTTP=https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/tar/elasticsearch/$ELASTICSEARCH_VERSION/$ELASTICSEARCH_FILE

curl -O  $ELASTICSEARCH_HTTP

tar -zxvf $ELASTICSEARCH_FILE

# echo "start elasticsearch server"
# ${ELASTICSEARCH_NAME}/bin/elasticsearch

#elasticsearch-2.4.0/bin/elasticsearch -d demonize
# echo "testing server connection"
# curl 'http://localhost:9200/?pretty'