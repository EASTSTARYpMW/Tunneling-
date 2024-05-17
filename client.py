import socket
import threading
import queue
#客户端

ip = 'Your Ip Address Here'
port = 7777
host_q = queue.Queue()
remote_q = queue.Queue()

def recv_remote(remote_sock):
    print("进入remote线程")
    threading.Thread(target=send_remote,args=(remote_sock,)).start()
    while True:
        try:
            stream_info = remote_sock.recv(1024)
            print(f'client:{stream_info}')
            remote_q.put(stream_info)
        except Exception:
            break
    connect_remote()

def recv_local(local_sock):
    try:
        global exit_flag
        exit_flag = 1
        print("进入local线程")
        send_thread = threading.Thread(target=send_local,args=(local_sock,))
        send_thread.start()
        while True:
            stream_info = local_sock.recv(1024)
            if not stream_info:
                exit_flag = 0
                print("检测到Local离线，正在断开线程")
                send_thread.join()
                local_sock.close()
                return
            print(f'local:{stream_info}')
            host_q.put(stream_info)
    except Exception:
        exit_flag = 0
        send_thread.join()
        local_sock.close()
        return

def send_local(local_sock):
    global exit_flag
    print("进入local发送线程")
    while True:
        if not exit_flag:
            return
        info = remote_q.get()
        if info:
            local_sock.sendall(info)

def send_remote(remote_sock):
    print("进入remote发送线程")
    while True:
        info = host_q.get()
        if info:
            remote_sock.sendall(info)

def connect_local(local_port):
    while True:
        try:
            local_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            local_sock.connect(('127.0.0.1',local_port))
            print("与本地服务连接成功")
            recv_local(local_sock)
        except Exception:
            continue

def connect_remote():
    while True:
        remote_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        remote_sock.connect((ip,port))
        print("与服务端连接成功")
        recv_remote(remote_sock)

if __name__ == '__main__':
    #Enter your local port.
    local_port = int(input('>>>'))
    threading.Thread(target=connect_local,args=(local_port,)).start()
    threading.Thread(target=connect_remote).start()

