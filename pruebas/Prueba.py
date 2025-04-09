import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

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

# 🗓 Recorrer últimos N días
N = 30
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

# 📂 Guardar los nuevos partidos
archivo = 'partidos_mlb.csv'
df_nuevos = pd.DataFrame(todos_los_partidos)
df_nuevos = df_nuevos[df_nuevos['estado'] == 'Final']

if os.path.exists(archivo):
    df_existente = pd.read_csv(archivo)
else:
    df_existente = pd.DataFrame()

# 🧼 Evitar duplicados
df_total = pd.concat([df_existente, df_nuevos]).drop_duplicates(subset='id_partido')
df_total.to_csv(archivo, index=False)
print(f"\n✔ Total de partidos en el archivo: {len(df_total)}")

# 🧠 Entrenar el modelo
df = df_total[df_total['estado'] == 'Final']
df['gana_local'] = (df['puntos_local'] > df['puntos_visitante']).astype(int)
df_modelo = df[['puntos_local', 'puntos_visitante', 'gana_local']]

X = df_modelo[['puntos_local', 'puntos_visitante']]
y = df_modelo['gana_local']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)
y_pred = modelo.predict(X_test)

print(f"📈 Precisión del modelo: {accuracy_score(y_test, y_pred):.2f}")
