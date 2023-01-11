import numpy as np
import Levenshtein


def jaccard(query, target, d='query'):
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
        div_set = set(query).union(set(target))
        div = max(len(div_set), 1)
    score = len(inter) / div
    return score



def cosine(query, target):
    """
    余弦相似度
    Arg:
        query: List(Float)
        target: List(Float)
    """
    query = np.array(query)
    target = np.array(target)
    dot = float(np.dot(query, target))
    norm = np.linalg.norm(query)*np.linalg.norm(target)
    sim = dot / max(norm, 1)
    # score = 1 - sim
    return sim



def Levenshtein_distance(query, target):
    """
    编辑距离: 描述由一个字串转化成另一个字串最少 的操作次数，在其中的操作包括：插入、删除、替换。
    Arg:
        query: String
        target: String
    """
    score = Levenshtein.distance(query, target)
    return score


def Levenshtein_hamming(query, target):
    """
    汉明距离: 描述两个等长字串之间对应位置上不同字符的个数。
    Arg:
        query: String
        target: String
    """
    score = Levenshtein.hamming(query, target)
    return score




if __name__ == '__main__':
    q = ['你', '叫', '什么', '名字'] 
    # a = ['你', '叫', '什么', '名字'] 
    a = ['什么'] 
    score = jaccard(q, a)
    print(score)
