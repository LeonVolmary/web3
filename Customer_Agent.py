import asyncio
import json
from pathlib import Path
from anp import ANPClient
from web3 import Web3

project_root = Path(__file__).parent
print(project_root)
DID_DOC_PATH = project_root / "did_public" / "public-did-doc.json"
PRIVATE_KEY_PATH = project_root / "did_public" / "public-private-key.pem"
PRIVATE_KEY_BLOCKCHAIN = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
SEARCH_AGENT_URL = "http://localhost:8000",


async def main(): 
    if not DID_DOC_PATH.exists():
        print(f"Error: DID document not found at {DID_DOC_PATH}")
        return
    
    # Initialisierung des ANP-Clients mit DID-Dokument und privatem Schlüssel
    private_key = PRIVATE_KEY_PATH if PRIVATE_KEY_PATH.exists() else DID_DOC_PATH
    client = ANPClient(did_document_path=str(DID_DOC_PATH),private_key_path=str(private_key))
    print("\n1. Client initialized")
    
    # Ruft die Agenten-Beschreibungen beider Server ab
    for i in SEARCH_AGENT_URL:
        ad_url = f"{i}/ad.json"
        print(f"\n2. Fetching agent description from {ad_url}...")
        agent_result = await client.fetch(ad_url)
        if agent_result ["success"]:
            agent = agent_result["data"]
            print(f"   ✓ Agent: {agent.get('name', 'N/A')} (DID: {agent.get('did', 'N/A')})")
            print(f"   ✓ Interfaces: {len(agent.get('interfaces', []))}")
            for iface in agent.get("interfaces", []):
                print(f"      - {iface.get('url', '')} : {iface.get('description', '')}")
        else:
            print(f"   ✗ Agent error: {agent_result.get('error')}")
            return
        
    search_result = await client.call_jsonrpc(
        server_url=f"{SEARCH_AGENT_URL[0]}/rpc",
        method="agentsearch",
        params={"requirement": "Uhrzeit"}
    )

    agent_url_to_use = search_result['result'][0]["endpoint"]

    # Interface abfrage falls LLM nutzung
    # Nutzung ohne LLM (Direkte abfrage)
    sc = await client.call_jsonrpc(
        server_url=f"{agent_url_to_use}/rpc",
        method="timeInfo",
        params={}
    )

    # Initialisierung mit erhaltenen Informationen
    w3 = Web3(Web3.HTTPProvider(sc["result"]["provider"]))
    contract = w3.eth.contract(address=sc["result"]["address"], abi= json.loads(sc["result"]["abi"]))
    account = w3.eth.account.from_key(PRIVATE_KEY_BLOCKCHAIN)
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

if __name__ == "__main__":
    asyncio.run(main())