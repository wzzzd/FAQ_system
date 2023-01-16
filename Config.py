
import os


class Config(object):

    # 文件
    path_root = os.getcwd()
    path_stopword = os.path.join(path_root, 'file/stopword.txt')
    path_w2v_model = os.path.join(path_root, 'file/model/w2v.model')

    # ES配置
    es_ip = 'http://localhost:9200'
    es_port = 2910
    es_index = 'corpus_faqs_ins_zhidao_v1' #'corpus_faqs_v2'
    es_timeout = 10

    # 数据集
    dataset = 'insurance_zhidao_test'    # afqmc_public
    path_corpus = os.path.join(path_root, 'data/{}/corpus.txt'.format(dataset))   

    # 粗排Prerank
    ## 可选：bm25/ngram/word2vec
    prerank_name = 'word2vec' 


    # 精排Rank
    ## GPU配置
    use_cuda = True                             # 是否使用GPU
    cuda_visible_devices = 'cpu'
    ## 可选：Distilbert/lm-mini/
    use_rank = True                             # 是否开启精排，True开启，False不开启
    use_supervise = True                       # True表示使用有监督方法，False表示使用无监督方法
    ## 无监督方法
    unsup_rank_name = 'lm-mini'                 # 可选：simcse-distilbert/simcse-bert/lm-mini
    path_unsup_rank = os.path.join(path_root, 'file/rank_simcse_distilbert_zhidao/')
    # path_rank = 'liam168/c4-zh-distilbert-base-uncased'
    ## 有监督方法
    sup_rank_name = 'bert'                      # 可选：distilbert/bert
    path_sup_rank_model = os.path.join(path_root, 'file/supervise/bert/')
    sup_rank_model_tokenizer = 'bert-base-chinese'  #'liam168/c4-zh-distilbert-base-uncased'#



