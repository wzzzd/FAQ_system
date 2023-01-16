

from sentence_transformers import SentenceTransformer, util




class LMEmbedding(object):

    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L12-v2')


    # def get_sentence_embedding(self, text):
    #     query_embedding = self.model.encode(text)
    #     # passage_embedding = self.model.encode([
    #     #                             '你叫什么名字',
    #     #                             '这名字怎么样',
    #     #                             '嘟嘟是你的名字',
    #     #                             '你猜我叫什么名字',
    #     #                             '我老公叫什么名字']
    #     #                             )
    #     # print("Similarity:", util.dot_score(query_embedding, passage_embedding))
    #     return query_embedding[0]

    def to(self, device):
        """
        模型加载到cuda
        """
        self.model.to(device)

    
    def get_embedding(self, text):
        """获取文本语义编码
        Args:
            text (string): 输入文本
        Returns:
            _type_: _description_
        """
        emb = self.model.encode(text)
        # emb = query_embedding[0]
        return emb

    
    def compute_similarity(self, query, corpus):
        """计算文本与语料库的相似度
        Args:
            query (_type_): _description_
            corpus (_type_): _description_
        """
        query_emb = self.model.encode(query)
        corpus_emb = self.model.encode(corpus)
        matrix = util.dot_score(query_emb, corpus_emb)
        flat = matrix.view(-1).cpu().tolist()
        flat = [[i,x] for i,x in enumerate(flat)]
        scores_rank = sorted(flat, key=lambda x: x[1], reverse=True)
        return scores_rank

    
    


if __name__ == '__main__':
    emb = LMEmbedding()
    text = '你叫什么名字'
    vec = emb.get_sentence_embedding(text)
    print(1)
