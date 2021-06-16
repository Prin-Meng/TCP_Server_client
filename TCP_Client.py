import json
from socket import *


def client_json(ip, port, obj):
    # 创建TCP Socket并连接
    sockobj = socket(AF_INET, SOCK_STREAM)
    sockobj.connect((ip, port))

    send_obj = obj

    # 把obj转换为JSON字节字符串
    send_message = json.dumps(send_obj).encode()
    # 读取1024字节长度数据, 准备发送数据分片
    send_message_fragment = send_message[:1024]
    # 剩余部分数据
    send_message = send_message[1024:]

    while send_message_fragment:
        sockobj.send(send_message_fragment)  # 发送数据分片（如果分片的话）
        send_message_fragment = send_message[:1024]  # 读取1024字节长度数据
        send_message = send_message[1024:]  # 剩余部分数据


if __name__ == '__main__':
    # 使用Linux解释器 & WIN解释器
    port = 6666

    # 执行命令
    exec_cmd = {'status': True, 'jingdu': '66', 'weidu': '77'}
    client_json('192.168.0.105', port, exec_cmd)
