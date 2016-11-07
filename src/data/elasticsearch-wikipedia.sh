# Launch Ubuntu instance
# Create 200GB Volume in the same zone and attach it

sudo mkfs.xfs /dev/xvdf
sudo mount /dev/xvdf /wikipedia
sudo chmod 777 /wikipedia

sudo apt-get install openjdk-7-jre-headless
#sudo apt-get install openjdk-7-jdk
#sudo update-alternatives --config java

sudo apt-get install elasticsearch

sudo nano /etc/elasticsearch/elasticsearch.yml
  path.data: /wikipedia

sudo service elasticsearch restart

curl http://localhost:9200
curl -XGET 'http://localhost:9200/_cluster/health?pretty=true'
curl -XGET 'http://localhost:9200/_cluster/state'

sudo /usr/share/elasticsearch/bin/plugin --install elasticsearch/elasticsearch-river-wikipedia/1.1.0
curl -XPUT http://localhost:9200/_river/wikipedia/_meta -d '{ "type" : "wikipedia" }'
#curl -XDELETE http://localhost:9200/_river/wikipedia/

curl http://localhost:9200/wikipedia/_stats
curl http://localhost:9200/wikipedia/_stats/indexing/docs

curl 'http://localhost:9200/wikipedia/page/_search?q=title:banana&fields=_id,title'
curl 'http://localhost:9200/wikipedia/page/13399/_mlt?mlt_fields=title,text'

curl 'http://localhost:9200/wikipedia/page/_mlt?fields=title,text&like_text=this+is+a+banana'

curl -XPOST http://localhost:9200/wikipedia/page/_search -d '{ "query": { "mlt": { "fields": ["title", "text"], "like_text": "this is a banana", "min_term_freq": 1, "max_query_terms" : 20 } } }'