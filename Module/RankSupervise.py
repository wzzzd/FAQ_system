
import os
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from Module.Model.Bert import Bert
from Module.Model.Distilbert import Distilbert
from Module.LM.LMEmbedding import LMEmbedding
from Utils.Logger import init_logger


class RankSupervise(object):


    def __init__(self, config):
        self.config = config
        os.environ["CUDA_VISIBLE_DEVICES"] = config.cuda_visible_devices

        self.model_name = self.config.sup_rank_name
        self.logger = init_logger() #'Rank model'
        self.logger.info('  - Supervise mode: {}'.format(str(self.config.use_supervise)))
        self.logger.info('  - model: {}'.format(self.model_name))

        # 初始化
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.sup_rank_model_tokenizer)
        if self.config.sup_rank_name == 'distilbert':
            self.model = Distilbert.from_pretrained(self.config.path_sup_rank_model)
        elif self.config.sup_rank_name == 'bert':
            self.model = Bert.from_pretrained(self.config.path_sup_rank_model)
        else:
            self.model = AutoModel.from_pretrained(self.config.path_sup_rank_model)
        if config.use_cuda:
            self.device = torch.device(self.config.cuda_visible_devices)
            self.model.to(self.device)


    def rank(self, query, corpus, size=10, batch_size=8):
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

        # 构造输入文本
        ## 构造方式为sentence1+[SEP]+sentence2
        inputs = []
        for line in question:
            tmp = query + '[SEP]' + line
            inputs.append(tmp)

        # # 计算排序分数
        # # 获取question的embedding输出
        # inputs_token = self.tokenizer(inputs, padding=True, return_tensors="pt")
        # if self.config.use_cuda:
        #     inputs_token = inputs_token.to(self.device)
        # with torch.no_grad():
        #     output = self.model(**inputs_token)
        #     # 获取标签
        #     pred = torch.max(output, 1)[1].cpu().numpy()
        #     # 获取概率
        #     outputs_softmax = F.softmax(output, 1)
        #     prob = torch.max(outputs_softmax, dim=1)[0].cpu().numpy().tolist()

        # # 获取标签为pos的概率值
        # score = []
        # for i,(lab, p) in enumerate(zip(pred, prob)):
        #     if lab==1:
        #         score.append([i, p])
        # # 排序
        # score = sorted(score, key=lambda x: x[1], reverse=True)
        # # 根据index获取answer
        # score = score[:size]
        # corpus_choice = [corpus[x[0]] for x in score]
        # probs = [x[1] for x in score]

        # 按照batch进行数据切片
        input_index = [[i,x] for i,x in enumerate(inputs)]
        interval = input_index[::batch_size]
        indexs = [x[0] for x in interval]
        if indexs[-1]!=len(inputs):
            indexs.append(len(inputs))
        if len(indexs)>1:
            index_range = [[x,y] for x,y in zip(indexs[:-1],indexs[1:])]
        else:
            index_range = [[0,len(indexs)]]
        # 获取question的embedding输出
        pred = []
        prob = []
        for line in index_range:
            tmp_input = inputs[line[0]:line[1]]
            tmp_input_token = self.tokenizer(tmp_input, padding=True, return_tensors="pt")
            with torch.no_grad():
                output = self.model(**tmp_input_token)
            # 获取标签
            tmp_pred = torch.max(output, 1)[1].cpu().numpy().tolist()
            # 获取概率
            outputs_softmax = F.softmax(output, 1)
            tmp_prob = torch.max(outputs_softmax, dim=1)[0].cpu().numpy().tolist()
            pred.extend(tmp_pred)
            prob.extend(tmp_prob)

        # 获取标签为pos的概率值
        score = []
        for i,(lab, p) in enumerate(zip(pred, prob)):
            if lab==1:
                score.append([i, p])
        # 排序
        score = sorted(score, key=lambda x: x[1], reverse=True)

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
