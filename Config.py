
import os


class Config(object):

    # 文件
    path_root = os.getcwd()
    path_stopword = os.path.join(path_root, 'file/stopword.txt')
    path_w2v_model = os.path.join(path_root, 'file/model/w2v.model')
    path_w2v_tx = os.path.join(path_root, 'file/model/tencent-ailab-embedding-zh-d100-v0.2.0-s.txt')

    # ES配置
    es_ip = 'http://localhost:9200'
    es_port = 2910
    es_index = 'corpus_faqs_ins_zhidao_v1' 
    es_timeout = 10

    # 数据集
    dataset = 'insurance_zhidao_test'    
    path_corpus = os.path.join(path_root, 'data/{}/corpus.txt'.format(dataset))   

    # 粗排Prerank
    ## 可选：bm25/ngram/word2vec/word2vec-tx
    prerank_name = 'bm25' 

    # 精排Rank
    ## GPU配置
    use_cuda = True                             # 是否使用GPU
    cuda_visible_devices = 'cpu'                # gpu卡号，如0
    use_rank = True                             # 是否开启精排，True开启，False不开启
    use_supervise = True                       # True表示使用有监督方法，False表示使用无监督方法
    
    ## 无监督方法
    unsup_rank_name = 'simcse-bert'                 # 可选：simcse-distilbert/simcse-bert/lm-mini
    path_unsup_rank = os.path.join(path_root, 'file/unsupervise/simcse-bert/')
    ## 有监督方法
    sup_rank_name = 'bert'                          # 可选：distilbert/bert
    path_sup_rank_model = os.path.join(path_root, 'file/supervise/bert/')
    sup_rank_model_tokenizer = 'bert-base-chinese' 



