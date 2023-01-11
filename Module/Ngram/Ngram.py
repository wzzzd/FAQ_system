
import json


class Ngram(object):
    

    def __init__(self):
        pass


    def get_ngram(self, text, n=2):
        """
        获取后缀ngram
        """
        ngram = []
        for i in range(len(text)):
            if i > len(text) - n:
                break
            string = ''
            for num in range(i, i + n):
                string += text[num]
            ngram.append(string)
        return ngram


    def compute_jaccard(self, query, target, d='target'):
        """
        jaccard相似性
        Arg:
            query: List(String)
            target: List(String)
        """
        inter = set(query).intersection(set(target))
        if d=='query':
            div = max(len(query), 1)
        elif d=='target':
            div = max(len(target), 1)
        else:
            merge = set(query).union(set(target))
            div = max(len(merge), 1)
        score = len(inter) / div
        return score
    

    def compute_similarity(self, query, question, topk=10):
        """
        计算query与question的相似度
        Args: 
            query (String): 请求文本
            question (List(String)): 文本库
        Returns:
            score_sort (List): 排序后的topk分数
                - 示例：[[1,0.8],[2,0.7]]
        """
        # 获取query的ngram
        query_ngram = [self.get_ngram(query, n=x) for x in [2,3,4]]
        query_ngrams = [x for line in query_ngram for x in line]
        # 获取question的ngram
        question_ngrams = []
        for q in question:
            q_ngram = [self.get_ngram(q, n=x) for x in [2,3,4]]
            q_ngrams = [x for line in q_ngram for x in line]
            question_ngrams.append(q_ngrams)
        # 计算相似度
        score = []
        for i,x in enumerate(question_ngrams):
            s = self.compute_jaccard(query_ngrams, x)
            score.append([i, s])
        # 排序
        score_sort = sorted(score, key=lambda x: x[1], reverse=True)[:topk]
        return score_sort




