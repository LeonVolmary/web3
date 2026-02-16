import json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://192.168.0.167:8545"))

address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
abi = json.loads('[{"type":"event","name":"DateQueried","inputs":[{"name":"querier","type":"address","components":null,"internalType":null,"indexed":true},{"name":"timestamp","type":"uint256","components":null,"internalType":null,"indexed":false}],"anonymous":false},{"type":"function","name":"get_current_timestamp","stateMutability":"payable","inputs":[],"outputs":[{"name":"","type":"uint256","components":null,"internalType":null}]},{"type":"function","name":"withdraw_fees","stateMutability":"nonpayable","inputs":[],"outputs":[]},{"type":"function","name":"owner","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"address","components":null,"internalType":null}]},{"type":"constructor","stateMutability":"nonpayable","inputs":[]}]')

contract = w3.eth.contract(address=address, abi=abi)

private_key = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
account = w3.eth.account.from_key(private_key)


print("Sende Transaktion...")
tx_hash = contract.functions.get_current_timestamp().transact({
    'from' : account.address,
    'value' : w3.to_wei(0.01, 'ether'),
    'gas' : 100000,
    'nonce' : w3.eth.get_transaction_count(account.address)
})

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Erfolg! Transaction Hash: {receipt.transactionHash.hex()}")

logs = contract.events.DateQueried().process_receipt(receipt)
if logs:
    print(f"Timestamp: {logs[0].args.timestamp}")