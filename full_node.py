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
        if not self.transactions:
            return

        now_tx :Transaction = self.transactions.popleft()
        utxo :Utxo = self.__get_utxo(now_tx.input.ptxid, now_tx.input.output_index)

        self.__validate_amount(now_tx, utxo)
        self.__validate_script(now_tx, utxo)

        self.__remove_utxo(utxo)
        self.__add_utxo_from_outputs(now_tx)

        self.processed_tx.append(now_tx)


    def __check_utxo_is_contained(self, utxo :Utxo):
        for check_utxo in self.utxo_set:
            if utxo.txid == check_utxo.txid and utxo.output_index == check_utxo.output_index:
                return True

        return False

    def __remove_utxo(self, utxo:Utxo):
        for check_utxo in self.utxo_set:
            if utxo.txid == check_utxo.txid and utxo.output_index == check_utxo.output_index:
                self.utxo_set.remove(check_utxo)
                return

    def __get_utxo(self, ptxid:str, output_index:int):
        for utxo in self.utxo_set:
            if utxo.txid == ptxid and utxo.output_index == output_index:
                return utxo
        raise Exception("utxo set에 없는 utxo")

    def __validate_amount(self, tx, utxo):
        input_amount = utxo.amount
        output_amount_sum = sum([output_amount for output_amount, locking_script in tx.output])
        if input_amount < output_amount_sum:
            raise Exception("올바르지 않은 amount 데이터")

    def __validate_script(self, tx, utxo):
        try:
            ee = ExecutionEngine()
            input_script = tx.input.unlocking_script
            output_script = utxo.locking_script
            script = input_script + " " + output_script
            ee.calculate(tx, script)
            self.__print_script_validation_result(tx, "passed")
        except Exception as e:
            msg = str(e)
            self.__print_script_validation_result(tx, "failed")

    def __add_utxo_from_outputs(self, tx):
        for i in range(len(tx.output)):
            amount, locking_script = tx.output[i]
            new_utxo:Utxo = Utxo({
                "txid": "txid",
                "output_index": i,
                "amount": amount,
                "locking_script": locking_script
            })
            self.utxo_set.append(new_utxo)

    def __print_script_validation_result(self, tx, result, failed_command=None):
        print(f"transaction: {'txid'}")
        print(f"\tinput")
        for i in range(len(tx.output)):
            print(f"\toutput:{i}")
        print(f"\tvalidity check: {result}")
        if result == "failed":
            print(f"failed at {failed_command}")


transaction_dict = json.load(open('data/transaction.json'))
utxo_dict = json.load(open('data/utxo.json'))
transaction_set = deque(map(lambda json_dict:Transaction(json_dict), transaction_dict))
utxo_set = deque(map(lambda json_dict:Utxo(json_dict), utxo_dict))
print(transaction_set)
print(utxo_set)

node = FullNode(transaction_set, utxo_set)
node.run()