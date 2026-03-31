from anp.fastanp import FastANP
import uvicorn
from web3 import Web3
from web3.contract import Contract
import json

w3 = Web3(Web3.HTTPProvider("http://192.168.0.167:8545"))
if not w3.is_connected():
    print("Nicht mit der Blockchain verbunden")
    exit()
contract_Bytecode = "3461009a5760206105b15f395f516064602082610591015f395f511161009a576020602082610591015f395f51018082610591016040395050335f5560206105915f395f516002556020604051015f81601f0160051c6005811161009a57801561007d57905b8060051b604001518160030155600101818118610065575b5050505f6008555f6009556104df61009e610000396104df610000f35b5f80fd5f3560e01c60026007820660011b6104d101601e395f51565b6308551a5381186104c957346104cd575f5460405260206040f36104c9565b637150d8ae81186104c957346104cd5760015460405260206040f36104c9565b63a035b1fe81186104c957346104cd5760025460405260206040f36104c9565b637e8a4a9b81186100f257346104cd57602080604052806040016020600354015f81601f0160051c600581116104cd5780156100c657905b80600301548160051b8501526001018181186100af575b5050508051806020830101601f825f03163682375050601f19601f825160200101169050810190506040f35b634de5585c81186104c957346104cd5760095460405260206040f36104c9565b63de7d1525811861012e57346104cd5760085460405260206040f35b6364edfbf081186104c9576008541561019c57600f6040527f426572656974732062657a61686c74000000000000000000000000000000000060605260405060405180606001601f825f031636823750506308c379a05f526020602052601f19601f6040510116604401601cfd5b6002543418156102015760186040527f53656e64652064656e206578616b74656e20426574726167000000000000000060605260405060405180606001601f825f031636823750506308c379a05f526020602052601f19601f6040510116604401601cfd5b336001556001600855006104c9565b636607ce2f81186104c957346104cd576001543318156102a957602b6040527f4e757220646572204b616575666572206b616e6e2064656e20457268616c74206060527f626573746165746967656e00000000000000000000000000000000000000000060805260405060405180606001601f825f031636823750506308c379a05f526020602052601f19601f6040510116604401601cfd5b60085461030b5760126040527f4e6f6368206e696368742062657a61686c74000000000000000000000000000060605260405060405180606001601f825f031636823750506308c379a05f526020602052601f19601f6040510116604401601cfd5b600954156103925760216040527f5472616e73616b74696f6e206265726569747320616267657363686c6f7373656060527f6e0000000000000000000000000000000000000000000000000000000000000060805260405060405180606001601f825f031636823750506308c379a05f526020602052601f19601f6040510116604401601cfd5b60016009555f5f5f5f6002545f545ff1156104cd57006104c9565b6335a063b481186104c957346104cd575f543318156104455760216040527f4e757220646572205665726b616575666572206b616e6e2061626272656368656060527f6e0000000000000000000000000000000000000000000000000000000000000060805260405060405180606001601f825f031636823750506308c379a05f526020602052601f19601f6040510116604401601cfd5b600954156104a85760156040527f4265726569747320616267657363686c6f7373656e000000000000000000000060605260405060405180606001601f825f031636823750506308c379a05f526020602052601f19601f6040510116604401601cfd5b600854156104c2575f5f5f5f6002546001545ff1156104cd575b6001600955005b5f5ffd5b5f80fd021000180037005703ad01120077841904df810e00a16576797065728300030a0014"
contract_abi = '[{"type":"constructor","stateMutability":"nonpayable","inputs":[{"name":"_price","type":"uint256","components":null,"internalType":null},{"name":"_info","type":"string","components":null,"internalType":null}]},{"type":"function","name":"purchase","stateMutability":"payable","inputs":[],"outputs":[]},{"type":"function","name":"confirm_delivery","stateMutability":"nonpayable","inputs":[],"outputs":[]},{"type":"function","name":"abort","stateMutability":"nonpayable","inputs":[],"outputs":[]},{"type":"function","name":"seller","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"address","components":null,"internalType":null}]},{"type":"function","name":"buyer","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"address","components":null,"internalType":null}]},{"type":"function","name":"price","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint256","components":null,"internalType":null}]},{"type":"function","name":"data_info","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"string","components":null,"internalType":null}]},{"type":"function","name":"is_paid","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"bool","components":null,"internalType":null}]},{"type":"function","name":"is_completed","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"bool","components":null,"internalType":null}]}]'
contract_address = ""
contract_to_deploy = w3.eth.contract(abi=contract_abi, bytecode = contract_Bytecode)
PRIVATE_KEY_BLOCKCHAIN = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
account = w3.eth.account.from_key(PRIVATE_KEY_BLOCKCHAIN)
contract: Contract


# Initialisierung des ANP-Servers auf Port 8000
anp = FastANP(
    name="Verkäufer Agent",
    description="Verkauft die Antwort auf alles",
    agent_domain="http://localhost:6000",
    did="did:wba:didhost.cc:public",
    enable_auth_middleware=False,  # Disable auth for simplicity
)

@anp.information("/ad.json", type="AgentDescription", description="Agent Description", tags=["agent"])
def get_agent_description():
    """Get Agent Description"""
    ad = anp.get_common_header(agent_description_path="/ad.json")
    #Hinzufügen des Interfaces
    ad["intefaces"] = [anp.interfaces[purchase].link_summary, anp.interfaces[returnData].link_summary]
    return ad

@anp.interface("/info/purchase.json", description="Gibt die Information zum Bezahlen")
def purchase() -> dict:
    global contract
    """    
    Veröffentlicht den Smart Contract
    :return: Dictionary with "abi", "address", "provider"
    """
    tx_hash = contract_to_deploy.constructor(10000, "Die Antwort auf alles").transact({
        'from': account.address,
        'gas': 2000000
    })

    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt.contractAddress
    print(f"Vertrag erstellt{contract_address}")
    print(f"Account Value:{w3.eth.get_balance(account.address)}")

    contract =  w3.eth.contract(address=contract_address, abi=json.loads(contract_abi))

    sc = {
        "abi": f"{contract_abi}",
        "address": f"{contract_address}",
        "provider": "http://192.168.0.167:8545"
    }
    return sc

@anp.interface("/daten/daten.json", description="Sendet die Daten, wenn die Zahlung erfolgt ist.")
def returnData() -> str:
    paid = contract.functions.is_paid().call()
    if paid:
        return "42"
    else:
        return ""

if __name__ == "__main__":
    uvicorn.run(anp.app, host="0.0.0.0", port=6000)