from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import requests
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

# Telegram config
import os
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_TOKEN")

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
    requests.post(url, data=data)

def obtener_datos_api(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None

def extraer_partidos(datos):
    lista = []
    for evento in datos.get("events", []):
        for competencia in evento.get("competitions", []):
            equipos = competencia.get("competitors", [])
            if len(equipos) == 2:
                local = equipos[0]
                visitante = equipos[1]
                partido = {
                    "id_partido": competencia.get("id"),
                    "fecha": competencia.get("date"),
                    "estado": competencia.get("status", {}).get("type", {}).get("description"),
                    "equipo_local": local.get("team", {}).get("displayName"),
                    "equipo_visitante": visitante.get("team", {}).get("displayName"),
                    "puntos_local": int(local.get("score", 0)),
                    "puntos_visitante": int(visitante.get("score", 0))
                }
                lista.append(partido)
    return lista

# Cargar Excel (o crear vacío si no existe)
archivo = "partidos_mlb.xlsx"
try:
    df_total = pd.read_excel(archivo)
except FileNotFoundError:
    df_total = pd.DataFrame(columns=[
        'id_partido', 'fecha', 'estado',
        'equipo_local', 'equipo_visitante',
        'puntos_local', 'puntos_visitante'
    ])

if not df_total.empty and 'estado' in df_total.columns:
    df_modelo = df_total[df_total['estado'] == 'Final'].copy()
else:
    enviar_telegram("⚠️ No hay suficientes datos para entrenar el modelo.")
    exit()

# Entrenar modelo
df_modelo['gana_local'] = (df_modelo['puntos_local'] > df_modelo['puntos_visitante']).astype(int)
X = df_modelo[['puntos_local', 'puntos_visitante']]
y = df_modelo['gana_local']
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X, y)

# Promedios por equipo
promedios_local = df_modelo.groupby('equipo_local')['puntos_local'].mean()
promedios_visitante = df_modelo.groupby('equipo_visitante')['puntos_visitante'].mean()

# Función para generar picks del día
def generar_picks_del_dia():
    hoy = datetime.today().strftime("%Y%m%d")
    url_hoy = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={hoy}"
    print("🔗 URL solicitada:", url_hoy)

    datos_hoy = obtener_datos_api(url_hoy)
    print("📦 Respuesta bruta de la API:", datos_hoy)

    mensaje = f"🎯 Picks de hoy – {datetime.today().strftime('%d/%m')}\n"

    if datos_hoy:
        partidos = extraer_partidos(datos_hoy)
        print("📦 Partidos recibidos hoy:", partidos)  # DEBUG

        if not partidos:
            mensaje += "\n⚠️ No hay partidos programados hoy."

        for p in partidos:
            local = p['equipo_local']
            visitante = p['equipo_visitante']
            prom_l = promedios_local.get(local, 4.5)
            prom_v = promedios_visitante.get(visitante, 4.0)
            total = prom_l + prom_v
            diferencia = abs(prom_l - prom_v)

            entrada = pd.DataFrame([[prom_l, prom_v]], columns=['puntos_local', 'puntos_visitante'])
            pred = modelo.predict(entrada)[0]
            ganador = local if pred == 1 else visitante

            riesgo = "60%" if diferencia < 1 else "45%" if diferencia < 1.5 else "30%" if diferencia < 2 else "20%"
            pick_total = "Over 8.5" if total >= 9 else "Under 8.5"
            handicap = f"{ganador} -1.5" if diferencia >= 1.5 else "No aplica"
            ambos = "Sí" if prom_l >= 3 and prom_v >= 3 else "No"

            mensaje += f"\n{visitante} vs {local}\n"
            mensaje += f"🔮 Gana: {ganador}\n"
            mensaje += f"💡 Riesgo estimado: {riesgo}\n"
            mensaje += f"⚾ Total estimado: {total:.1f} → {pick_total}\n"
            mensaje += f"📉 Hándicap: {handicap}\n"
            mensaje += f"🎯 Ambos anotan: {ambos}\n"
    else:
        mensaje += "\n⚠️ No se pudo obtener la información de hoy."

    return mensaje

