import psutil
import matplotlib.pyplot as plt
import time
import os

# --- KONFIGURATION ---
AGENTS = ["Search_Agent.py", "Kaeufer_Agent.py", "Verkaeufer_Agent.py"]
COLORS = ['blue', 'green', 'orange']
Y_LIMITS = [15, 100, 30] 
X_WINDOW_SIZE = 100 
UPDATE_INTERVAL = 0.1 

# Speicher für die echten Prozess-Objekte
agent_objects = {agent: None for agent in AGENTS}
history = {agent: [0] * X_WINDOW_SIZE for agent in AGENTS}

def find_agents():
    """Sucht die Prozesse einmalig und speichert die Objekte."""
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmd = " ".join(proc.info['cmdline']) if proc.info['cmdline'] else ""
            for agent in AGENTS:
                if agent in cmd and "plot.py" not in cmd: # Monitor selbst ignorieren
                    if agent_objects[agent] is None:
                        p = psutil.Process(proc.info['pid'])
                        p.cpu_percent(interval=None) # Erster Aufruf zum Initialisieren
                        agent_objects[agent] = p
                        print(f"✅ {agent} gefunden (PID: {p.pid})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

# Initialisierung
plt.ion()
fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
fig.suptitle('Agenten CPU nutzung', fontsize=16)

lines = []
for i, agent in enumerate(AGENTS):
    line, = axs[i].plot(history[agent], color=COLORS[i], label=agent)
    axs[i].set_ylim(0, Y_LIMITS[i])
    axs[i].set_xlim(0, X_WINDOW_SIZE)
    axs[i].set_ylabel(f"CPU (%)", fontsize=10, fontweight='bold')
    axs[i].legend(loc="upper left")
    axs[i].grid(True, linestyle='--', alpha=0.4)
    lines.append(line)

    if i == len(AGENTS) - 1:
        axs[i].set_xlabel("Zeit (Intervalle: 0,1s)", fontsize=12)

print("Suche Agenten-Prozesse...")
find_agents()

try:
    while True:
        # Falls ein Agent neu gestartet wurde, kurz nachsehen
        if None in agent_objects.values():
            find_agents()

        for i, agent in enumerate(AGENTS):
            proc = agent_objects[agent]
            val = 0
            if proc and proc.is_running():
                try:
                    # Jetzt ist die Messung präzise, da wir das Objekt behalten
                    val = proc.cpu_percent(interval=None)
                except: pass
            
            history[agent].append(val)
            history[agent] = history[agent][-X_WINDOW_SIZE:]
            lines[i].set_ydata(history[agent])
        
        plt.pause(UPDATE_INTERVAL)
        
except KeyboardInterrupt:
    plt.ioff()
    plt.savefig(f"agent_fixed_{int(time.time())}.png")
    plt.show()