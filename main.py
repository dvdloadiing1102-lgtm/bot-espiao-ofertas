import os
import asyncio
from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
import threading

# --- 1. SERVIDOR FALSO PARA O RENDER ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot Espião da DVD Ofertas rodando 100%!"

def manter_online():
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))

# Inicia o servidor falso em segundo plano
threading.Thread(target=manter_online, daemon=True).start()

# --- 2. CREDENCIAIS DO TELEGRAM ---
API_ID = int(os.environ.get('API_ID'))
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('SESSION_STRING')

# --- 3. CONFIGURAÇÃO DOS CANAIS ---
CANAIS_ALVO = ['@tabaratasso'] 
MEU_CANAL = '@dvdofertas' 

# --- 4. CORREÇÃO DO EVENT LOOP (Para o Render não travar) ---
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# --- 5. LÓGICA DO BOT ---
print("Iniciando a sessão do Bot Espião...")
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, loop=loop)

@client.on(events.NewMessage(chats=CANAIS_ALVO))
async def roubar_oferta(event):
    try:
        texto_original = event.message.text or ""
        texto_final = f"{texto_original}\n\n🔥 **Mais uma oferta na DVD Ofertas!**"
        
        await client.send_message(MEU_CANAL, texto_final, file=event.message.media)
        print("✅ Oferta capturada do @tabaratasso e postada no canal!")
    except Exception as e:
        print(f"❌ Erro ao processar oferta: {e}")

print("🚀 Bot Espião operando nas sombras...")
client.start()
client.run_until_disconnected()
