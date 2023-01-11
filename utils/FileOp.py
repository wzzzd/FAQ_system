

class File(object):


    def __init__(self):
        pass

    def write(sel, text, path):
        with open(path, 'a', encoding='utf8') as f:
            f.write(text+'\n')
            
