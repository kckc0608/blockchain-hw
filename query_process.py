import socket

class QueryProcess:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('127.0.0.1', 9999))
        pass

    def run(self):
        while True:
            cmd = input(">> ")
            tokens = list(map(lambda token: token.strip(), cmd.split()))

            if len(tokens) == 1:
                if tokens[0] == 'exit':
                    break

            if len(tokens) == 2:
                if tokens[0] == 'snapshot':
                    if tokens[1] == 'transactions':
                        self.client_socket.send(bytes(tokens[0], 'utf-8'))
                        data = self.client_socket.recv(1024)
                        print(data)
                        continue
                    if tokens[1] == 'utxoset':
                        self.client_socket.send(bytes(tokens[0], 'utf-8'))
                        data = self.client_socket.recv(1024)
                        print(data)
                        continue

            print("알 수 없는 명령어 입니다.")

process = QueryProcess()
process.run()