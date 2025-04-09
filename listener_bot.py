import time
import requests
from mlb_picks_diarios import generar_picks_del_dia

BOT_TOKEN = "TU_TOKEN_AQUI"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
offset = None

def responder(chat_id, mensaje):
    requests.post(API_URL + "sendMessage", data={"chat_id": chat_id, "text": mensaje})

def iniciar_bot():
    print("🤖 Bot escuchando mensajes...")
    while True:
        try:
            resp = requests.get(API_URL + "getUpdates", params={"offset": offset})
            data = resp.json()

            for update in data.get("result", []):
                global offset
                offset = update["update_id"] + 1
                chat_id = update["message"]["chat"]["id"]
                texto = update["message"]["text"].lower()

                if "picks" in texto:
                    responder(chat_id, "🔮 Picks de hoy:\nCargando...")
                    mensaje = generar_picks_del_dia()
                    responder(chat_id, mensaje)
                else:
                    responder(chat_id, "Escribe 'picks' para ver las predicciones.")

            time.sleep(3)
        except Exception as e:
            print("❌ Error:", e)
            time.sleep(5)

# 👇 Este bloque solo se ejecuta si corres el script directamente
if __name__ == "__main__":
    iniciar_bot()
