

import math


class BM25(object):
    

    def __init__(self):
        self.f = []                                                 # 列表的每一个元素是一个dict，dict存储着一个文档中每个词的出现次数
        self.df = {}                                                # 存储每个词及出现了该词的文档数量
        self.idf = {}                                               # 存储每个词的idf值
        self.k1 = 1.5
        self.b = 0.75
        

    def init_corpus(self, docs):
        """
        初始化语料
        """
        self.D = len(docs)                                          # 文档数量
        self.avgdl = sum([len(doc)+0.0 for doc in docs]) / self.D   # 平均每个文档的句子长度=所有文档的token总数/文档数量
        self.docs = docs
        # 计算词频
        for i,doc in enumerate(self.docs):
            # 单文档中的词频
            tmp = {}
            for word in doc:
                tmp[word] = tmp.get(word, 0) + 1  # 存储每个文档中每个词的出现次数
            self.f.append(tmp)
            # 所有文档中单个词出现的文档数
            for k in tmp.keys():
                self.df[k] = self.df.get(k, 0) + 1
        # 计算每个文档的IDF值
        for k, v in self.df.items():
            self.idf[k] = math.log(self.D-v+0.5)-math.log(v+0.5)


    def search(self, query, corpus):
        """
        计算query与库中所有文档的相似性
        """
        # 计算文档相似性
        scores = []
        for index, line in enumerate(corpus):
            score = self.sim(query, index)
            scores.append([index, score])
        # 排序
        score_sort = sorted(scores, key=lambda x: x[1], reverse=True)
        # index = [ x[0] for x in score_sort ]
        # 计算概率：按照排序分数
        # value = sum([x[1] for x in score_sort])
        # probs = [[x[0], x[1]/max(1,value)] for x in score_sort]
        return score_sort


    def sim(self, query, doc_index):
        """计算相似度
        Args:
            doc (_type_): query
            index (_type_): 文档库中的index
        """
        score = 0
        for word in query:
            # 跳过在doc中不存在的word
            if word not in self.f[doc_index]:
                continue
            # doc中index文档的token长度
            d = len(self.docs[doc_index])
            # 相似度
            word_idf = self.idf[word]                   # 词IDF值
            word_freq = self.f[doc_index][word]         # 词频
            K = 1-self.b + self.b*(d/self.avgdl)        # 约束文档长度在比较中的重要性
            score += (word_idf*word_freq*(self.k1+1) / (word_freq+self.k1*K))
        return score


    # def search(self, query, recall_index, topk=3):
    #     """
    #     计算query与库中所有文档的相似性
    #     """
    #     # 计算文档相似性
    #     scores = []
    #     for index in recall_index:
    #         score = self.sim(query, index)
    #         scores.append([index, score])
    #     # 排序
    #     scores_rank = sorted(scores, key=lambda x: x[1], reverse=True)[:topk]
    #     # index = [ x[0] for x in scores_rank ]
    #     # 计算概率：按照排序分数
    #     # value = sum([x[1] for x in scores_rank])
    #     # probs = [[x[0], x[1]/max(1,value)] for x in scores_rank]
    #     return scores_rank
