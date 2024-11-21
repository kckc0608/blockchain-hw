from utxo import Utxo


class Transaction():
    def __init__(self, json_dict):
        self.input = self.Input(*json_dict['input']['utxo'].values(), json_dict['input']['unlocking_script'])
        self.output = [(output_dict['amount'], output_dict['locking_script']) for output_dict in json_dict['output']]

    def __str__(self):
        return self.utxo + " " + self.unlocking_script + " " + str(self.output)


    class Input:
        def __init__(self, ptxid:str, output_index:int, unlocking_script:str):
            self.ptxid = ptxid
            self.output_index = output_index
            self.unlocking_script = unlocking_script


