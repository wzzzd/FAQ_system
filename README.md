# FAQ

FAQ智能问答系统

使用多种方法，实现FAQ的问题-模板匹配功能。

使用Tornado框架，部署成轻量级的Web服务应用。

整体框架如下。

<img src=./img/structure.jpg width=100% />


## 流程
- 1.初始化流程
```
1.读取QA数据集
2.创建Elasticsearch的index索引
3.将QA语料导入Elasticsearch
```

- 2.查询流程
```
输入query文本 -> 分词 -> 召回（ES） -> 粗序（PreRank） -> 精排（Rank） -> result
```

## 方法

### 1. 召回
- 目的：尽可能多地召回与query相关的问题
- 使用[jieba](https://github.com/fxsjy/jieba)分词
- 基于分词，获取Elasticsearch中相关的问题模板候选集

### 2. 排序
- 目的：使用基于字符或向量的方法，召回结果进行排序，用比较快的速度完成初筛，减少精排的数据量。
- BM25
     - 基于`BM25`的思路，计算query与候选数据集之间的得分，作为排序分数。
- N-gram
     - 使用`2-gram`、`3-gram`、`4-gram`提取词片段，再使用`jaccard`计算相似度，作为排序分数。
- Word2Vec
     - 提供了两种获取词向量的方法：
          - (1) 使用本项目的QA数据集作为语料，基于`gensim`框架训练得到的`word2vec`模型。
          - (2) 使用腾讯AI Lab开源的词向量[Embedding](https://ai.tencent.com/ailab/nlp/en/embedding.html)。需要将文件放置在目录`file/model/`下。项目默认使用【Original size: 1.8G; tar.gz size: 763M】的词向量，若使用其他词向量文件，需要修改`Config.py`下的`path_w2v_tx`变量值。
     - 计算词向量之间的相似度，作为排序分数。

### 3. 精排
- 目的：基于无监督或有监督的方法，对粗排结果进行再排序。
#### 3.1 基于无监督方法
- Language Model
     - 使用开源预训练模型，原因是模型较小，消耗资源少。
     - 基于框架`sentence-transformers`，Base model为[MiniLM](https://huggingface.co/microsoft/MiniLM-L12-H384-uncased)，使用的模型参数为[all-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L12-v2)。
- SimCSE
     - 为了利用垂直领域的业务数据，基于指定语料，使用无监督的方法训练语言模型。
     - 使用[SimCSE](https://github.com/princeton-nlp/SimCSE)的无监督训练方法，使用本项目中的FAQ数据集进行训练。
     - 说明：基于Bert，使用对比学习的方法，来fine-tune模型。原理是，在超球面上，拉近语义层面相似的句子，同时尽可能地使语义不相似的句子相互远离。
#### 3.2 基于监督方法
- Bert
     - 垂直领域使用有监督的方法（分类模型的思路），训练一个排序模型，提升精排的准确率。
     - 可参考本人另一个项目[text_classifier_pytorch](https://github.com/wzzzd/text_classifier_pytorch)
     - 训练语料使用句子对的形式，学习目标是两个句子相似与否，即分类任务。
```
给出句子
sentence1: 车子不小心刮花了，保险流程怎么办？
sentence2: 不小心刮花车子了，怎么走保险流程？
label: 1（语义相同）

转化为
input: 车子不小心刮花了，保险流程怎么办？[SEP]不小心刮花车子了，怎么走保险流程？
label: 1
```




## 数据集

1.保险行业语料
- 来自项目[baoxianzhidao_filter](https://github.com/SophonPlus/ChineseNlpCorpus/blob/master/datasets/baoxianzhidao/intro.ipynb)
- 根据`is_best=1`筛选出回答正确的数据，获取其中的`title`和`reply`字段，处理成两个数据集，位于目录`data/insurance_zhidao_test/`下
     - `corpus.txt`: 语料库，包含`question`和`answer`两个字段。
          - `question`：与原始文件的`title`字段对应
          - `answer`：与原始文件的`reply`对应。
     - `test.txt` : 测试数据，包含`query`和`question`两个字段。
          - `question`：根据`question`字段使用回译的方法（中->英->中），获取语义相同但表述不同的句子。
          - `answer`：表示原始问题的标准答案。

          
2.自定义语料
- 可按照上述数据集的格式，使用自定义的数据。注意，需要包含两个文件`corpus.txt`和`test.txt`。




## 环境说明
本项目基于python==3.8实现。
若安装了anaconda，建议创建一套虚拟环境，再安装环境依赖
```
$ conda create -n your_env_name python=3.8   # 创建虚拟环境
$ conda activate your_env_name               # 激活环境
$ pip install -r requirements.txt            # 安装依赖
```
若无安装anaconda，直接安装依赖
```
$ pip install -r requirements.txt
```

另外，为了在语料较大的情况下，减少召回模块消耗的时间，本项目使用Elasticsearch分布式搜索引擎来存储所有的语料。使用版本为（[7-10-2](https://www.elastic.co/cn/downloads/past-releases/elasticsearch-7-10-2)）。

按照完毕后，启动ES服务
```
cd /your_path/elasticsearch-7.10.2/bin;
./elasticsearch -d;
```

## 效果

### 1.示例
在模型配置，粗排方法为bm25，精排方法为有监督的bert方法下，部分效果如下：

> Query：重疾险有年龄限制吗？
> 
> PreRank：
> - question:商业养老保险是否有投保年龄限制  - score:12.33
> - question:康惠保重疾险是所有人都可以买吗？对年龄有什么限制？  - score:9.42
> - question:重疾险对购买人年龄有没有要求？  - score:9.01
> - question:多大年龄开始购买重疾险比较好？  - score:9.01
> - question:哆啦A保对年龄有没有限制，10岁的小女孩可以买吗  - score:7.74
> - question:交强险有报案时间限制吗  - score:7.38
> - question:生育险报销有时间限制吗  - score:7.00
> - question:生育险到账有时间限制去取吗  - score:6.66
> - question:有商业保险可年龄大可以贷款吗  - score:6.51
> - question:16周岁的孩子买人身保险有什么限制吗  - score:6.07
> 
> Rank:
> - question:重疾险对购买人年龄有没有要求？  - score:0.98
> - question:有年交2000块的重疾险吗  - score:0.94
> - question:康惠保重疾险是所有人都可以买吗？对年龄有什么限制？  - score:0.76
> - question:多大年龄开始购买重疾险比较好？  - score:0.69
> - question:缴费年限是什么？  - score:0.53
> - question:重大疾病保险有必要买吗？  - score:0.52
> - question:重疾险有多少种疾病  - score:0.50

### 2.指标
在100个样本的测试集中，分别统计top1、top3、top10的召回结果准确率。
| 粗排模型 | 精排模型 | Top1 Acc | Top3 Acc | Top10 Acc |
| :-----| :---- | :---- | :---- | :---- |
| bm25 | - | 0.77 | 0.86 | 0.92 |
| ngram | - | 0.52 | 0.69 | 0.84 |
| word2vec(tencent) | - | 0.76 | 0.83 | 0.88 |
| bm25 | lm-mini(Unsup) | 0.45 | 0.54 | 0.64 |
| bm25 | simcse-bert(Unsup) | 0.43 | 0.51 | 0.61 |
| bm25 | bert(sup) | 0.99 | 1.0 | 1.0 |



## 使用方式
### 1.配置文件
根目录下的`Config.py`文件，是配置文件。可自行修改相关的参数：
- `es_ip`：ES搜索引擎的地址，默认是部署在同一台设备环境里，如果ES是部署在其他服务器，那么需要改成其他服务器的地址。
- `es_index`：表示语料存储在ES中的index名字。
- `model_name`：表示排序的方法，分别包含`bm25/ngram/word2vec/word2vec-tx`。
- `dataset`：表示数据集的名称，对应目录`./data/`下的数据文件夹名。
- `use_rank`：是否使用精排模块。True开启，False关闭。
- `use_supervise`：精排模块使用有监督方法，还是无监督方法。True为监督方法，False为无监督方法。
- `unsup_rank_name`：表示无监督精排中，使用的模型类型，可选：`simcse-distilbert/simcse-bert/lm-mini`
- `sup_rank_name`：表示监督方法精排中，使用的模型类型，可选：`distilbert/bert`


### 2.项目初始化
考虑到性能问题，原始的数据会被存储到Elasticsearch。
在开始以下Demo之前，需要将加工数据，并存储到ES。
```
$ python insert_data_to_es.py
```


### 3.训练有监督的排序模型（可选）
若配置文件`config.py`中，字段`use_supervise=True`，则表示在rank阶段，使用有监督的方法来实现。
那么就需要提前训练好一个rank模型。
本项目提供了已经处理好的保险行业rank数据集，可参考
```
└── data
     └── insurance_zhidao_rank
          ├── train.txt
          ├── dev.txt
          └── test.txt
```
模型方面，选了本人另一个项目[text_classifier_pytorch](https://github.com/wzzzd/text_classifier_pytorch)中的bert模型来完成排序任务。
可直接将本数据集，替换掉该项目的数据集，再进行训练，即可得到排序模型。

若想直接使用本数据集训练的模型参数，可直接下载模型文件[rank-bert](https://pan.baidu.com/s/1B51WcVrjxRRRPVcqg4-dwg)，密码:tal1。并将下载的所有文件（非文件夹）放在目录`file/supervise/bert/`下。


### 4.训练无监督的语义表征模型SimCSE（可选）
若配置文件`config.py`中，字段`use_supervise=False`，则表示在rank阶段，使用有无监督的方法来实现。字段`unsup_rank_name=simcse-bert`时，表示使用SimCSE训练的预训练模型来进行句子语义提取。

具体的无监督SimCSE模型及训练，可参考论文源码[SimCSE](https://github.com/princeton-nlp/SimCSE)。

本项目提供了已经处理好的保险行业的无监督训练数据集，可参考`data/insurance_zhidao_unsup/corpus.txt`

若想直接使用本数据集训练的模型参数，可直接下载模型文件[simcse-unsup-bert]()，密码:。并将下载的所有文件（非文件夹）放在目录`file/unsupervise/simcse_bert/`下。


### 5.FAQ问答
直接测试FAQ效果
```
$ python FAQ.py
```


### 6.部署FAQ问答服务
可以将FAQ部署成一个Web服务。

**Step1：启动FAQ问答Web服务。**
```
$ python service.py
```

**Step2：以http的方式访问FAQ问答Web服务。**

可在linux shell命令行下，发送http请求，其中参数说明
- `data` 里面包含了两个参数
- `question` 表示输入的问题
- `size` 表示返回的结果数量，返回结果不一定与输入的size值一致，但是返回结果长度会小于或等于size值。

```
$ curl --request POST \
  --url http://localhost:5000/api/v1/faq/ \
  --header 'content-type: application/json' \
  --data '{"question": "什么是综保保险？","size": 3}'
```
结果会按照相似得分倒序排序，服务会返回类似以下的结果格式：
```
{
    "status": 200,
    "answer": [
        {
            "question": "综保是什么保险",
            "answer": "综合保险是为了维护外来从业人员的合法权益，规范单位用工行为，维护劳动力市场秩序。综合保险包括工伤（或者意外伤害）、住院医疗和老年补贴等三项保险待遇。外来从业人员在参加综合保险期间发生工伤事故或患职业病的，可以得到一次性支付的工伤保险金...",
            "score": "0.98"
        },
        {
            "question": "什么是万能型保险？",
            "answer": "万能型保险是指包含保险保障功能并至少在一个投资账户拥有一定资产价值的人身保险产品。万能型保险除了同传统寿险一样给予保护生命保障外，还可以让客户直接参与由保险公司为投保人建立的投资帐户内资金的投资活动，将保单的价值与保险公司独立运作的投保人投资帐户资金的业绩联系起来...",
            "score": "0.97"
        },
        {
            "question": "保险到底是什么？",
            "answer": "保险是指投保人根据合同约定，向保险人支付保险费，保险人对于合同约定的可能发生的事故因其发生所造成的财产损失承担赔偿保险金责任，或者被保险人死亡、伤残、疾病或者达到合同约定的年龄、期限等条件时承担给付保险金责任的商业保险行为...",
            "score": "0.96"
        }
    ]
}
```
说明
- 此服务部署方式只支持同一台设备的网络访问。
- 若想通过其他设备来访问此Web服务，需要额外配置对外开放相关端口，或者接入流量转发器（如nginx）进行请求的转发。



## 更新日志

| 更新时间 | 版本号 | 说明 |
| :-----| :---- | :---- |
| 2023-01-05 | V1.0 | 项目初始化，主要包含召回+排序的算法框架，以及Web服务 |
| 2023-01-17 | V1.1 | 算法框架修改为：召回+粗排+精排；新增精排的supervise方法；在粗排方法中，引入外部词向量 |
| ... | ... | ... |

