import sys
import threading
import redis

if len(sys.argv) != 2:
    print("Uso: python3 chat_keydb.py <tu_nombre>")
    sys.exit(1)

NICK = sys.argv[1]
CHANNEL = "sala_chat"

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def listener():
    sub = r.pubsub()
    sub.subscribe(CHANNEL)
    for msg in sub.listen():
        if msg["type"] == "message":
            print("\r" + msg["data"] + "\n> ", end="", flush=True)

print(f"Conectado a KeyDB como {NICK}. Escribe y presiona Enter (Ctrl-C para salir)…")
threading.Thread(target=listener, daemon=True).start()

try:
    while True:
        texto = input("> ").strip()
        if texto:
            r.publish(CHANNEL, f"[{NICK}] {texto}")
except KeyboardInterrupt:
    print("\nSaliendo… ¡Hasta luego!")
