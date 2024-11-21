from collections import deque
import socket
from threading import Thread
import json

from execution_engine import ExecutionEngine
from transaction import Transaction
from utxo import Utxo

class FullNode():
    HOST = '127.0.0.1'
    PORT = 9999

    def __init__(self, transactions :deque, utxo_set :deque):
        self.transactions = transactions
        self.utxo_set = utxo_set
        self.query_queue = deque()
        self.processed_tx = []

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
        # 1. tx fetch
        now_tx :Transaction = self.transactions.popleft()
        # 2. get tx's utxo from utxo set
        utxo :Utxo = now_tx.input_transaction
        if not self.__check_utxo_is_contained(utxo):
            raise Exception("utxo set에 없는 utxo")
        # 3. input amount >= sum(output amount)
        input_amount = now_tx.input_transaction.amount
        output_amount_sum = sum([output_amount for output_amount, locking_script in now_tx.output])
        if input_amount < output_amount_sum:
            raise Exception("올바르지 않은 amount 데이터")
        # 4. check tx's unlocking script can unlock the locking script in utxo (연산결과 true하나만 남아야)
        ee = ExecutionEngine()
        ee.calculate(now_tx)
        # 5. utxo set 에 기존 input utxo 제거, output 들을 utxo로 추가

    def __check_utxo_is_contained(self, utxo :Utxo):
        for check_utxo in self.utxo_set:
            if utxo.txid == check_utxo.txid and utxo.output_index == check_utxo.output_index:
                return True

        return False


transaction_dict = json.load(open('data/transaction.json'))
utxo_dict = json.load(open('data/utxo.json'))
transaction_set = deque(map(lambda json_dict:Transaction(json_dict), transaction_dict))
utxo_set = deque(map(lambda json_dict:Utxo(json_dict), utxo_dict))
print(transaction_set)
print(utxo_set)

node = FullNode(transaction_set, utxo_set)
node.run()