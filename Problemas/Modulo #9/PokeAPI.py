import requests
from tqdm import tqdm
import time
import requests_cache

# Configuración básica
BASE_URL = "https://pokeapi.co/api/v2"
requests_cache.install_cache('pokeapi_cache', expire_after=86400)  # Cache por 1 día

# Función mejorada para obtener datos JSON con manejo de errores
def obtener_json(url):
    try:
        respuesta = requests.get(url, timeout=15)
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.exceptions.HTTPError as errh:
        print(f"Error HTTP en {url}: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error de conexión en {url}: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout en {url}: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Error en {url}: {err}")
    return None

# 1a) Pokémon de tipo fuego en la región de Kanto
def pokemon_fuego_kanto():
    print("\n=== Pokémon de tipo fuego en Kanto ===")

    # Obtener todos los Pokémon de tipo fuego
    tipo_fuego = obtener_json(f"{BASE_URL}/type/fire")
    if not tipo_fuego:
        print("No se pudo obtener datos de tipo fuego")
        return

    # Obtener especies de Kanto (generación 1)
    generacion_kanto = obtener_json(f"{BASE_URL}/generation/1")
    if not generacion_kanto:
        print("No se pudo obtener datos de la generación Kanto")
        return

    # Crear conjunto de URLs de especies de Kanto para comparación
    especies_kanto = {especie['url'] for especie in generacion_kanto['pokemon_species']}

    # Filtrar Pokémon de fuego que son de Kanto
    fuego_en_kanto = []
    for pokemon in tqdm(tipo_fuego['pokemon'], desc="Filtrando Pokémon"):
        # Ignorar formas alternativas
        if '-' in pokemon['pokemon']['name']:
            continue

        datos_pokemon = obtener_json(pokemon['pokemon']['url'])
        if datos_pokemon and datos_pokemon['species']['url'] in especies_kanto:
            fuego_en_kanto.append(datos_pokemon['name'])
        time.sleep(0.2)  # Delay para evitar sobrecarga

    print(f"\n🔥 Se encontraron {len(fuego_en_kanto)} Pokémon de tipo fuego en Kanto:")
    print(", ".join([nombre.capitalize() for nombre in sorted(fuego_en_kanto)]))

# 1b) Pokémon tipo agua con altura > 1 metro
def pokemon_agua_altos():
    print("\n=== Pokémon tipo agua con altura > 1 metro ===")

    tipo_agua = obtener_json(f"{BASE_URL}/type/water")
    if not tipo_agua:
        print("No se pudo obtener datos de tipo agua")
        return

    altos = []
    for pokemon in tqdm(tipo_agua['pokemon'], desc="Buscando Pokémon altos"):
        # Ignorar formas alternativas (mega, gigantamax, etc.)
        if '-' in pokemon['pokemon']['name']:
            continue

        datos = obtener_json(pokemon['pokemon']['url'])
        if datos and datos.get('height', 0) > 10:
            altura_metros = datos['height'] / 10
            altos.append((datos['name'], altura_metros))
        time.sleep(0.2)

    if altos:
        print("\n💧 Pokémon tipo agua más altos que 1 metro:")
        for nombre, altura in sorted(altos, key=lambda x: x[1], reverse=True):
            print(f"   - {nombre.capitalize()}: {altura:.1f} metros")
    else:
        print("No se encontraron Pokémon que cumplan los criterios")

# 2a) Cadena evolutiva de un Pokémon
def cadena_evolutiva(pokemon_nombre='bulbasaur'):
    print(f"\n=== Cadena evolutiva de {pokemon_nombre.capitalize()} ===")

    especie = obtener_json(f"{BASE_URL}/pokemon-species/{pokemon_nombre}")
    if not especie:
        print("Pokémon no encontrado")
        return

    if not especie.get('evolution_chain'):
        print(f"{pokemon_nombre.capitalize()} no tiene cadena evolutiva")
        return

    url_cadena = especie['evolution_chain']['url']
    cadena = obtener_json(url_cadena)
    if not cadena:
        print("No se pudo obtener la cadena evolutiva")
        return

    def recorrer_cadena(eslabon, nombres=None):
        if nombres is None:
            nombres = []

        nombres.append(eslabon['species']['name'])

        if eslabon['evolves_to']:
            for evolucion in eslabon['evolves_to']:
                recorrer_cadena(evolucion, nombres)

        return nombres

    evoluciones = recorrer_cadena(cadena['chain'])

    print(" ➡️ ".join([nombre.capitalize() for nombre in evoluciones]))

# 2b) Pokémon de tipo eléctrico sin evoluciones
def electricos_sin_evoluciones():
    print("\n=== Pokémon eléctricos sin evoluciones ===")

    tipo_electrico = obtener_json(f"{BASE_URL}/type/electric")
    if not tipo_electrico:
        print("No se pudo obtener datos de tipo eléctrico")
        return

    sin_evolucion = []

    for pokemon in tqdm(tipo_electrico['pokemon'], desc="Analizando Pokémon"):
        # Ignorar formas alternativas
        if '-' in pokemon['pokemon']['name']:
            continue

        nombre = pokemon['pokemon']['name']
        especie = obtener_json(f"{BASE_URL}/pokemon-species/{nombre}")

        if not especie:
            continue

        # Verificar si no evoluciona de nadie
        if not especie.get('evolves_from_species'):
            cadena = obtener_json(especie['evolution_chain']['url'])
            if cadena and not cadena['chain']['evolves_to']:
                sin_evolucion.append(nombre)

        time.sleep(0.3)  # Delay importante para evitar sobrecarga

    if sin_evolucion:
        print("\n⚡ Pokémon eléctricos que no evolucionan:")
        for nombre in sorted(sin_evolucion):
            print(f"   - {nombre.capitalize()}")
    else:
        print("No se encontraron Pokémon eléctricos sin evoluciones")

# 3a) Pokémon con mayor ataque en Johto
def mayor_ataque_johto():
    print("\n=== Pokémon con mayor ataque en Johto ===")

    pokedex_johto = obtener_json(f"{BASE_URL}/pokedex/2")
    if not pokedex_johto:
        print("No se pudo obtener la Pokédex de Johto")
        return

    max_ataque = ("", 0)

    for entrada in tqdm(pokedex_johto['pokemon_entries'], desc="Analizando Pokémon"):
        nombre = entrada['pokemon_species']['name']
        pokemon = obtener_json(f"{BASE_URL}/pokemon/{nombre}")

        if pokemon:
            ataque = next((stat['base_stat'] for stat in pokemon['stats']
                           if stat['stat']['name'] == 'attack'), 0)
            if ataque > max_ataque[1]:
                max_ataque = (nombre, ataque)

        time.sleep(0.2)

    print(f"\n💥 Pokémon con mayor ataque en Johto: {max_ataque[0].capitalize()} ({max_ataque[1]})")

# 3b) Pokémon no legendario más veloz
def mas_rapido_no_legendario():
    print("\n=== Pokémon no legendario más veloz ===")

    # Primero obtener todos los Pokémon (paginación)
    todos_pokemon = []
    url = f"{BASE_URL}/pokemon?limit=1000"

    while url:
        datos = obtener_json(url)
        if not datos:
            break

        todos_pokemon.extend(datos['results'])
        url = datos.get('next')
        time.sleep(0.5)

    if not todos_pokemon:
        print("No se pudieron obtener los datos de Pokémon")
        return

    mas_rapido = ("", 0)

    for pokemon in tqdm(todos_pokemon, desc="Buscando el más veloz"):
        nombre = pokemon['name']
        datos = obtener_json(pokemon['url'])

        if datos:
            especie = obtener_json(datos['species']['url'])

            if especie and not especie.get('is_legendary', False):
                velocidad = next((stat['base_stat'] for stat in datos['stats']
                                  if stat['stat']['name'] == 'speed'), 0)
                if velocidad > mas_rapido[1]:
                    mas_rapido = (nombre, velocidad)

        time.sleep(0.2)

    print(f"\n⚡ Pokémon no legendario más veloz: {mas_rapido[0].capitalize()} (Velocidad: {mas_rapido[1]})")

# 4a) Hábitat más común entre Pokémon tipo planta
def habitat_comun_planta():
    print("\n=== Hábitat más común entre Pokémon tipo planta ===")

    tipo_planta = obtener_json(f"{BASE_URL}/type/grass")
    if not tipo_planta:
        print("No se pudo obtener datos de tipo planta")
        return

    habitats = {}

    for pokemon in tqdm(tipo_planta['pokemon'], desc="Analizando hábitats"):
        # Ignorar formas alternativas
        if '-' in pokemon['pokemon']['name']:
            continue

        nombre = pokemon['pokemon']['name']
        especie = obtener_json(f"{BASE_URL}/pokemon-species/{nombre}")

        if especie and especie.get('habitat'):
            habitat = especie['habitat']['name']
            habitats[habitat] = habitats.get(habitat, 0) + 1

        time.sleep(0.3)

    if habitats:
        habitat_comun, cantidad = max(habitats.items(), key=lambda x: x[1])
        print(f"\n🌱 Hábitat más común para Pokémon tipo planta: {habitat_comun.capitalize()} ({cantidad} Pokémon)")
    else:
        print("No se encontraron datos de hábitats")

# 4b) Pokémon más liviano
def pokemon_mas_liviano():
    print("\n=== Pokémon más liviano ===")

    # Obtener lista paginada de Pokémon
    todos_pokemon = []
    url = f"{BASE_URL}/pokemon?limit=1000"

    while url:
        datos = obtener_json(url)
        if not datos:
            break

        todos_pokemon.extend(datos['results'])
        url = datos.get('next')
        time.sleep(0.5)

    if not todos_pokemon:
        print("No se pudieron obtener los datos de Pokémon")
        return

    mas_liviano = ("", float('inf'))

    for pokemon in tqdm(todos_pokemon, desc="Buscando el más liviano"):
        datos = obtener_json(pokemon['url'])
        if datos and datos['weight'] < mas_liviano[1]:
            mas_liviano = (pokemon['name'], datos['weight'])
        time.sleep(0.2)

    peso_kg = mas_liviano[1] / 10
    print(f"\n🍃 Pokémon más liviano: {mas_liviano[0].capitalize()} ({peso_kg:.2f} kg)")

# Ejecutar consultas de forma controlada
if __name__ == "__main__":
    print("=== Consultas a la PokeAPI ===")

    # Lista de funciones a ejecutar (en orden)
    consultas = [
        pokemon_fuego_kanto,
        pokemon_agua_altos,
        lambda: cadena_evolutiva("eevee"),
        electricos_sin_evoluciones,
        mayor_ataque_johto,
        mas_rapido_no_legendario,
        habitat_comun_planta,
        pokemon_mas_liviano
    ]

    # Ejecutar cada consulta con manejo de errores
    for consulta in consultas:
        try:
            consulta()
            print("\n" + "=" * 50 + "\n")
            time.sleep(1)  # Pausa entre consultas
        except Exception as e:
            print(f"\n⚠️ Error al ejecutar consulta: {str(e)}")
            print("Continuando con la siguiente consulta...\n")
            time.sleep(2)

    print("=== Todas las consultas han finalizado ===")