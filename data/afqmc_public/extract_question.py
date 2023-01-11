
import os
import json
import pandas as pd


def main():
    
    # 读取数据
    path = './data/afqmc_public/'
    data = []
    for file in ['train.json', 'dev.json']:
        tmp_path = path + file
        with open(tmp_path, 'r', encoding='utf8') as f:
            for line in f.readlines():
                line = eval(line)
                data.append(line)

    # 获取标签为1的数据
    target = [x for x in data if x['label']=='1']
    target = pd.DataFrame(target)
    target = target[['sentence1', 'sentence2']]
    target.columns = ['question', 'module']
    target.to_csv('./data/afqmc_public/module.csv', sep='\t', index=False)
    a = 1




if __name__ == '__main__':
    main()
