class QueryProcess:

    def __init__(self):
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
                        continue
                    if tokens[1] == 'utxoset':
                        continue

            print("알 수 없는 명령어 입니다.")