

import os
import pandas as pd
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from gensim.test.utils import common_texts
# from gensim.models.word2vec import Word2Vec
import jieba
import numpy as np




class W2VTX(object):

    def __init__(self, config):
        self.config = config
        path_stopword = self.config.path_stopword
        self.min_count = 1
        self.window = 5
        self.workers = 8
        self.size = 100
        self.model = Word2Vec(min_count=self.min_count, window=self.window, workers=self.workers, vector_size=self.size)
        self.stopword = [ w.strip() for w in open(path_stopword, 'r', encoding='utf8').readlines()]
        # self.dict_word = list(self.model.wv.key_to_index.keys())
        

    def tokenizer(self, sentence):
        """
        对单个句子进行分词
        """
        words = jieba.cut(sentence, cut_all=False)                  # 精确模式
        # words = [ w for w in words if w not in self.stopword]
        words = [ w for w in words]
        return words

    
    def get_corpus(self, corpus):
        """
        对语料库中的每个句子进行分词
        """
        print('word2vec: tokenizer...')
        sentences = [ self.tokenizer(sen) for sen in corpus]
        return sentences


    def get_word_embedding(self, word):
        """
        获取单词的embedding vector
        同时需要考虑OOV的问题
        """
        try:
            vec = self.model.word_vec(word)
        except KeyError:
            vec = np.zeros(self.size, dtype=np.float32)
            num = 0
            for w in word:
                if w in self.dict_word:
                    vec += self.model.word_vec(w)
                    num += 1
            vec /= max(1, num)
        return vec


    def get_embedding(self, sentence):
        """
        获取句子的embedding vector
        """
        vec = np.zeros(self.size, dtype=np.float32)
        for word in sentence:
            vec += self.get_word_embedding(word)
        vec /= max(1, len(sentence))
        return vec

    
    def compute_similarity(self, query, corpus):
        """计算文本与语料库的相似度
        Args:
            query (_type_): _description_
            corpus (_type_): _description_
        """
        score = []
        for i,c in enumerate(corpus):
            # cos_sim = query.dot(c) / np.linalg.norm(query) * np.linalg.norm(c)
            dot = float(np.dot(query, c))
            norm = np.linalg.norm(query)*np.linalg.norm(c)
            cos_sim = dot / max(norm, 1)
            score.append([i, cos_sim])
        scores_rank = sorted(score, key=lambda x: x[1], reverse=True)
        return scores_rank 

    
    def load(self, path):
        """
        读取模型/词向量
        """
        self.model = KeyedVectors.load_word2vec_format(path, binary=False)
        self.dict_word = list(self.model.key_to_index.keys())
        

    