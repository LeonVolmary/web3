from anp.fastanp import FastANP
import uvicorn
from typing import List, Dict

# Initialisierung des ANP-Servers auf Port 8000
anp = FastANP(
    name="Search Agent",
    description="Empfiehlt Agenten",
    agent_domain="http://localhost:6000",
    did="did:wba:didhost.cc:public",
    enable_auth_middleware=False,  # Disable auth for simplicity
)

@anp.information("/ad.json", type="AgentDescription", description="Agent Description", tags=["agent"])
def get_agent_description():
    """Get Agent Description"""
    ad = anp.get_common_header(agent_description_path="/ad.json")
    #Hinzufügen des Interfaces
    ad["intefaces"] = [anp.interfaces[timeInfo].link_summary,]
    return ad

@anp.interface("/info/timeInfo.json", description="Returns Information for a Smart Contract which returns the current Time after paying")
def timeInfo() -> dict:
    """    
    :return: Dictionary with "abi", "address", "provider"
    """

    sc = {
        "abi": '[{"type":"event","name":"DateQueried","inputs":[{"name":"querier","type":"address","components":null,"internalType":null,"indexed":true},{"name":"timestamp","type":"uint256","components":null,"internalType":null,"indexed":false}],"anonymous":false},{"type":"function","name":"get_current_timestamp","stateMutability":"payable","inputs":[],"outputs":[{"name":"","type":"uint256","components":null,"internalType":null}]},{"type":"function","name":"withdraw_fees","stateMutability":"nonpayable","inputs":[],"outputs":[]},{"type":"function","name":"owner","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"address","components":null,"internalType":null}]},{"type":"constructor","stateMutability":"nonpayable","inputs":[]}]',
        "address": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
        "provider": "http://192.168.0.167:8545"
    }
    return sc

if __name__ == "__main__":
    uvicorn.run(anp.app, host="0.0.0.0", port=6000)