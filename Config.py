
import os


class Config(object):

    # ES配置
    es_ip = 'http://localhost:9200'
    es_port = 2910
    es_index = 'corpus_faqs_ins_v2' #'corpus_faqs_v2'
    es_timeout = 10

    # 匹配方法
    ## 可选：bm25/ngram/word2vec/lm
    model_name = 'bm25' 


    # 文件
    path_root = os.getcwd()
    path_stopword = os.path.join(path_root, 'file/stopword.txt')
    path_w2v_model = os.path.join(path_root, 'file/model/w2v.model')

    # 数据集
    dataset = 'insuranceqa_test'    # afqmc_public
    path_corpus = os.path.join(path_root, 'data/{}/corpus.txt'.format(dataset))   
