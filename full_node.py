from collections import deque
import socket
from threading import Thread
import json
from transaction import Transaction
from utxo import Utxo

class FullNode():
    HOST = '127.0.0.1'
    PORT = 9999

    def __init__(self, transactions, utxo_set):
        self.transactions = transactions
        self.utxo_set = utxo_set
        self.query_queue = deque()

        self.__set_socket()
        query_listening_thread = Thread(target=self.__get_query, daemon=True)
        query_listening_thread.start()


    def run(self):
        while True:
            if self.query_queue:
                query = self.query_queue.popleft()
                print(query)
                # process query
                # send response
                continue
            self.__process_transaction()


    def __set_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.HOST, self.PORT))


    def __get_query(self):
        self.server_socket.listen()
        while True:
            client_socket, addr = self.server_socket.accept()
            data = str(client_socket.recv(1024), encoding='utf-8')
            self.query_queue.append(data)
            print("receive query")

    def __process_transaction(self):

        pass


transaction_dict = json.load(open('data/transaction.json'))
utxo_dict = json.load(open('data/utxo.json'))
transaction_set = deque(map(lambda json_dict:Transaction(json_dict), transaction_dict))
utxo_set = deque(map(lambda json_dict:Utxo(json_dict), utxo_dict))
print(transaction_set)
print(utxo_set)

node = FullNode(transaction_set, utxo_set)
node.run()