from __future__ import division
from elasticsearch import Elasticsearch
from scipy import stats
import math
import operator
from pathos.pools import ProcessPool, ThreadPool
from sklearn import preprocessing
import numpy as np
from abc import ABCMeta, abstractmethod

N_CPUS = 8

class TopicCoherence(object):
    __metaclass__ = ABCMeta

    epsilon = 1

    def __init__(self, index_name, doc_type, es_address="localhost:9200"):
        self.index_name = index_name
        self.doc_type = doc_type

        self.pairwise_probability = {}
        self.word_probability = {}
        self.pairwise_hits = {}
        self.word_hits = {}
        self.coherence_scores = {}
        # self.pairwise = {}

        self.es = Elasticsearch(es_address)
        self.collection_size = self.get_collection_size(index_name, doc_type)

    @staticmethod
    def normalize(scores):
        scores = np.array(scores)
        scores = scores.reshape(1, -1)

        min_max_scaler = preprocessing.Normalizer()
        normalized_scores = min_max_scaler.fit_transform(scores)

        return normalized_scores[0].tolist()

    @staticmethod
    def entropy(scores):
        return stats.entropy(scores)

    @abstractmethod
    def compute_pairwise_hits(self, pairwise_key): pass

    @abstractmethod
    def compute_coherence(self, prob_ngrams, prob_ngram_a, prob_ngram_b): pass

    @abstractmethod
    def fit(self, words): pass

    def get_hit_count_for_terms(self, es_index_name, terms):
        exact_terms = ["\"" + x + "\"" for x in terms]
        lucene_query = " AND ".join(exact_terms)

        res = self.es.search(index=es_index_name,
                             q=lucene_query,
                             doc_type=self.doc_type)

        return res['hits']['total']

    def compute_probability(self, hits):
        hits = 0 if (hits is None) else hits
        return float(hits) / float(self.collection_size)

    def get_collection_size(self, index_name, _doc_type):
        res = self.es.search(index=index_name,
                             doc_type=_doc_type,
                             body={"query": {"match_all": {}}})

        return res['hits']['total']

    def compute_word_hits(self, word):
        self.word_hits[word] = self.get_hit_count_for_terms(self.index_name, [word])
        self.word_probability[word] = self.compute_probability(self.word_hits[word])


class UCI(TopicCoherence):
    def compute_pairwise_hits(self, pairwise_key):
        word_i = pairwise_key.split("_")[0]
        word_j = pairwise_key.split("_")[1]
        self.pairwise_hits[pairwise_key] = self.get_hit_count_for_terms(self.index_name, [word_i, word_j])
        self.pairwise_probability[pairwise_key] = self.compute_probability(self.pairwise_hits[pairwise_key])
        self.coherence_scores[pairwise_key] = self.compute_coherence(
            self.pairwise_probability[pairwise_key],
            self.word_probability[word_i],
            self.word_probability[word_j])

    def compute_coherence(self, prob_ngrams, prob_ngram_a, prob_ngram_b):
        prob_ngram_a = 1 if (prob_ngram_a == 0) else prob_ngram_a
        prob_ngram_b = 1 if (prob_ngram_b == 0) else prob_ngram_b

        prob_product = (prob_ngrams + self.epsilon) / (prob_ngram_a * prob_ngram_b)
        prob_product = 1 if (prob_product == 0.0) else prob_product

        res = math.log(prob_product)
        return res

    def fit(self, words):

        self.coherence_scores = {}

        self.pairwise_probability = {}
        self.word_probability = {}

        self.pairwise_hits = {}
        self.word_hits = {}

        for word_i in words:
            for word_j in words:
                if word_i is not word_j:
                    pairwise_key = "_".join(sorted([word_i, word_j]))
                    if pairwise_key not in self.pairwise_probability.keys():
                        self.pairwise_probability[pairwise_key] = 0
                        self.pairwise.append(pairwise_key)

        pool = ThreadPool(N_CPUS)
        pool.map(self.compute_word_hits, words)
        pool.map(self.compute_pairwise_hits, self.pairwise)

        return sum(self.coherence_scores.values())

    def __init__(self, index_name, doc_type, es_address):
        super(UCI, self).__init__(index_name, doc_type, es_address)
        self.pairwise = []


class UMass(TopicCoherence):
    def __init__(self, index_name, doc_type, es_address="localhost:9200"):
        super(UMass, self).__init__(index_name, doc_type, es_address="localhost:9200")
        self.word_scores = {}
        self.pairwise = {}
        # self.words = words

    def compute_pairwise_hits(self, pairwise_key):

        most_rare_hits = self.pairwise[pairwise_key]["most_rare_hits"]
        most_common_hits = self.pairwise[pairwise_key]["most_common_hits"]
        most_common_ngram = self.pairwise[pairwise_key]["most_common_ngram"]
        most_rare_ngram = self.pairwise[pairwise_key]["most_rare_ngram"]

        self.pairwise_hits[pairwise_key] = self.get_hit_count_for_terms(self.index_name,
                                                                        [most_rare_ngram, most_common_ngram])

        self.pairwise_probability[pairwise_key] = self.compute_probability(self.pairwise_hits[pairwise_key])

        self.word_probability[most_rare_ngram] = self.compute_probability(most_rare_hits)

        self.word_probability[most_common_ngram] = self.compute_probability(most_common_hits)

        self.coherence_scores[pairwise_key] = self.compute_coherence(
            self.pairwise_probability[pairwise_key],
            self.word_probability[most_common_ngram],
            self.word_probability[most_rare_ngram])

    def compute_coherence(self, prob_ngrams, prob_ngram_a, prob_ngram_b):
        prob_ngram_a = 1 if (prob_ngram_a == 0) else prob_ngram_a
        prob_ngram_b = 1 if (prob_ngram_b == 0) else prob_ngram_b

        prob_product = (prob_ngrams + self.epsilon) / prob_ngram_a
        prob_product = 1 if (prob_product == 0.0) else prob_product

        res = math.log(prob_product)
        return res

    def fit(self, words):
        self.coherence_scores = {}

        self.pairwise_probability = {}
        self.word_probability = {}

        self.pairwise_hits = {}
        self.word_hits = {}

        pool = ThreadPool(N_CPUS)
        pool.map(self.compute_word_hits, words)

        # for word_i in self.words:

        sorted_desc = sorted(self.word_hits.items(), key=operator.itemgetter(1), reverse=True)
        sorted_asc = sorted(self.word_hits.items(), key=operator.itemgetter(1))

        for most_common in sorted_desc:
            most_common_ngram = most_common[0]
            most_common_hits = most_common[1]

            for most_rare in sorted_asc:
                most_rare_ngram = most_rare[0]
                most_rare_hits = most_rare[1]

                if most_common_ngram is not most_rare_ngram:
                    if most_rare_hits < most_common_hits:
                        pairwise_key = most_rare_ngram + "_" + most_common_ngram

                        if pairwise_key not in self.pairwise_probability.keys():
                            self.pairwise_probability[pairwise_key] = 0
                            self.pairwise[pairwise_key] = {
                                "most_common_ngram": most_common_ngram,
                                "most_common_hits": most_common_hits,
                                "most_rare_ngram": most_rare_ngram,
                                "most_rare_hits": most_rare_hits
                            }

        pool.map(self.compute_pairwise_hits, self.pairwise.keys())

        return sum(self.coherence_scores.values())

    def __init__(self, index_name, doc_type, es_address):
        super(UMass, self).__init__(index_name, doc_type, es_address)
        self.pairwise = {}