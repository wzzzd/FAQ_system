
import json
import pandas as pd


def main():
    path = './data/insuranceqa/train.json'
    train = load(path)
    path = './data/insuranceqa/test.json'
    test = load(path)
    path = './data/insuranceqa/valid.json'
    valid = load(path)

    path = './data/insuranceqa/answers.json'
    answer = load(path)

    mapping_answer = {}
    for k,v in answer.items():
        mapping_answer[k] = v['zh']

    train_set = []
    for index,line in train.items():
        question = line['zh']
        answer = line['answers']
        module = []
        for x in answer:
            tmp = mapping_answer[x]
            module.append(tmp)
        module = '###'.join(module)
        train_set.append([question, module])

    valid_set = []
    for index,line in valid.items():
        question = line['zh']
        answer = line['answers']
        module = []
        for x in answer:
            tmp = mapping_answer[x]
            module.append(tmp)
        module = '###'.join(module)
        valid_set.append([question, module])

    test_set = []
    for index,line in test.items():
        question = line['zh']
        answer = line['answers']
        module = []
        for x in answer:
            tmp = mapping_answer[x]
            module.append(tmp)
        module = '###'.join(module)
        test_set.append([question, module])

    
    data = train_set + valid_set + test_set
    df = pd.DataFrame(data, columns=['question', 'module'])
    df.to_csv('./data/insuranceqa_test/corpus.txt', sep='\t', index=False)

    df = pd.DataFrame(test_set, columns=['question', 'module'])
    df.to_csv('./data/insuranceqa_test/test.txt', sep='\t', index=False)

    a=1




def load(path):
    with open(path, 'r', encoding='utf8') as f:
        log = json.load(f)
    return log




if __name__=='__main__':
    main()

