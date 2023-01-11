
from elasticsearch import Elasticsearch
from elasticsearch import helpers


class Recall(object):

    def __init__(self, config):
        self.config = config
        self.es = Elasticsearch(hosts=self.config.es_ip, 
                                    port=self.config.es_port, 
                                    sniff_timeout=self.config.es_timeout)

    
    def recall(self, token, size=200):
        """根据输入的token，召回相关语料库文本
        Args:
            token (list): 分词
            size (int): 每个分词召回的结果数，最大值为10000
        Returns:
            corpus (list): 召回结果
        """
        # 通过DSL语句来查询
        res = []
        for word in token:
            dsl = {
                    'query': {
                        'match': {
                            'question' : word
                        }
                    }
                    # 'collapse':{
                    #     'field':'answer'
                    # }
                }
            response = self.es.search(index=self.config.es_index,  body=dsl, size=size)
            record = response.get('hits',{}).get('hits',[])
            res.extend(record)

        # 解析json
        corpus = []
        # corpus_question = []
        # corpus_answer = []
        cache = []
        for line in res:
            source = line.get('_source', {})
            question = source.get('question', '')
            answer = source.get('answer', '')
            if question+answer != '' and question+answer not in cache:
                corpus.append(source)
                cache.append(question+answer)
            # corpus_question.append(question)
            # corpus_answer.append(answer)
            # corpus.append(source)
        return corpus

        
