.PHONY: clean data lint requirements sync_data_to_s3 sync_data_from_s3

#################################################################################
# GLOBALS                                                                       #
#################################################################################

#################################################################################
# COMMANDS                                                                      #
#################################################################################

requirements:
	pip install -r requirements.txt

install_elasticsearch:
	src/data/install_elasticsearch.sh

data:
	python src/data/make_dataset.py --elastic_address localhost:9200 --elastic_index 20newsgroups

data_preparation:
	python src/features/build_features.py

topics:
	python src/models/train_lda_model.py

coherence:
	python src/models/compute_topic_coherence.py

clean:
	find . -name "*.pyc" -exec rm {} \;
	find . -name "*.db" -exec rm {} \;

lint:
	flake8 --exclude=lib/,bin/,docs/conf.py .

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################
