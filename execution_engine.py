import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed

from test.test_data import str_to_byte
from transaction import Transaction


class ExecutionEngine:
    def __init__(self):
        self.__script_list = []
        self.__stack = []
        pass

    def calculate(self, tx :Transaction, script:str):
        print(script)
        self.__tx: Transaction = tx
        self.__script_list = ['OP_CHECKFINALRESULT'] + list(reversed(script.split()))
        print(self.__script_list)
        self.__stack = []
        while len(self.__script_list):
            token = self.__script_list.pop()
            if self.__is_op(token):
                self.__operate(token)
            else:
                self.__stack.append(token)
            print(self.__stack)


    def __is_op(self, token: str):
        return token.startswith('OP_')


    def __operate(self, op: str):
        op = op[3:]
        if op == 'DUP':
            self.__DUP()
        elif op == 'HASH':
            self.__HASH()
        elif op == 'EQUAL':
            self.__EQUAL()
        elif op == 'EQUALVERIFY':
            self.__EQUALVERIFY()
        elif op == 'CHECKSIG':
            self.__CHECKSIG()
        elif op == 'CHECKSIGVERIFY':
            self.__CHECKSIGVERIFY()
        elif op == 'CHECKMULTISIG':
            pass
        elif op == 'CHECKMULTISIGVERIFY':
            pass
        elif op == 'IF':
            pass
        elif op == 'CHECKFINALRESULT':
            self.__CHECKFINALRESULT()
        else:
            raise Exception("존재하지 않는 OP 명령어")


    def __DUP(self):
        if not self.__stack:
            raise Exception("DUP : 스택에 원소가 없습니다.")
        data = self.__stack.pop()
        self.__stack.append(data)
        self.__stack.append(data)


    def __HASH(self):
        if not self.__stack:
            raise Exception("HASH : 스택에 원소가 없습니다.")
        data = self.__stack.pop()
        hashed_data = self.__hash(data)
        self.__stack.append(hashed_data)


    def __EQUAL(self):
        if len(self.__stack) < 2:
            raise Exception("EQUAL : 스택에 원소가 2개 미만입니다.")
        data1 = self.__stack.pop()
        data2 = self.__stack.pop()
        if data1 == data2:
            self.__stack.append("TRUE")
        else:
            self.__stack.append("FALSE")


    def __EQUALVERIFY(self):
        if len(self.__stack) < 2:
            raise Exception("EQUALVERIFY : 스택에 원소가 2개 미만입니다.")
        data1 = self.__stack.pop()
        data2 = self.__stack.pop()
        if data1 != data2:
            raise Exception("EQUALVERIFY : 두 원소가 다릅니다.")


    def __CHECKSIG(self):
        if len(self.__stack) < 2:
            raise Exception("CHECKIG : 스택에 원소가 2개 미만입니다.")

        pubKey = self.__stack.pop()
        signature = self.__stack.pop()
        result = self.__verify_sig(pubKey, signature)
        self.__stack.append(result)


    def __CHECKSIGVERIFY(self):
        if len(self.__stack) < 2:
            raise Exception("CHECKSIGVERIFY : 스택에 원소가 2개 미만입니다.")
        pubKey = self.__stack.pop()
        signature = self.__stack.pop()
        result = self.__verify_sig(pubKey, signature)
        if result == "FALSE":
            raise Exception("CHECKSIGVERIFY : 검증에 실패했습니다.")


    def __CHECKFINALRESULT(self):
        if len(self.__stack) != 1:
            raise Exception("CHECKFINALRESULT : 스택에 원소가 1개 남아있어야 합니다.")
        if self.__stack[-1] != "TRUE":
            raise Exception("CHECKFINALRESULT : 스택에 남아있는 원소가 TRUE가 아닙니다.")


    def __hash(self, original_data:str):
        data = original_data.encode('ascii')
        digest = hashes.Hash(hashes.SHA256())
        digest.update(data)
        byte_hash = digest.finalize()
        return base64.b64encode(byte_hash).decode('ascii')


    def __verify_sig(self, pub_key :str, signature :str):
        try:
            pubKey_byte = str_to_byte(pub_key)
            signature_byte = str_to_byte(signature)
            pubKey = serialization.load_der_public_key(pubKey_byte)
            tx_hash = self.__hash(str(self.__tx))
            tx_hash_byte = str_to_byte(tx_hash)
            print(self.__tx, tx_hash)
            pubKey.verify(signature_byte, tx_hash_byte, ec.ECDSA(Prehashed(hashes.SHA256())))
            return "TRUE"
        except Exception as e:
            return "FALSE"

    def __byte_to_str(self, data: bytes):
        return base64.b64encode(data).decode('ascii')

    def __str_to_byte(self, data: str):
        return base64.b64decode(data.encode('ascii'))