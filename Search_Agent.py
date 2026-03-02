import uvicorn
from anp.fastanp import FastANP
from typing import List, Dict

# Initialisierung des ANP-Servers auf Port 8000
anp = FastANP(
    name="Search Agent",
    description="Empfiehlt Agenten",
    agent_domain="http://localhost:8000",
    did="did:wba:didhost.cc:public",
    enable_auth_middleware=False,  # Disable auth for simplicity
)

# Die Agenten-Registry
AGENT_REGISTRY = [
    {
        "name": "Uhrzeit-Agent",
        "capability": "Besitzt einen SmartContract für die aktuelle Uhrzeit",
        "endpoint": "http://localhost:6000"
    },
]

# Erstellung der Agenten Beschreibung
@anp.information("/ad.json", type="AgentDescription", description="Agent Description", tags=["agent"])
def get_agent_description():
    """Get Agent Description."""
    ad = anp.get_common_header(agent_description_path="/ad.json")
    # Hinzufügen des Interfaces
    ad["interfaces"] = [anp.interfaces[agentsearch].link_summary,]
    return ad

# Interface erstellung | Such-Logik (Simple Keyword-Matching)
@anp.interface("/info/agentsearch.json", description="Returns a fitting Agent")
def agentsearch(requirement: str) -> List[Dict]:
    print("Agentsearch")
    requirement = requirement.lower()
    matches = []
    for agent in AGENT_REGISTRY:
        # Prüfen, ob Wörter aus der Anforderung in der Beschreibung vorkommen
        if any(word in agent["capability"].lower() for word in requirement.split()):
            matches.append(agent)
    return matches

# Start des Discovery Agents
if __name__ == "__main__":
    uvicorn.run(anp.app, host="0.0.0.0", port=8000)