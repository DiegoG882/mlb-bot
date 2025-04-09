import time
import requests
import os
from mlb_picks_diarios import generar_picks_del_dia
from dotenv import load_dotenv

load_dotenv()

# Configuración del bot
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

offset = None  # Se usará para evitar procesar el mismo mensaje más de una vez

def responder(chat_id, mensaje):
    requests.post(API_URL + "sendMessage", data={"chat_id": chat_id, "text": mensaje})

def iniciar_bot():
    global offset
    print("🤖 Bot escuchando mensajes...")
    while True:
        try:
            resp = requests.get(API_URL + "getUpdates", params={"offset": offset})
            data = resp.json()

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                texto = message.get("text", "").lower()

                if "picks" in texto:
                    responder(chat_id, "🔮 Picks de hoy:\nCargando...")
                    predicciones = generar_picks_del_dia()
                    responder(chat_id, predicciones)
                else:
                    responder(chat_id, "Hola 👋 escribe *picks* para ver las predicciones de hoy.")

            time.sleep(3)

        except Exception as e:
            print("❌ Error:", e)
            time.sleep(5)

if __name__ == "__main__":
    iniciar_bot()
