from __future__ import unicode_literals, print_function

import logging
from nltk.corpus import stopwords
import nltk
import string
import re
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.porter import *
from nltk.stem import porter
from nltk.stem.util import suffix_replace

from nltk.stem.api import StemmerI


def remove_digits(text):
    words = text.split(" ")
    digits_pattern = re.compile(r"\d")

    clean_words = [i for i in words if not digits_pattern.search(i)]

    result = " ".join(clean_words)
    return result


def remove_ponctuations(text):
    words = text.split(" ")
    punctuations_pattern = re.compile(r"[^a-zA-Z0-9]")

    # result = ' '.join(word.replace("."," ").strip(string.punctuation) for word in words)
    clean_words = [i for i in words if not punctuations_pattern.search(i)]

    result = " ".join(clean_words)
    return result


def remove_urls(text):
    words = text.split(" ")
    urls_pattern = re.compile(
        r"((https?|ftp|gopher|telnet|file|Unsure|http):((//)|(\\\\))+[\\w\\d:#@%/;$()~_?\\+-=\\\\\\.&]*)")

    clean_words = [i for i in words if not urls_pattern.search(i)]

    result = " ".join(clean_words)
    return result


def remove_short_tokens(text):
    words = text.split(" ")

    clean_words = [i for i in words if len(i) >= 3]
    result = " ".join(clean_words)
    return result


def remove_nltk_stopwords(text):
    text = ' '.join([word for word in text.split() if word not in stopwords.words('english')])

    return text


def remove_local_stopwords(text):
    text = ' '.join([word for word in text.split() if word not in ['don', 'com', 'jpeg', 'gif', 've', 'use']])

    return text


def run_stemmer(text, stemmer):
    words = text.split(" ")

    singles = [stemmer.stem(token) for token in words]
    text = " ".join(singles)

    return text


def clean_text(text):
    text = text.lower()

    text = remove_urls(text)
    text = remove_digits(text)
    text = remove_ponctuations(text)
    text = remove_nltk_stopwords(text)
    text = remove_local_stopwords(text)
    text = remove_short_tokens(text)

    # eng_stemmer = SnowballStemmer("english")
    # test enabled stemmer
    # text = run_stemmer(text,eng_stemmer)

    return text
