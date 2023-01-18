

import os
import pandas as pd
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from gensim.test.utils import common_texts

# from gensim.models.word2vec import Word2Vec
import jieba
import numpy as np




class W2V(object):

    def __init__(self, config):
        self.config = config
        path_stopword = self.config.path_stopword
        self.min_count = 1
        self.window = 5
        self.workers = 8
        self.size = 300
        self.model = Word2Vec(min_count=self.min_count, window=self.window, workers=self.workers, vector_size=self.size)
        self.stopword = [ w.strip() for w in open(path_stopword, 'r', encoding='utf8').readlines()]


    def train(self, corpus):
        """
        训练word2vec模型
        """
        # model.save("word2vec.model")
        # model = Word2Vec.load("word2vec.model") 
        print('word2vec: training...')
        self.model.build_vocab(corpus)                                                                  # prepare the model vocabulary
        self.model.train(corpus, total_examples=self.model.corpus_count, epochs=self.model.epochs)      # train word vectors


    def tokenizer(self, sentence):
        """
        对单个句子进行分词
        """
        words = jieba.cut(sentence, cut_all=False)                  # 精确模式
        words = [ w for w in words if w not in self.stopword]
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
        dict_word = self.model.wv.vocab.keys()
        if word in dict_word:
            # 在词典里
            vec = self.model.wv[word]                          # get numpy vector of a word
        else:
            # 不在词典里
            # 判断词组长度，遍历词组所有字，获取融合后的字向量
            vec = np.zeros(self.size, dtype=np.float32)
            num = 0
            if len(word) > 1:
                for w in word:
                    if w in dict_word:
                        vec += self.model.wv[word]
                        num += 1
            vec /= max(1, num)
        return vec


    def get_sentence_embedding(self, sentence):
        """
        获取句子的embedding vector
        """
        vec = np.zeros(self.size, dtype=np.float32)
        for word in sentence:
            vec += self.get_word_embedding(word)
        vec /= max(1, len(sentence))
        return vec

        
    def save(self, path, m='model'):
        """
        保存模型/词向量
        """
        print('word2vec: saving...')
        if m == 'model':
            # 保存模型
            self.model.save(path)
        else:
            # 只保存词向量
            self.model.wv.save(path)

    
    def load(self, path, m='model'):
        """
        读取模型/词向量
        """
        print('word2vec: loading...')
        if m == 'model':
            # 读取模型
            self.model = Word2Vec.load(path)
        else:
            # 只读取词向量
            wv = KeyedVectors.load(path, mmap='r')
            return wv
        

    def get_sims_word(self, word):
        """
        获取相似度较高的词
        """
        words = self.model.wv.most_similar(word, topn=10) 
        return words

    
    def stats_word(self, corpus):
        """
        统计词频
        """
        d = {}
        for line in corpus:
            for w in line:
                d.setdefault(w,0)
                d[w] += 1
        
        d = sorted(d.items(), key=lambda x: x[1], reverse=True)
        with open('./cache/stats.csv', 'w', encoding='utf8') as f:
            for x in d:
                string = str(x[0]) + '\t' + str(x[1]) + '\n'
                f.write(string)


    def read_keyword(self, path_keyword):
        """获取关键词字典"""
        list_file = os.listdir(path_keyword)
        dict_file = {}
        for file in list_file:
            # 读取文件
            file_name = file.split('-')[0]
            file_content = open(os.path.join(path_keyword, file), 'r', encoding='utf8').readlines()
            file_content = [ x.strip() for x in file_content if x.strip() != '']
            # 存入字典
            dict_file.setdefault(file_name, [])
            dict_file[file_name] = list(set(dict_file[file_name]).union(file_content))
        return dict_file


if __name__ == '__main__':

    mode = 'train'
    if mode == 'train':
        obj = W2V()                                                     # 初始化模型
        # corpus = ["cat say meow", "dog say woof"]                       # 语料demo
        corpus = [ x.strip() for x in open('./data/word2vec/corpus.many.txt', 'r', encoding='utf8').readlines()]#[:10]
        corpus = obj.get_corpus(corpus)                                 # 对语料进行分词
        obj.train(corpus)                                               # 训练模型
        obj.save('./models/word2vec/w2v.model')
        # vec = obj.get_word_embedding('dog')                             # 获取单词向量
        # vec_sen = obj.get_sentence_embedding('The dog is running')      # 获取句子向量
    else:
        obj = W2V()
        obj.load('./word2vec/model/w2v.model')
        sims = obj.model.wv.most_similar('弹', topn=100) 
        # for w in sims:
        #     print(sims)
        sims = [[word, score] for word, score in sims]
        dt = pd.DataFrame(sims,columns=['word','score'])
        dt.to_csv('./word2vec/cache/words.txt', sep='\t', index=False)
