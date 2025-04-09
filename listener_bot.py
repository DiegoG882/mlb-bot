import time
import requests
from mlb_picks_diarios import generar_picks_del_dia

# Token y API base
BOT_TOKEN = "7840207154:AAHVsYGk2PiEMPPRwwOKy_uPWxtWzIAMd_o"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
offset = None

def responder(chat_id, mensaje):
    requests.post(API_URL + "sendMessage", data={"chat_id": chat_id, "text": mensaje})

print("🤖 Bot escuchando mensajes...")

while True:
    try:
        resp = requests.get(API_URL + "getUpdates", params={"offset": offset})
        data = resp.json()

        for update in data.get("result", []):
            offset = update["update_id"] + 1
            chat_id = update["message"]["chat"]["id"]
            texto = update["message"]["text"].strip().lower()

            if "picks" in texto:
                responder(chat_id, "🔮 Picks de hoy:\nCargando predicciones...")
                picks = generar_picks_del_dia()
                responder(chat_id, picks)

            elif "hola" in texto or "help" in texto:
                responder(chat_id, "👋 Hola, soy tu bot de predicciones MLB.\nPuedes escribirme:\n• picks – para recibir los partidos de hoy")

            else:
                responder(chat_id, "❓ No entendí. Escribe 'picks' o 'help'.")

        time.sleep(2)

    except Exception as e:
        print("❌ Error:", e)
        time.sleep(5)
