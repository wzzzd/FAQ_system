import json


def store(data, path):
    with open(path, 'w', encoding='utf-8') as fw:
        # 将字典转化为字符串
        json_str = json.dumps(data, ensure_ascii=False)
        fw.write(json_str)
        # 上面两句等同于下面这句
        # json.dump(data,fw)


def load(path):
    with open(path,'r') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print('Error: failed to load personal file ({})'.format(path))
            data = {}
        return data


        