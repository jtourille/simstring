# coding: utf-8

from simstring.feature_extractor.character_ngram import CharacterNgramFeatureExtractor
from simstring.feature_extractor.mecab_ngram import MecabNgramFeatureExtractor
from simstring.measure.cosine import CosineMeasure
from simstring.database.mongo import MongoDatabase
from simstring.searcher import Searcher

text = u"あなたはとてもお洒落ですね"

db = MongoDatabase(MecabNgramFeatureExtractor(2))
db.add(text)
db.add('あなたとてもお洒落ですね')
db.add('あの暑い夏の日のこと')
print(db.all_documents())

searcher = Searcher(db, CosineMeasure())
xs = searcher.search(text, 0.5)
print(xs)
