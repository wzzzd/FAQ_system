
import os
import torch
from transformers import AutoTokenizer, AutoModel
from Module.LM.LMEmbedding import LMEmbedding
from Utils.Logger import init_logger


class RankUnsupervise(object):


    def __init__(self, config):
        self.config = config
        self.model_name = self.config.unsup_rank_name
        self.logger = init_logger() #'Rank model'
        self.logger.info('  - Supervise mode: {}'.format(str(self.config.use_supervise)))
        self.logger.info('  - model: {}'.format(self.model_name))

        # 初始化：Distilbert
        if self.model_name in ['simcse-distilbert', 'simcse-bert']:
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.path_unsup_rank)
            self.model = AutoModel.from_pretrained(self.config.path_unsup_rank)
        # 初始化：Language Model
        if self.model_name == 'lm-mini':
            self.model = LMEmbedding()
        # 判断是否使用GPU
        if config.use_cuda:
            self.device = torch.device(self.config.cuda_visible_devices)
            self.model.to(self.device)



    def rank(self, query, corpus, size=10):
        """排序
        Args:
            query (string): 请求文本
            corpus (list): 召回的语料
        Returns:
        """
        self.logger.info('>> Rank Start ...')
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
        ## Distilbert
        if self.model_name in ['simcse-distilbert', 'simcse-bert']:
            # 获取query的embedding输出
            inputs_token = self.tokenizer(query, return_tensors="pt")
            if self.config.use_cuda:
                inputs_token = inputs_token.to(self.device)
            out_query = self.model(**inputs_token)
            emb_query = out_query.last_hidden_state[:,0]
            emb_query = emb_query.transpose(0,1)
            # 获取question的embedding输出
            in_question = self.tokenizer(question, padding=True, return_tensors="pt")
            out_question = self.model(**in_question)
            emb_question = out_question.last_hidden_state[:,0]
            # 计算相似度
            vec_inner = torch.matmul(emb_question, emb_query)
            list_inner = [[ind, x[0]] for ind,x in enumerate(vec_inner.cpu().tolist())]
            # 排序
            score = sorted(list_inner, key=lambda x: x[1], reverse=True)

            a=1
        ## LM
        elif self.model_name == 'lm-mini':
            score = self.model.compute_similarity(query, question)
        ## Surpervise Learning: Distilbert
        else:
            score = []
        
        # 根据index获取answer
        score = score[:size]
        corpus_choice = [corpus[x[0]] for x in score]
        probs = [x[1] for x in score]

        ## 打印top10结果
        self.logger.info('rank top10:')
        for i,line in enumerate(corpus_choice):
            self.logger.info('     - question:{}  - score:{}'.format(line['question'], probs[i]))

        self.logger.info('>> Rank End ...')
        return corpus_choice, probs
