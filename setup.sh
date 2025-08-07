#!/bin/bash
python -m pip install --upgrade pip
python -m nltk.downloader punkt averaged_perceptron_tagger
python -m spacy download pt_core_news_lg
