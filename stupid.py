from elasticsearch import Elasticsearch
es = Elasticsearch('http://localhost:9200')
es.index(index='my_index',doc_type='my_index', id=1, body={'text': "#coool stuff is keaton"})
es.index(index='my_index', doc_type='my_index', id=2, body={'text': 'a second test'})
ret = es.search(index='my_index', doc_type ='my_index', body={'query': {'match': {'text':'keaton'}}})
print(ret)
es.indices.delete('my_index')