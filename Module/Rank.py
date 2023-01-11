
import os
import pandas as pd
from Module.BM25.BM25 import BM25
from Module.Ngram.Ngram import Ngram
from Module.Word2Vec.Word2Vec import W2V
# from Module.Word2Vec.train import W2V
from Module.LM.LMEmbedding import LMEmbedding


class Rank(object):


    def __init__(self, config):
        self.config = config
        self.model_name = self.config.model_name
        print('Rank model: {}'.format(self.model_name))

        # 初始化：Word2Vec
        if self.model_name == 'word2vec':
            self.model = W2V(config)
            ## 若不存在word2vec模型，则训练
            if not os.path.exists(self.config.path_w2v_model):
                print('     - model: not exist')
                print('     - model: training ...')
                data = pd.read_csv(self.config.path_corpus, sep='\t')
                corpus = data['question'].drop_duplicates().tolist() + data['answer'].drop_duplicates().tolist()
                corpus = self.model.get_corpus(corpus)
                self.model.train(corpus)
                self.model.save(self.config.path_w2v_model)
            else:
                print('     - model: exist')
                print('     - model: loading ...')
                self.model.load(self.config.path_w2v_model)
        # 初始化：BM25
        if self.model_name == 'bm25':
            # self.model = BM25()
            pass
        # 初始化：N-gram
        if self.model_name == 'ngram':
            self.model = Ngram()
        # 初始化：Language Model
        if self.model_name == 'lm':
            self.model = LMEmbedding()


    def rank(self, query, query_token, corpus, topk=10):
        """排序
        Args:
            query (string): 请求文本
            corpus (list): 召回的语料
        Returns:
        """
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
            score = self.model.search(query_token, index, topk=topk)
        ## Ngram
        elif self.model_name == 'ngram':
            score = self.model.compute_similarity(query, question, topk=topk)
        ## Word2Vec
        elif self.model_name == 'word2vec':
            query_vec = self.model.get_embedding(query_token)
            corpus_vec = [self.model.get_embedding(line) for line in question_token]
            score = self.model.compute_similarity(query_vec, corpus_vec, topk=topk)
        ## LM
        elif self.model_name == 'lm':
            score = self.model.compute_similarity(query, question, topk=topk)
        ## Surpervise Learning: Distilbert
        else:
            score = []
        
        # index = [x[0] for x in score]
        return score
