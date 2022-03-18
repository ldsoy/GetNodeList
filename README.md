# GetNodeList

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
