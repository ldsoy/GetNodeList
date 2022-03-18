import json
import pandas as pd
import requests
import warnings

'''
运行环境:python 3.6以上

准备工作:
1.先从Github项目上下载到最新的机场域名文件,项目地址:https://github.com/RobAI-Lab/sspanel-mining/tree/main/src/database/sspanel_hosts/classifier,下载最新的CSV文件,并重命名成domain.csv放入同级目录
2.创建一个conf的文件夹存放承载用户配置

业务流程:
1.先从CSV文件中拿到数据,这里拿到的是不需要验证就能注册机场域名
2.验证第一步这些机场域名里面有多少ret的值等于-1,也就是可能有承载用户的
3.注册
    1.登入
    2.请求{域名+/getnodelist},并检验返回的数据中的nodes_muport的如果值不是[],就说明真的存在承载用户
    3.把承载用户写入配置,写入的配置在conf文件夹下

未完成功能:自动拼接节点
'''


# 1.先从CSV文件中拿到数据,这里拿到的是不需要验证就能注册机场域名
def CSV():
    # 定义列表一会用来接收批量网址数据
    BaseUrl = []
    # 读取未处理的csv文件
    df = pd.read_csv('domain.csv')

    # 进行数据处理,筛选出label是Normal的df对象,并且只要url
    data = df['url'][df['label'] == 'Normal']

    # 把筛选出来的数据写进列表
    for i in data:
        # 要清楚这里的i不是原始的机场域名,而是注册接口,为了方便后面进行的工作,所以直接在这里进行处理,转换成原始机场域名
        i = i.split('/auth')
        i = i[0]
        BaseUrl.append(i)
    # 此处返回的是原始的域名
    print("CSV文件处理完成，已经拿到机场域名，接下来开始验证ret的值")
    return BaseUrl


# 2.验证第一步这些机场域名里面有多少ret的值等于-1,也就是可能有承载用户的
def ret():
    # 这个retUrl这个列表是用来存放ret值验证通过的机场
    retURL = open("retURL.txt", "w", encoding="utf-8")
    # 从CSV方法返回的列表,遍历循环
    for i in CSV():
        # 请求的时候非常容易发生异常
        try:
            value = requests.get(i + '/getnodelist', timeout=5).json()["ret"]
        # 如果异常,就跳过这个域名,进行下一个
        except Exception as e:
            # 异常直接跳，就是任性，就是玩
            continue
        # 没有异常,就保存域名到retUrl列表
        else:
            if (value == -1):
                retURL.write(i + "\n")
                print(i + ' ' + 'ret值验证通过')
    retURL.close()


# 注册和登入需要的数据,随便写没验证
email = '15975328846@gmail.com'
name = 'annan'
passwd = '123456789'
repasswd = '123456789'


# 3.注册
def register():
    conf = open("conf.txt", "w", encoding="utf-8")
    # 注册成功的列表
    for i in trans("retURL.txt"):
        # 忽略所有警告
        warnings.filterwarnings("ignore")
        # 保持连接
        web_session = requests.session()
        # 请求体
        data = 'email=' + email + '&name=' + name + '&passwd=' + passwd + '&repasswd=' + repasswd + '&code=0'
        # 请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }

        # 出现异常的处理
        try:
            regMsg = web_session.post(i + '/auth/register', data, headers=headers, verify=False).json()["msg"]
        except Exception as e:
            print(f'{i} 注册异常\n')
            continue
        else:
            print(i + " " + regMsg)
            # 4.进行登入
            logindata = 'email=' + email + '&passwd=' + passwd + '&code='
            try:
                loginMsg = web_session.post(i + '/auth/login', logindata, headers=headers, verify=False).json()["msg"]
            except Exception as e:
                print(f'{i} 登入异常\n')
                continue
            else:
                print(i + " " + loginMsg)
                # 5.判断有没有承载用户
                try:
                    getenodelistMsg = web_session.get(i + '/getnodelist').json()
                except Exception as e:
                    print(f'{i} 请求getnodelist异常\n')
                    continue
                else:
                    if getenodelistMsg['nodeinfo']['nodes_muport'] == []:
                        print(f'{i} 无承载用户\n')
                    else:
                        # 有承载用户
                        print(f'{i} 有承载用户')
                        i = i.split('//')[1]
                        with open(f'./conf/{i}.json', 'w') as f:
                            try:
                                json.dump(getenodelistMsg, f, ensure_ascii=False, indent=4)
                            except Exception as e:
                                print(f"{i} 的承载用户配置写入异常\n")
                            else:
                                conf.write(i + "\n")
                                print(f'{i} 的承载用户配置已经写入完成\n')
    conf.close()


# 文件转列表函数,用来固化数据
def trans(path):
    transList = []
    tran = open(path, "r", encoding="utf-8")
    while True:
        buf = tran.readline()
        if len(buf) == 0:
            break
        else:
            buf = buf.split("\n")[0]
            transList.append(buf)
    tran.close()
    return transList



"""以下为函数控制流程"""
# 检测ret值,运行一遍就行,检测到ret=-1,就会自动保存数据到retURL.txt文件
ret()

# 开始注册登入检测程序,并保存配置到conf文件夹
register()

