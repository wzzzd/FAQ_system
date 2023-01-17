
import os
import pandas as pd
from Module.BM25.BM25 import BM25
from Module.Ngram.Ngram import Ngram
from Module.Word2Vec.Word2Vec import W2V
# from Module.Word2Vec.train import W2V
from Module.LM.LMEmbedding import LMEmbedding
from Utils.Logger import init_logger


class PreRank(object):


    def __init__(self, config):
        self.config = config
        self.model_name = self.config.prerank_name
        self.logger = init_logger() # 'PreRank model'
        self.logger.info('  - model: {}'.format(self.model_name))

        # 初始化：Word2Vec
        if self.model_name == 'word2vec':
            self.model = W2V(config)
            ## 若不存在word2vec模型，则训练
            if not os.path.exists(self.config.path_w2v_model):
                self.logger.info('     - model: not exist')
                self.logger.info('     - model: training ...')
                data = pd.read_csv(self.config.path_corpus, sep='\t')
                corpus = data['question'].drop_duplicates().tolist() + data['answer'].drop_duplicates().tolist()
                corpus = self.model.get_corpus(corpus)
                self.model.train(corpus)
                self.model.save(self.config.path_w2v_model)
            else:
                self.logger.info('     - model: exist')
                self.logger.info('     - model: loading ...')
                self.model.load(self.config.path_w2v_model)
        # 初始化：BM25
        if self.model_name == 'bm25':
            # self.model = BM25()
            pass
        # 初始化：N-gram
        if self.model_name == 'ngram':
            self.model = Ngram()
        # # 初始化：Language Model
        # if self.model_name == 'lm':
        #     self.model = LMEmbedding()


    def rank(self, query, query_token, corpus, size=100):
        """排序
        Args:
            query (string): 请求文本
            corpus (list): 召回的语料
        Returns:
        """
        self.logger.info('>> PreRank Start ...')
        # 获取语料信息
        question = []
        question_token = []
        index = []
        for i,line in enumerate(corpus):
            question.append(line['question'])
            line_q_token = line['question_token'].split(' ')
            question_token.append(line_q_token)
            index.append(i)
        # 计算排序分数
        ## BM25
        if self.model_name == 'bm25':
            self.model = BM25()
            self.model.init_corpus(question_token)
            score = self.model.search(query_token, index)
        ## Ngram
        elif self.model_name == 'ngram':
            score = self.model.compute_similarity(query, question)
        ## Word2Vec
        elif self.model_name == 'word2vec':
            query_vec = self.model.get_embedding(query_token)
            corpus_vec = [self.model.get_embedding(line) for line in question_token]
            score = self.model.compute_similarity(query_vec, corpus_vec)
        # ## LM
        # elif self.model_name == 'lm':
        #     score = self.model.compute_similarity(query, question, topk=topk)
        # ## Surpervise Learning: Distilbert
        else:
            score = []

        # 根据index获取answer
        score = score#[:size]
        corpus_choice = [corpus[x[0]] for x in score]
        probs = [x[1] for x in score]

        ## 打印top10结果
        self.logger.info('rank top10:')
        for i,line in enumerate(corpus_choice[:10]):
            self.logger.info('     - question:{}  - score:{}'.format(line['question'], probs[i]))

        self.logger.info('>> PreRank End ...')
        return corpus_choice, probs
