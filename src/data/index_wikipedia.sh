curl -O download.elasticsearch.org/stream2es/stream2es; chmod +x stream2es

# ./stream2es wiki --target http://localhost:9200/tmp --log debug
# create index http://localhost:9200/wikipedia_en
# stream wiki from http://download.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2

# wget http://download.wikimedia.org/ptwiki/20160920/ptwiki-20160920-pages-articles.xml.bz2
# ./stream2es wiki --target http://localhost:9200/ptwiki --log debug --source ptwiki-20160920-pages-articles.xml.bz2
# Index the latest Wikipedia article dump.

# % stream2es wiki --target http://localhost:9200/tmp --log debug
# create index http://localhost:9200/tmp
# stream wiki from http://download.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2
# ^Cstreamed 1158 docs 1082 bytes xfer 15906901 errors 0
# If you're at a café or want to use a local copy of the dump, supply --source:

# % ./stream2es wiki --max-docs 5 --source /d/data/enwiki-20121201-pages-articles.xml.bz2
# Note that if you live-stream the WMF-hosted dump, it will cut off after a while. Grab a torrent and index it locally if you need more than a few thousand docs.