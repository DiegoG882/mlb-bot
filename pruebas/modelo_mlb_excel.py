import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# -------------------------------
# FUNCIONES
# -------------------------------
def obtener_datos_api(url):
    try:
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            return respuesta.json()
    except Exception as e:
        print("Error:", e)
    return None

def extraer_partidos(datos):
    lista = []
    eventos = datos.get('events', [])
    for evento in eventos:
        for competencia in evento.get('competitions', []):
            if len(competencia.get('competitors', [])) == 2:
                local = competencia['competitors'][0]
                visitante = competencia['competitors'][1]
                partido = {
                    'id_partido': competencia.get('id'),
                    'fecha': competencia.get('date'),
                    'estado': competencia.get('status', {}).get('type', {}).get('description'),
                    'equipo_local': local.get('team', {}).get('displayName'),
                    'equipo_visitante': visitante.get('team', {}).get('displayName'),
                    'puntos_local': int(local.get('score', 0)),
                    'puntos_visitante': int(visitante.get('score', 0))
                }
                lista.append(partido)
    return lista

# -------------------------------
# PARTE 1: DESCARGAR DATOS
# -------------------------------
N = 30  # Días a recorrer hacia atrás
todos_los_partidos = []

for i in range(N):
    fecha = datetime.today() - timedelta(days=i)
    fecha_str = fecha.strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={fecha_str}"
    print(f"Revisando: {fecha_str}")
    datos = obtener_datos_api(url)
    if datos:
        partidos = extraer_partidos(datos)
        todos_los_partidos.extend(partidos)

# Filtrar solo partidos finalizados
df_nuevos = pd.DataFrame(todos_los_partidos)
df_nuevos = df_nuevos[df_nuevos['estado'] == 'Final']

# Cargar archivo existente si ya hay
archivo = 'partidos_mlb.xlsx'
if os.path.exists(archivo):
    df_existente = pd.read_excel(archivo)
else:
    df_existente = pd.DataFrame()

# Unir sin duplicar
df_total = pd.concat([df_existente, df_nuevos]).drop_duplicates(subset='id_partido')
df_total.to_excel(archivo, index=False)
print(f"\n✔ Total de partidos guardados en {archivo}: {len(df_total)}")

# -------------------------------
# PARTE 2: ENTRENAR EL MODELO
# -------------------------------
df = df_total[df_total['estado'] == 'Final'].copy()
df['gana_local'] = (df['puntos_local'] > df['puntos_visitante']).astype(int)

# Entrenamiento básico con puntos
df_modelo = df[['puntos_local', 'puntos_visitante', 'gana_local']]
X = df_modelo[['puntos_local', 'puntos_visitante']]
y = df_modelo['gana_local']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

y_pred = modelo.predict(X_test)
print(f"\n📈 Precisión del modelo: {accuracy_score(y_test, y_pred):.2f}")

# -------------------------------
# PARTE 3: PREDICCIÓN DE EJEMPLO
# -------------------------------
ejemplo = pd.DataFrame({
    'puntos_local': [6],
    'puntos_visitante': [4]
})

resultado = modelo.predict(ejemplo)
print("\n🔮 ¿Gana el equipo local?:", "Sí 🏠" if resultado[0] == 1 else "No 🚌")


# -------------------------------
# PARTE 4: PREDICCIONES CON NOMBRE DEL EQUIPO GANADOR
# -------------------------------
print("\n📅 Predicciones para los partidos del día de hoy con estadísticas reales:\n")

# Calcular promedios reales de anotaciones
promedios_local = df.groupby('equipo_local')['puntos_local'].mean()
promedios_visitante = df.groupby('equipo_visitante')['puntos_visitante'].mean()

# Obtener partidos del día actual
fecha_hoy = datetime.today().strftime("%Y%m%d")
url_hoy = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={fecha_hoy}"
datos_hoy = obtener_datos_api(url_hoy)

if datos_hoy:
    partidos_hoy = extraer_partidos(datos_hoy)
    for partido in partidos_hoy:
        if partido['estado'] != 'Final':
            local = partido['equipo_local']
            visitante = partido['equipo_visitante']

            prom_local = promedios_local.get(local, 4.5)
            prom_visitante = promedios_visitante.get(visitante, 4.0)

            entrada = pd.DataFrame({
                'puntos_local': [prom_local],
                'puntos_visitante': [prom_visitante]
            })

            pred = modelo.predict(entrada)[0]
            ganador = local if pred == 1 else visitante

            print(f"{visitante} vs {local}")
            print(f"Prom. {visitante}: {prom_visitante:.2f} | Prom. {local}: {prom_local:.2f}")
            print(f"🔮 Predicción: Gana **{ganador}**\n")
else:
    print("No se pudieron obtener los partidos del día.")
