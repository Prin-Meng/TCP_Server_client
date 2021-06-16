import json
from socket import *


def server_json(ip, port):
    # 创建TCP Socket, AF_INET为IPv4，SOCK_STREAM为TCP
    sockobj = socket(AF_INET, SOCK_STREAM)
    # 允许socket端口复用
    sockobj.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    # 绑定套接字到地址，地址为（host，port）的元组
    sockobj.bind((ip, port))
    # 在拒绝连接前，操作系统可以挂起的最大连接数量，一般配置为5
    sockobj.listen(5)

    while True:  # 一直接受请求，直到ctl+c终止程序
        try:
            # 接受TCP连接，并且返回（conn,address）的元组，conn为新的套接字对象，可以用来接收和发送数据，address是连接客户端的地址
            connection, address = sockobj.accept()
            # conn.settimeout(5.0)  # 设置连接超时!
            # 打印连接客户端的IP地址
            print('Server Connected by', address)
            recieved_message = b''  # 预先定义接收信息变量
            recieved_message_fragment = connection.recv(1024)  # 读取接收到的信息，写入到接收到信息分片
            if len(recieved_message_fragment) < 1024:  # 如果长度小于1024!表示客户发的数据小于1024!

                recieved_message = recieved_message_fragment
                obj = json.loads(recieved_message.decode())  # 把接收到信息json.loads回正常的obj

            else:
                while len(recieved_message_fragment) == 1024:  # 等于1024表示还有后续数据!
                    recieved_message = recieved_message + recieved_message_fragment  # 把接收到信息分片重组装
                    recieved_message_fragment = connection.recv(1024)  # 继续接收后续的1024的数据
                else:
                    recieved_message = recieved_message + recieved_message_fragment  # 如果数据小于1024!拼接最后数据
                obj = json.loads(recieved_message.decode())  # 把接收到信息json.loads回正常的obj
            if obj.get('state'):
                info = {'jingdu': obj['jingdu'], 'weidu': obj['weidu']}

            connection.close()

        except Exception as e:
            print(e)


if __name__ == '__main__':
    # 使用Linux解释器 & WIN解释器
    server_ip = '0.0.0.0'
    server_port = 6666
    server_json(server_ip, server_port)
