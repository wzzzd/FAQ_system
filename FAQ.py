

import jieba
import pandas as pd

from Config import Config
from Module.Recall import Recall
from Module.PreRank import PreRank
from Module.RankUnsupervise import RankUnsupervise
from Module.RankSupervise import RankSupervise
from utils.Logger import init_logger


class FAQ(object):


    def __init__(self):

        self.logger = init_logger() # 'FAQ'
        self.logger.info('----------------- Initial -----------------')
        self.config = Config()
        self.model_recall = Recall(self.config)
        self.model_prerank = PreRank(self.config)
        if self.config.use_supervise:
            self.model_rank_sup = RankSupervise(self.config)
        else:
            self.model_rank_unsup = RankUnsupervise(self.config)
        

    def query(self, query, recall_size=1000, prerank_size=100, rank_size=10):
        """
        逻辑：
            1.分词
            2.召回
            3.排序
        Arg:
            text (String): 输入文本
            size (Int): 返回结果大小
        Returns:
            res (Dict): 结果
                - 格式为：[{'question':'xxx', 'answer':'xxx'},...]
        """
        self.logger.info('----------------- FAQ start -----------------')
        self.logger.info('query: {}'.format(query))
        # 分词
        tokens = [ x for x in jieba.cut(query, cut_all=False)]
        self.logger.info('token: {}'.format(tokens))
        # 召回
        corpus = self.model_recall.recall(tokens, size=recall_size)
        self.logger.info('recall corpus num: {}'.format(len(corpus)))
        # 粗排
        corpus_prerank, score = self.model_prerank.rank(query, tokens, corpus, size=prerank_size)
        # 精排
        if self.config.use_rank:
            if self.config.use_supervise:
                corpus_rank, score = self.model_rank_sup.rank(query, corpus_prerank, size=rank_size)
            else:
                corpus_rank, score = self.model_rank_unsup.rank(query, corpus_prerank, size=rank_size)
        else:
            corpus_rank, score =corpus_prerank, score
        # 返回结果
        res = []
        for i,x in enumerate(corpus_rank):
            tmp = {
                    'question':x['question'], 
                    'answer':x['answer'], 
                    'score':str(score[i])
                }
            res.append(tmp)
        self.logger.info('----------------- FAQ end-----------------')
        return res



if __name__ == '__main__':
    # 读取数据
    path = './data/insurance_zhidao_test/test.txt'
    data = pd.read_csv(path, sep='\t')

    top1_num = 0
    top3_num = 0
    top10_num = 0
    recall_num = 0
    faq = FAQ()
    for i, line in data.iterrows():
        # print('-'*30)
        question = line['question']
        target = line['answer']
        answer = faq.query(question)
        # top1 num
        module = answer[0]['answer']
        if target==module:
            top1_num += 1
        # top3 num
        for x in answer[:3]:
            module = x['answer']
            if target==module:
                top3_num += 1
                break
        # top10 num
        for x in answer[:10]:
            module = x['answer']
            if target==module:
                top10_num += 1
                break
        #  num
        for x in answer:
            module = x['answer']
            if target==module:
                recall_num += 1
                break
    # acc
    top1_acc = top1_num/max(len(data), 1)
    top3_acc = top3_num/max(len(data), 1)
    top10_acc = top10_num/max(len(data), 1)
    recall = recall_num/max(len(data), 1)

    print('top 1 acc={}/{}={}'.format(top1_num, max(len(data), 1), top1_acc))
    print('top 3 acc={}/{}={}'.format(top3_num, max(len(data), 1), top3_acc))
    print('top 10 acc={}/{}={}'.format(top10_num, max(len(data), 1), top10_acc))
    print('recall acc={}/{}={}'.format(recall_num, max(len(data), 1), recall))
    a = 1

