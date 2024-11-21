import base64
from collections import deque
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import json

from cryptography.hazmat.primitives import hashes

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
                self.__process_query(*query)
                # send response
                continue
            self.__process_transaction()


    def __set_socket(self):
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind((self.HOST, self.PORT))


    def __get_query(self):
        self.server_socket.listen()
        while True:
            client_socket, addr = self.server_socket.accept()
            data = str(client_socket.recv(1024), encoding='utf-8')
            self.query_queue.append((client_socket, addr, data))
            print("receive query")


    def __process_query(self, client_socket, addr, data):
        if data == "transactions":
            response = ""
            for txid, result in self.processed_tx:
                response += f"transaction: {txid}, validity check: {result}\n"
            client_socket.send(response.encode('utf-8'))
            return

        if data == "utxoset":
            response = "utxoset not yet"
            client_socket.send(response.encode('utf-8'))
            return

        response = f"{data} 는 처리할 수 없는 쿼리"
        client_socket.send(response.encode('utf-8'))


    def __process_transaction(self):
        if not self.transactions:
            return

        now_tx :Transaction = self.transactions.popleft()
        utxo :Utxo = self.__get_utxo(now_tx.input.ptxid, now_tx.input.output_index)

        self.__validate_amount(now_tx, utxo)
        result = self.__validate_script(now_tx, utxo)

        self.__remove_utxo(utxo)
        self.__add_utxo_from_outputs(now_tx)

        self.processed_tx.append((self.__hash(str(now_tx)), result))


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
        result = "failed"
        try:
            ee = ExecutionEngine()
            input_script = tx.input.unlocking_script
            output_script = utxo.locking_script
            script = input_script + " " + output_script
            ee.calculate(tx, script)
            result = "passed"
            self.__print_script_validation_result(tx, result)
        except Exception as e:
            command = str(e).split(":")[0]
            self.__print_script_validation_result(tx, result, command)
        finally:
            return result

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
        print(f"transaction: {self.__hash(str(tx))}")
        print(f"\tinput")
        for i in range(len(tx.output)):
            print(f"\toutput:{i}")
        print(f"\tvalidity check: {result}")
        if result == "failed":
            print(f"\t\t\t\t\tfailed at {failed_command}")

    def __hash(self, original_data: str):
        data = original_data.encode('ascii')
        digest = hashes.Hash(hashes.SHA256())
        digest.update(data)
        byte_hash = digest.finalize()
        return base64.b64encode(byte_hash).decode('ascii')


transaction_dict = json.load(open('data/transaction.json'))
utxo_dict = json.load(open('data/utxo.json'))
transaction_set = deque(map(lambda json_dict:Transaction(json_dict), transaction_dict))
utxo_set = deque(map(lambda json_dict:Utxo(json_dict), utxo_dict))

node = FullNode(transaction_set, utxo_set)
node.run()