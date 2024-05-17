import socket
import threading
import queue
#服务端
#7860/1314对外
#7777对内

host_q = queue.Queue()
client_q = queue.Queue()

def recv_client(client_sock):
    global exit_flag
    exit_flag = 1
    print("跳转到client线程")
    send_thread = threading.Thread(target=send_client,args=(client_sock,))
    send_thread.start()
    while True:
        try:
            stream_info = client_sock.recv(1024)
            if not stream_info:
                exit_flag = 0
                print("检测到client离线，正在断开线程")
                send_thread.join()
                client_sock.close()
                return
            print(f'client:{stream_info}')
            client_q.put(stream_info)
        except Exception:
            print(Exception)
            client_sock.close()
            break
    return

def recv_host(host_sock):
    print('跳转到host线程')
    threading.Thread(target=send_host,args=(host_sock,)).start()
    while True:
        try:
            stream_info = host_sock.recv(1024)
            print(f'host\local:{stream_info}')
            host_q.put(stream_info)
        except Exception:
            print(Exception)
            host_sock.close()
            break
    return

def send_host(host_sock):
    try:
        while True:
            info = client_q.get()
            if info:
                host_sock.sendall(info)
    except Exception:
        return

def send_client(client_sock):
    global exit_flag
    try:
        while True:
            if not exit_flag:
                return
            info = host_q.get()
            if info:
                client_sock.sendall(info)
    except Exception:
        return

def connect_host():
    #Here change your server bind port which is connected by your localhost
    host_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_sock.bind(('0.0.0.0',7777))
    host_sock.listen(5)
    while True:
        sock,addr = host_sock.accept()
        print(f'Host：{addr}已经建立连接')
        threading.Thread(target=recv_host,args=(sock,)).start()

def connect_client():
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.bind(('0.0.0.0',1314))
    client_sock.listen(16)
    while True:
        sock,addr = client_sock.accept()
        print(f'client：{addr}已经建立连接')
        threading.Thread(target=recv_client,args=(sock,)).start()

if __name__ == '__main__':
    print("7860为对外端口\n7777为对内端口")
    print("服务端运行中")
    threading.Thread(target=connect_host).start()
    threading.Thread(target=connect_client).start()










