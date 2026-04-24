import asyncio
import json
from datetime import datetime
from pathlib import Path
import statistics
import time
from anp import ANPClient
from web3 import Web3

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

project_root = Path(__file__).parent
print(project_root)
DID_DOC_PATH = project_root / "did_public" / "public-did-doc.json"
PRIVATE_KEY_PATH = project_root / "did_public" / "public-private-key.pem"
PRIVATE_KEY_BLOCKCHAIN = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
SEARCH_AGENT_URL = "http://localhost:8000",

RUNS = 10 # Anzahl der Testdurchläufe

# Messung
results = { "end_to_end": [],
            "search_latency": [],
            "blockchain_latency": [],
            "confirm_latency": [],
            "deploy_latency": [],
            "gas_purchase": [],
            "gas_confirm": [],
            "gas_deploy": []
            }


async def main(): 
    if not DID_DOC_PATH.exists():
        print(f"Error: DID document not found at {DID_DOC_PATH}")
        return
    
    # Initialisierung des ANP-Clients mit DID-Dokument und privatem Schlüssel
    private_key = PRIVATE_KEY_PATH if PRIVATE_KEY_PATH.exists() else DID_DOC_PATH
    client = ANPClient(did_document_path=str(DID_DOC_PATH),private_key_path=str(private_key))
    print("\n1. Client initialized")
    
    # Ruft die Agenten-Beschreibungen ab
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
        
    start_total = time.time()

    search_start = time.time()
        
    search_result = await client.call_jsonrpc(
        server_url=f"{SEARCH_AGENT_URL[0]}/rpc",
        method="agentsearch",
        params={"requirement": "Daten"}
    )

    search_end = time.time()

    agent_url_to_use = search_result['result'][0]["endpoint"]

    # Interface abfrage falls LLM nutzung
    # Nutzung ohne LLM (Direkte abfrage)
    sc = await client.call_jsonrpc(
        server_url=f"{agent_url_to_use}/rpc",
        method="purchase",
        params={}
    )

    # Initialisierung mit erhaltenen Informationen
    w3 = Web3(Web3.HTTPProvider(sc["result"]["provider"]))
    contract = w3.eth.contract(address=sc["result"]["address"], abi= json.loads(sc["result"]["abi"]))
    account = w3.eth.account.from_key(PRIVATE_KEY_BLOCKCHAIN)
    print("Frage Preis an...")
    price_in_wei = contract.functions.price().call()
    print(f"{price_in_wei} Wei")

    print("Sende Transaktion...")
    tx_start = time.time()
    tx_hash = contract.functions.purchase().transact({
        'from' : account.address,
        'value' : price_in_wei,
        'gas' : 100000,
        'nonce' : w3.eth.get_transaction_count(account.address)
    })
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    tx_end = time.time()

    gas_purchase = receipt.gasUsed

    print(f"Erfolg! Transaction Hash: {receipt.transactionHash.hex()}")

    answer = await client.call_jsonrpc(
        server_url=f"{agent_url_to_use}/rpc",
        method="returnData",
        params={}
    )
    print(f"Erhaltene Antwort: {answer}")
    confirm_start = time.time()
    if answer != "":
        tx_hash = contract.functions.confirm_delivery().transact({
            'from' : account.address
        })
        confirm_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    confirm_end = time.time()
    gas_confirm = confirm_receipt.gasUsed

    end_total = time.time()

    # Speichern
    results["search_latency"].append(search_end - search_start) 
    results["end_to_end"].append(end_total - start_total)
    results["blockchain_latency"].append(tx_end - tx_start)
    results["confirm_latency"].append(confirm_end - confirm_start)
    results["gas_purchase"].append(gas_purchase)
    results["gas_confirm"].append(gas_confirm)
    results["deploy_latency"].append(sc["result"]["time"])
    results["gas_deploy"].append(sc["result"]["cost"])

def print_results(): 
    print("\n===== EVALUATION =====")
    
    def stats(name, values):
        print(f"\n{name}:") 
        print(f" Mittelwert: {statistics.mean(values):.4f}") 
        print(f" Min: {min(values):.4f}")
        print(f" Max: {max(values):.4f}")
        
    stats("End-to-End Zeit (s)", results["end_to_end"])
    stats("Such Latenz (s)", results["search_latency"])
    stats("Blockchain Latenz (s)", results["blockchain_latency"])
    stats("Bestätigung Latenz (s)", results["confirm_latency"])
    stats("Blockchain-veröffentlichung Latenz (s)", results["deploy_latency"])
    print("\nGas Kosten:")
    print(f" purchase(): Ø {int(statistics.mean(results['gas_purchase']))}")
    print(f" confirm(): Ø {int(statistics.mean(results['gas_confirm']))}")
    print(f" deploy(): Ø {int(statistics.mean(results['gas_deploy']))}")

def plot_results():
    # 1. Daten in ein DataFrame umwandeln (einfacher für Seaborn)
    df_latency = pd.DataFrame({
        'Search': results["search_latency"],
        'Transaction': results["blockchain_latency"],
        'Confirm': results["confirm_latency"],
        'Deploy': results["deploy_latency"]
    })

    # 2. Plot erstellen
    plt.figure(figsize=(12, 6))
    
    # Subplot 1: Latenzen als Boxplot
    plt.subplot(1, 2, 1)
    sns.boxplot(data=df_latency)
    plt.title('Latenz Verteilung (s)')
    plt.ylabel('Sekunden')

    # Subplot 2: Gas Kosten (Durchschnitt)
    plt.subplot(1, 2, 2)
    gas_means = {
        'Purchase': sum(results["gas_purchase"]) / len(results["gas_purchase"]),
        'Confirm': sum(results["gas_confirm"]) / len(results["gas_confirm"]),
        'Deploy': sum(results["gas_deploy"]) / len(results["gas_deploy"])
    }
    plt.bar(gas_means.keys(), gas_means.values(), color='orange')
    plt.title('Ø Gas Kosten')
    plt.ylabel('Gas Units')

    plt.tight_layout()
    plt.show()

async def run():
    for i in range(RUNS):
        print(f"Run {i+1}/{RUNS}") 
        await main()
    print_results()
    plot_results()

if __name__ == "__main__": 
    asyncio.run(run())
    # asyncio.run(main())