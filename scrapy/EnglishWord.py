from bs4 import BeautifulSoup as bs

import requests

class Const:
    count = 0
    EW_PATH = '../pdca/gain/EnglishWords'
    DOLIST = list()
    ERRLIST = list()

    @classmethod
    def init_data(cls):
        with open(Const.EW_PATH, 'r') as f:
            for line in f:
                k = line.split(':')[0].strip()
                if k:
                    Const.DOLIST.append(k)

def core(query_word):
    form = {'q': query_word}
    rs = requests.get('http://cn.bing.com/dict/', params = form)
    soup = bs(rs.content)
    denote = soup.find_all(class_ = 'def')
    print('*'*70)
    for item in denote:
        print(item.text)
    Const.count += 1
    in_text = input('[{}]: '.format(Const.count))
    if check_value(in_text, query_word):
        print('holy shit!')
        if query_word in Const.ERRLIST:
            Const.ERRLIST.remove(query_word)
    else:
        print('no, the right answer is {}'.format(query_word))
        Const.ERRLIST.append(query_word)
    print('*'*70)
    print()

def check_value(answer, fact):
    if answer.strip().upper() == fact.upper():
        return True
    return False

def menu2():
    for item in set(Const.DOLIST):
        core(item)
    while len(Const.ERRLIST) > 0:
        for item in Const.ERRLIST:
            core(item)

def loopInput():
    def dis_menu():
        print('='*60 + '\n1. 英->汉\n2. 汉->英\n' + '='*60)

    Const.init_data()
    dis_menu()
    while 1: 
        in_text = input('>>> ')
        if in_text.strip() == 'exit':
            break
        elif in_text.strip() == 'menu':
            dis_menu()
        elif in_text.strip() == '1':
            print('not supported yet!')
        elif in_text.strip() == '2':
            menu2()
        else:
            print('no such an item, please input again!')

if __name__ == '__main__':
    loopInput()
