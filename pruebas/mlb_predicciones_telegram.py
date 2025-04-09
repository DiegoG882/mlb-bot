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

def enviar_telegram(mensaje):
    bot_token = "7840207154:AAHVsYGk2PiEMPPRwwOKy_uPWxtWzIAMd_o"
    chat_id = "1693253640"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": mensaje
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("✅ Predicciones enviadas por Telegram.")
    else:
        print("❌ Error al enviar por Telegram.")
        print("Código:", response.status_code)
        print("Respuesta:", response.text)

# -------------------------------
# ENTRENAR MODELO
# -------------------------------

archivo = 'partidos_mlb.xlsx'
if not os.path.exists(archivo):
    print("❌ No se encontró el archivo partidos_mlb.xlsx")
    exit()

df_total = pd.read_excel(archivo)
df = df_total[df_total['estado'] == 'Final'].copy()
df['gana_local'] = (df['puntos_local'] > df['puntos_visitante']).astype(int)

X = df[['puntos_local', 'puntos_visitante']]
y = df['gana_local']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

print(f"📈 Precisión del modelo: {accuracy_score(y_test, modelo.predict(X_test)):.2f}")

promedios_local = df.groupby('equipo_local')['puntos_local'].mean()
promedios_visitante = df.groupby('equipo_visitante')['puntos_visitante'].mean()

# -------------------------------
# PREDICCIONES DEL DÍA
# -------------------------------

fecha_hoy = datetime.today().strftime("%Y%m%d")
url_hoy = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={fecha_hoy}"
datos_hoy = obtener_datos_api(url_hoy)

mensaje = f"📅 Predicciones MLB del {datetime.today().strftime('%d/%m')}:\n"

if datos_hoy:
    partidos = extraer_partidos(datos_hoy)
    for partido in partidos:
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

            total_estimado = prom_local + prom_visitante
            pick_total = "Over 8.5" if total_estimado >= 9 else "Under 8.5"

            diferencia = abs(prom_local - prom_visitante)
            pick_handicap = f"{ganador} -1.5" if diferencia >= 1.5 else "N/A"

            ambos_anotan = "Sí" if prom_local >= 3 and prom_visitante >= 3 else "No"

            mensaje += f"\n{visitante} vs {local}\n"
            mensaje += f"🔮 Gana: {ganador}\n"
            mensaje += f"⚾ Total estimado: {total_estimado:.1f} → {pick_total}\n"
            mensaje += f"📉 Hándicap sugerido: {pick_handicap}\n"
            mensaje += f"🎯 Ambos anotan: {ambos_anotan}\n"

    if mensaje.strip() == f"📅 Predicciones MLB del {datetime.today().strftime('%d/%m')}:":
        mensaje += "\n⚠️ No se encontraron partidos pendientes hoy."
else:
    mensaje += "\n⚠️ No se pudo obtener la información desde ESPN."

# -------------------------------
# ENVIAR MENSAJE
# -------------------------------

enviar_telegram(mensaje)
