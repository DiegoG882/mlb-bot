import requests
import pandas as pd

# Función para obtener datos desde un endpoint específico
def obtener_datos_api(url):
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        return respuesta.json()
    else:
        print(f"Error al acceder a {url}: {respuesta.status_code}")
        return None

# URL de los endpoints de la API de ESPN
url_partidos = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
url_equipos = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams"

# Obtener datos de partidos
datos_partidos = obtener_datos_api(url_partidos)
if datos_partidos:
    eventos = datos_partidos.get('events', [])
    lista_partidos = []
    for evento in eventos:
        for competencia in evento.get('competitions', []):
            partido = {
                'id_partido': competencia.get('id'),
                'fecha': competencia.get('date'),
                'estado': competencia.get('status', {}).get('type', {}).get('description'),
                'equipo_local': competencia.get('competitors', [])[0].get('team', {}).get('displayName'),
                'equipo_visitante': competencia.get('competitors', [])[1].get('team', {}).get('displayName'),
                'puntos_local': competencia.get('competitors', [])[0].get('score'),
                'puntos_visitante': competencia.get('competitors', [])[1].get('score'),
            }
            lista_partidos.append(partido)
    df_partidos = pd.DataFrame(lista_partidos)
    df_partidos.to_csv('partidos_mlb.csv', index=False)
    print("Datos de partidos guardados en 'partidos_mlb.csv'.")

# Obtener datos de equipos
datos_equipos = obtener_datos_api(url_equipos)
if datos_equipos:
    equipos = datos_equipos.get('sports', [])[0].get('leagues', [])[0].get('teams', [])
    lista_equipos = []
    for equipo in equipos:
        team = equipo.get('team', {})
        datos_equipo = {
            'id_equipo': team.get('id'),
            'nombre': team.get('displayName'),
            'abreviatura': team.get('abbreviation'),
            'ciudad': team.get('location'),
            'nombre_equipo': team.get('name'),
            'color': team.get('color'),
            'logo': team.get('logos', [{}])[0].get('href'),
        }
        lista_equipos.append(datos_equipo)
    df_equipos = pd.DataFrame(lista_equipos)
    df_equipos.to_csv('equipos_mlb.csv', index=False)
    print("Datos de equipos guardados en 'equipos_mlb.csv'.")
