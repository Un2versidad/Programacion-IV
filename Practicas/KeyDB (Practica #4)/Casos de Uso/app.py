import threading
import time
import redis
import sys

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def op_ping():
    print("PING ➜", "✓" if r.ping() else "✗")

def op_set_get():
    k = input("  Clave › ")
    v = input("  Valor › ")
    ttl = input("  TTL en segundos (vacío = sin expiración) › ")
    ttl = int(ttl) if ttl.strip() else None
    r.set(k, v, ex=ttl)
    print(f"  GET {k} ➜", r.get(k))

def op_lista():
    key = input("  Nombre de lista › ")
    while True:
        sub = input("  [1] LPUSH  [2] RPOP  [0] Volver › ")
        if sub == "1":
            val = input("    Valor a LPUSH › ")
            r.lpush(key, val)
            print(f"    LPUSH ✔  | LLen={r.llen(key)}")
        elif sub == "2":
            val = r.rpop(key)
            print("    RPOP ➜", val)
        elif sub == "0":
            break

def op_hash():
    key = input("  Hash key › ")
    campo = input("  Campo › ")
    valor = input("  Valor › ")
    r.hset(key, campo, valor)
    print("  HGETALL ➜", r.hgetall(key))

def op_pipeline():
    n = int(input("  ¿Cuántas veces incrementar 'visitas'? › "))
    with r.pipeline(transaction=True) as pipe:
        for _ in range(n):
            pipe.incr("visitas")
        valores = pipe.execute()
    print("  Valor final de 'visitas' ➜", valores[-1])

sub_thread = None
stop_sub = threading.Event()

def listen_pubsub():
    sub = r.pubsub()
    sub.subscribe("noticias")
    for msg in sub.listen():
        if stop_sub.is_set():
            break
        if msg["type"] == "message":
            print(f"\n[SUSCRIPTOR] {msg['data']}")
    sub.close()

def op_pubsub():
    global sub_thread
    if not sub_thread:
        stop_sub.clear()
        sub_thread = threading.Thread(target=listen_pubsub, daemon=True)
        sub_thread.start()
        print("  Suscriptor en canal 'noticias' iniciado.")
    msg = input("  Mensaje para publicar (vacío = salir) › ")
    if msg:
        r.publish("noticias", msg)
    else:
        stop_sub.set()
        sub_thread = None
        print("  Suscriptor detenido.")

def op_clean():
    pats = input("  Patrón de claves a borrar (ej: * ) › ")
    keys = r.keys(pats)
    if not keys:
        print("  No se encontraron claves.")
    else:
        r.delete(*keys)
        print(f"  Borradas {len(keys)} claves.")

menu = {
    "1": ("Ping", op_ping),
    "2": ("SET / GET (string)", op_set_get),
    "3": ("Listas LPUSH / RPOP", op_lista),
    "4": ("Hashes HSET / HGETALL", op_hash),
    "5": ("Pipeline INCR visitas", op_pipeline),
    "6": ("Pub/Sub (canal noticias)", op_pubsub),
    "7": ("Borrar claves (cleanup)", op_clean),
    "0": ("Salir", None),
}

def main():
    if not r.ping():
        print("❌ No se pudo conectar a KeyDB.")
        sys.exit(1)
    while True:
        print("\n=== DEMO INTERACTIVA KEYDB ===")
        for k, (txt, _) in menu.items():
            print(f"[{k}] {txt}")
        choice = input("Elige una opción › ")
        if choice == "0":
            print("Hasta luego 👋")
            break
        action = menu.get(choice, (None, None))[1]
        if action:
            try:
                action()
            except Exception as e:
                print("⚠️  Error:", e)
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()