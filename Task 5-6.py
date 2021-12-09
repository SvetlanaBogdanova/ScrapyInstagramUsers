from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)

db = client['instagram']

# Выбираем нужного пользователя (user) и тип отношений (relationship_type):
# подписчик на заданного пользователя ("follower") или подписка с его стороны ("following")
# user = '__i.r.i.s.h.k.a__'
user = 'misss_brunetka_'
relationship_type = 'follower'
# relationship_type = 'following'

docs = list(db.users.find({'target_username': user, 'relationship_type': relationship_type}, {'_id': 0, 'username': 1}))

pprint(docs)
print(len(docs))
