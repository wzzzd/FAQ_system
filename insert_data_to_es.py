

import jieba
import pandas as pd
from Config import Config

from elasticsearch import Elasticsearch
from elasticsearch import helpers

    
def main():
    """
    初始化数据：语料库导入到ES
    """
    # 读取配置
    config = Config()
    es = Elasticsearch(hosts=config.es_ip, 
                        # port=config.es_port, 
                        sniff_timeout=config.es_timeout)
    # 读取数据
    data = pd.read_csv(config.path_corpus, sep='\t')
    corpus = data.values

    # 创建ES索引
    mapping = {
        "mappings": {
                "properties" : {
                    "question" : {
                        "type" : "text",    # keyword
                    },
                    "answer" : {
                        "type" : "text",
                    },
                    "question_token" : {
                        "type" : "text",
                    }
                }
            }
        }
    es.indices.create(index=config.es_index, body=mapping)

    # 插入es
    ## 格式处理
    action = []
    for i, line in enumerate(corpus):
        tmp_action = {
            "_index": config.es_index,
            "_source": {
                'question': line[0],
                'answer' : line[1],
                'question_token':  ' '.join([ x for x in jieba.cut(line[0], cut_all=False)])
            }
        }
        action.append(tmp_action)
    ## 提交
    interval = 10000
    post_data = []
    for i, line in enumerate(action):
        post_data.append(line)
        if i % interval == 0:
            helpers.bulk(es, action)
            post_data = []
    if post_data:
        helpers.bulk(es, action)


if __name__ == '__main__':
    main()

