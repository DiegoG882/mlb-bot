import requests

# Token de tu bot
bot_token = "7840207154:AAHVsYGk2PiEMPPRwwOKy_uPWxtWzIAMd_o"

# Tu chat ID
chat_id = "1693253640"

# Mensaje de prueba
mensaje = "✅ ¡Hola Diego! Tu bot de Telegram está funcionando correctamente. ⚾️"

# Enviar mensaje
url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
data = {
    "chat_id": chat_id,
    "text": mensaje
}

response = requests.post(url, data=data)

# Ver resultado
if response.status_code == 200:
    print("✅ Mensaje enviado con éxito.")
else:
    print("❌ Error al enviar mensaje.")
    print("Código:", response.status_code)
    print("Respuesta:", response.text)
