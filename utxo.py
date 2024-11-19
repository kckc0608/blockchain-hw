class Utxo:
    def __init__(self, utxo_dict):
        self.txid = utxo_dict['txid']
        self.output_index = utxo_dict['output_index']
        self.amount = utxo_dict['amount']
        self.locking_script = utxo_dict['locking_script']