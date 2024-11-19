import json


class Transaction():
    def __init__(self, json_dict):
        self.input_transaction = json_dict['input']['utxo']
        self.unlocking_script = json_dict['input']['unlocking_script']
        self.output = [(output_dict['amount'], output_dict['locking_script']) for output_dict in json_dict['output']]

    def __str__(self):
        return self.input_transaction + " " + self.unlocking_script + " " + str(self.output)


