import os
import asyncio
import re
import urllib.request
from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
import threading

# --- 1. SERVIDOR FALSO PARA O RENDER ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot Espião Automático da DVD Promo a rodar a 100%!"

def manter_online():
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))

threading.Thread(target=manter_online, daemon=True).start()

# --- 2. CREDENCIAIS ---
API_ID = int(os.environ.get('API_ID'))
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('SESSION_STRING')

# --- 3. CONFIGURAÇÃO DOS CANAIS ---
CANAIS_ALVO = [
    'me', 
    '@tabaratasso', 
    '@promocoesecuponsglobais', 
    '@LinksBrazil',
    '@tigersinaiswin',
    '@ofertasnatela',
    '@OfertaLegal'
] 
MEU_CANAL = 'https://t.me/dvdpromo' 

# --- SEUS IDs SECRETOS DE AFILIADO ---
SHOPEE_ID = "an_18380960994"
ML_TOOL = "15256041"
ML_WORD = "davidvasconcellos"
MAGALU_ID = "magazinedvdnet" # Adicionada a sua loja Magalu!

# --- 4. A MÁGICA: ENGENHARIA REVERSA DE LINKS ---
def converter_link(url_original):
    try:
        req = urllib.request.Request(url_original, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as response:
            url_final = response.geturl()
        
        url_base = url_final.split('?')[0]
        
        if 'shopee' in url_base.lower():
            return f"{url_base}?utm_source={SHOPEE_ID}&utm_medium=affiliates"
        
        elif 'mercadolivre' in url_base.lower() or 'mlb' in url_base.lower() or 'meli' in url_base.lower():
            if '/social/' in url_base.lower():
                return "VITRINE_ML"
            return f"{url_base}?matt_tool={ML_TOOL}&matt_word={ML_WORD}"
            
        elif 'magazineluiza' in url_base.lower() or 'magazinevoce' in url_base.lower():
            # A nova inteligência do Magalu: joga o produto para dentro da sua loja
            if '.com.br/' in url_base:
                caminho_produto = url_base.split('.com.br/')[1]
                return f"https://www.magazinevoce.com.br/{MAGALU_ID}/{caminho_produto}"
                
        return "LOJA_DESCONHECIDA"
    except Exception as e:
        print(f"Erro ao desencurtar {url_original}: {e}")
        return "LOJA_DESCONHECIDA"

# --- 5. MOTOR DO TELEGRAM ---
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, loop=loop)

@client.on(events.NewMessage(chats=CANAIS_ALVO))
async def roubar_oferta(event):
    try:
        texto_original = event.message.text or ""
        texto_modificado = texto_original
        deve_postar = False 
        mandar_pro_privado = False 
        
        links_encontrados = re.findall(r'(https?://[^\s]+)', texto_original)
        
        if links_encontrados:
            for link in links_encontrados:
                novo_link = converter_link(link)
                
                if novo_link == "VITRINE_ML":
                    texto_modificado = texto_modificado.replace(link, f"🚨 **[LINK DA VITRINE DELES]({link})**")
                    mandar_pro_privado = True
                elif novo_link != "LOJA_DESCONHECIDA":
                    texto_modificado = texto_modificado.replace(link, f"[🛒 CLIQUE AQUI PARA VER A OFERTA]({novo_link})")
                    deve_postar = True
                else:
                    texto_modificado = texto_modificado.replace(link, "")
        
        if mandar_pro_privado:
            texto_final = f"🚨 **ALERTA DE OFERTA BOA ESCONDIDA!** 🚨\n\n{texto_modificado}\n\n⚠️ *O bot não pegou a comissão porque é link de vitrine. Procure no app e poste manualmente!*"
            await client.send_message('me', texto_final, file=event.message.media, link_preview=False)
            print("🚨 Oferta de vitrine enviada para o seu privado!")
            
        elif deve_postar:
            texto_final = f"{texto_modificado}\n\n🔥 **Mais uma oferta na DVD Promo!**"
            await client.send_message(MEU_CANAL, texto_final, file=event.message.media, link_preview=False)
            print("✅ Oferta postada com sucesso na DVD Promo!")
            
        else:
            print("🚫 Oferta ignorada: Não é produto válido ou é loja desconhecida.")
            
    except Exception as e:
        print(f"❌ Erro ao processar oferta: {e}")

# --- 6. INICIALIZAÇÃO ---
async def iniciar_bot():
    print("A iniciar a sessão do Bot Espião...")
    await client.start()
    await client.get_dialogs() 
    print("🚀 Bot Espião Automático a operar nas sombras...")
    await client.run_until_disconnected()

loop.run_until_complete(iniciar_bot())
