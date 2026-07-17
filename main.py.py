import requests
import gzip
import time
import json
import os
import math
from discord import SyncWebhook

# --- CONFIGURARE ---
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PUNCTAJ_MIN = 26
CONTINENTE_PERMISE = [43, 53]
# --------------------

FILE_URL = "https://rop13.triburile.ro/map/village.txt.gz"
DB_FILE = "/app/sate_curente.json"

def calcul_k(x, y):
    return (math.floor(y / 100) * 10) + math.floor(x / 100)

def descarca_si_parseaza():
    try:
        response = requests.get(FILE_URL, timeout=30)
        with open("village.txt.gz", "wb") as f: f.write(response.content)
        sate = {}
        with gzip.open("village.txt.gz", "rt", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 6 and parts[4] == "0":
                    x, y, p = int(parts[2]), int(parts[3]), int(parts[5])
                    k = calcul_k(x, y)
                    if p >= PUNCTAJ_MIN and k in CONTINENTE_PERMISE:
                        sate[parts[0]] = {"nume": parts[1], "x": x, "y": y, "puncte": p, "k": k}
        return sate
    except: return None

def main():
    if not WEBHOOK_URL: return
    webhook = SyncWebhook.from_url(WEBHOOK_URL)
    baza_veche = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: baza_veche = json.load(f)

    while True:
        baza_noua = descarca_si_parseaza()
        if baza_noua:
            if len(baza_veche) > 0:
                for v_id, info in baza_noua.items():
                    if v_id not in baza_veche:
                        webhook.send(f"🚨 **Sat nou în K{info['k']}** | Puncte: {info['puncte']} | Coordonate: {info['x']}|{info['y']}")
            with open(DB_FILE, "w") as f: json.dump(baza_noua, f)
            baza_veche = baza_noua
        time.sleep(300)

if __name__ == "__main__": main()