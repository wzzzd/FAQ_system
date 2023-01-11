# FAQ

FAQ问答服务

使用多种方法，实现FAQ的问题-模板匹配功能。

使用Tornado框架，部署成轻量级的Web服务应用。



## 流程
- 初始化流程
```
1.读取QA数据集
2.创建Elasticsearch的index索引
3.将QA语料导入Elasticsearch
```

- 查询流程
```
输入query文本 -> 分词 -> 召回（ES） -> 排序(Model)
```

## 方法
### 1. 召回
- 使用[jieba](https://github.com/fxsjy/jieba)分词
- 基于分词，获取Elasticsearch中相关的问题模板候选集
### 2. 排序
#### 2.1 基于无监督方法
- BM25
     - 基于BM25的思路，计算query与候选数据集之间的得分，作为排序分数。
- N-gram
     - 使用2-gram、3-gram、4-gram提取词片段，再使用jaccard计算相似度，作为排序分数。
- Word2Vec
     - 使用本项目的QA数据集作为语料，基于gensim框架训练得到的word2vec模型。
     - 计算词向量之间的相似度，作为排序分数。
- Language Model
     - 基于框架sentence-transformers，Base model为[MiniLM](https://huggingface.co/microsoft/MiniLM-L12-H384-uncased)，使用的模型参数为[all-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L12-v2)。
#### 2.2 基于监督方法
- 待补充
     - 其实就是使用分类模型的思路，训练一个排序模型。
     - 所有bert及相关变体都可以用在这个场景。
     - 可参考项目[text_classifier_pytorch](https://github.com/wzzzd/text_classifier_pytorch)


## 数据集
1.AFQMC 蚂蚁金融语义相似度 Ant Financial Question Matching Corpus
- 原始数据是一个句子pair语义相似任务的数据集。包含训练集（34334）验证集（4316）测试集（3861）。
     - 栗子：{"sentence1": "双十一花呗提额在哪", "sentence2": "里可以提花呗额度", "label": "0"}
- 本项目中，提取了所有`"label"="1"`，即在原始数据集中，被认为是语义相似的数据。将数据抽取成两个字段，分别为`question`（问题）和`module`（问题模板）。
     - 注意：原始的数据集中，标注为相似的句子pair，存在部分标注错误问题。
     - 栗子：{"question":"花呗充话费在哪个界面", "module":"在那里用花呗充值话费"}
     - 数据集：
          - `corpus.txt`: 语料库,包含`question`和`module`两个字段。
               - 包含了原始数据集中训练、验证、测试三个数据集。
          - `test.txt`: 测试数据，包含`query`和`question`两个字段。
               - `query`字段是根据`question`字段处理后的文本复述，语义相同但表述不同。
               - `question`字段表示标准问题，来自`corpus.txt`部分数据的`question`字段。

2.保险行业语料
- 来自项目[insuranceqa-corpus-zh](https://github.com/chatopera/insuranceqa-corpus-zh)
- 数据处理成两个数据集
     - `corpus.txt`: 语料库，包含`question`和`answer`两个字段。
          - 包含了原始数据集中训练、验证、测试三个数据集。
     - `test.txt` : 测试数据，包含`query`和`question`两个字段。
          - `query`字段是根据`question`字段处理后的文本复述，语义相同但表述不同。
          - `question`字段表示标准问题，来自`corpus.txt`部分数据的`question`字段。

3.自定义语料
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

另外，为了在语料较大的情况下，减少召回模块消耗的时间，本项目使用Elasticsearch分布式搜索引擎来存储所有的语料。使用版本为7-10-2。（[下载地址](https://www.elastic.co/cn/downloads/past-releases/elasticsearch-7-10-2)）




## 使用方式
### 1.配置文件
根目录下的`Config.py`文件，是配置文件。可自行修改相关的参数：
- `es_ip`：ES搜索引擎的地址，默认是部署在同一台设备环境里，如果ES是部署在其他服务器，那么需要改成其他服务器的地址。
- `es_index`：表示语料存储在ES中的index名字。
- `model_name`：表示排序的方法，分别包含`bm25`/`ngram`/`word2vec`/`lm`。
- `dataset`：表示数据集的名称，对应目录`./data/`下的数据文件夹名。


### 2.项目初始化
考虑到性能问题，原始的数据会被存储到Elasticsearch。
在开始以下Demo之前，需要将加工数据，并存储到ES。
```
$ python insert_data_to_es.py
```


### 3.FAQ问答
直接测试FAQ效果
```
$ python FAQ.py
```
部分结果可见


### 4.部署FAQ问答服务
可以将FAQ部署成一个Web服务。

**Step1：启动FAQ问答Web服务。**
```
$ python service.py
```

**Step2：以http的方式访问FAQ问答Web服务。**

可在linux shell命令行下，发送http请求，其中参数说明
- `data` 里面包含了两个参数
- `question` 表示输入的问题
- `size` 表示返回的结果数量

```
$ curl --request POST \
  --url http://localhost:5000/api/v1/faq/ \
  --header 'content-type: application/json' \
  --data '{"question": "我的花呗怎么还钱","size": 3}'
```
结果会按照相似得分倒序排序，服务会返回类似以下的结果格式：
```
{
    "status": 200,
    "answer": [
        {
            "question": "花呗怎么还款",
            "answer": "我的花呗不知道咋还款的",
            "score": "0.75"
        },
        {
            "question": "花呗怎么还呐",
            "answer": "在淘宝用花呗支付的，怎么还款",
            "score": "0.75"
        },
        {
            "question": "月底花呗怎么还",
            "answer": "怎么样用花呗还款",
            "score": "0.6"
        }
    ]
}
```
说明
- 此服务部署方式只支持同一台设备的网络访问。
- 若想通过其他设备来访问此Web服务，需要额外配置对外开放相关端口，或者接入流量转发器（如nginx）进行请求的转发。


### 5.训练有监督的排序模型
训练recall+rank框架中的有监督rank模型
```
python TrainRank.py
```

## 说明



## 更新日志

| 更新时间 | 版本号 | 说明 |
| :-----| :---- | :---- |
| 2023-01-05 | V1.0 | 项目初始化，主要包含召回+排序的算法框架，以及Web服务 |
| ... | ... | ... |

