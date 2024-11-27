import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed

from transaction import Transaction


class ExecutionEngine:
    def __init__(self):
        self.__script_list = []
        self.__stack = []
        pass

    def calculate(self, tx :Transaction, script:str):
        # print(script)
        self.__tx: Transaction = tx
        self.__stack = []
        script_tokens = list(reversed(script.split()))
        if not script_tokens:
            raise Exception("script is empty")

        if len(script_tokens) > 1 and script_tokens[1] == "OP_EQUALVERIFY" and script_tokens[0] == "OP_CHECKFINALRESULT": # P2SH
            op_dup_idx = script_tokens.index("OP_DUP")
            script_sig_tokens = script_tokens[op_dup_idx+1:]
            while script_sig_tokens:
                token = script_sig_tokens[-1]
                if self.__is_op(token):
                    break

                self.__stack.append(script_sig_tokens.pop())

            self.__script_list = script_tokens[:op_dup_idx+1] + [" ".join(reversed(script_sig_tokens))]
        else:
            self.__script_list = script_tokens
        # print(self.__script_list)
        while len(self.__script_list):
            token = self.__script_list.pop()
            if self.__is_op(token):
                # print(token)
                self.__operate(token)
            else:
                self.__stack.append(token)
            # print(self.__stack)


    def __is_op(self, token: str):
        return token.startswith('OP_') and ' ' not in token


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
            self.__CHECKMULTISIG()
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
        check_script = ""
        while self.__stack:
            check_script = self.__stack.pop() + " " + check_script
        self.calculate(self.__tx, check_script.strip())
        if len(self.__stack) != 1:
            raise Exception("CHECKFINALRESULT : 스택에 원소가 1개 남아있어야 합니다.")
        if self.__stack[-1] != "TRUE":
            raise Exception("CHECKFINALRESULT : 스택에 남아있는 원소가 TRUE가 아닙니다.")


    def __CHECKMULTISIG(self):
        try:
            pubkey_count = int(self.__stack.pop())
            pubkey_list = [self.__stack.pop() for _ in range(pubkey_count)]
            sig_count = int(self.__stack.pop())
            sig_list = [self.__stack.pop() for _ in range(sig_count)]
            result = self.__verify_multi_sig(pubkey_list, sig_list)
            self.__stack.append(result)

        except Exception as e:
            raise Exception("CHECKMULTISIG : " + str(e))


    def __hash(self, original_data:str):
        data = original_data.encode('ascii')
        digest = hashes.Hash(hashes.SHA256())
        digest.update(data)
        byte_hash = digest.finalize()
        return base64.b64encode(byte_hash).decode('ascii')


    def __verify_sig(self, pub_key :str, signature :str):
        try:
            pubKey_byte = self.__str_to_byte(pub_key)
            signature_byte = self.__str_to_byte(signature)
            pubKey = serialization.load_der_public_key(pubKey_byte)
            tx_hash = self.__hash(str(self.__tx))
            tx_hash_byte = self.__str_to_byte(tx_hash)
            # print(self.__tx, tx_hash)
            pubKey.verify(signature_byte, tx_hash_byte, ec.ECDSA(Prehashed(hashes.SHA256())))
            return "TRUE"
        except Exception as e:
            return "FALSE"

    def __verify_multi_sig(self, pubkey_list, sig_list):
        try:
            count = 0
            for sig in sig_list:
                for pubkey in pubkey_list:
                    result = self.__verify_sig(pubkey, sig)
                    if result == "TRUE":
                        count += 1
                        break

            if count < len(sig_list):
                return "FALSE"
            else:
                return "TRUE"
        except Exception as e:
            return "FALSE"


    def __byte_to_str(self, data: bytes):
        return base64.b64encode(data).decode('ascii')

    def __str_to_byte(self, data: str):
        return base64.b64decode(data.encode('ascii'))