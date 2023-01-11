

import jieba
import pandas as pd

from Config import Config
from Module.Recall import Recall
from Module.Rank import Rank
from utils.Logger import init_logger


class FAQ(object):


    def __init__(self):
        self.config = Config()
        self.model_recall = Recall(self.config)
        self.model_rank = Rank(self.config)
        self.logger = init_logger('FAQ')


    def query(self, text, size=3):
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
        # 分词
        tokens = [ x for x in jieba.cut(text, cut_all=False)]
        self.logger.info('token: {}'.format(tokens))
        # 召回
        corpus = self.model_recall.recall(tokens)
        self.logger.info('recall corpus num: {}'.format(len(corpus)))
        # 排序
        scores = self.model_rank.rank(text, tokens, corpus, topk=size)
        ## 根据index获取answer
        corpus_choice = [corpus[x[0]] for x in scores]
        probs = [x[1] for x in scores]
        ## 打印top10结果
        self.logger.info('rank top10:')
        for i,line in enumerate(corpus_choice):
            self.logger.info('     - question:{}  - answer:{}  - score:{}'.format(line['question'], line['answer'], probs[i]))
            # self.logger.info('     - answer:   {}'.format(line['answer']))
        # 返回TopK结果
        res = []
        for i,x in enumerate(corpus_choice[:size]):
            tmp = {
                    'question':x['question'], 
                    'answer':x['answer'], 
                    'score':str(probs[i])
                }
            res.append(tmp)
        return res



if __name__ == '__main__':
    # 读取数据
    path = './data/insuranceqa_test/test.txt'
    data = pd.read_csv(path, sep='\t')

    top1_num = 0
    top3_num = 0
    faq = FAQ()
    for i, line in data.iterrows():
        # print('-'*30)
        question = line['question']
        target = line['answer']
        answer = faq.query(question)
        print('- question:{}'.format(question))
        # print('- answer:  {}'.format(target))
        for line in answer:
            print('     - question:{} '.format(line['question']))
            # print('     - question:{}  - answer:{}'.format(line['question'],line['answer']))
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
    # top1 acc
    top1_acc = top1_num/max(len(data), 1)
    # top3 acc
    top3_acc = top3_num/max(len(data), 1)

    print('top 1 acc={}/{}={}'.format(top1_num, max(len(data), 1), top1_acc))
    print('top 3 acc={}/{}={}'.format(top3_num, max(len(data), 1), top3_acc))
    a = 1

