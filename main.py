import os
import asyncio
import re
import urllib.request
import urllib.parse
import urllib.error
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

# --- IDs SECRETOS DE AFILIADO ---
SHOPEE_ID = "an_18380960994"
ML_TOOL = "15256041"
ML_WORD = "davidvasconcellos"

MAGALU_PROMOTER = "5636885"
MAGALU_PARTNER = "3440"

# --- 4. A MÁGICA: MOTOR ANTI-BLOQUEIO DO MAGALU ---
class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib.response.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl
    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302

def converter_link(url_original):
    try:
        opener = urllib.request.build_opener(NoRedirectHandler())
        current_url = url_original
        
        # O bot vai rastrear o link passo a passo, no máximo 5 vezes
        for _ in range(5):
            req = urllib.request.Request(current_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            try:
                response = opener.open(req, timeout=10)
                if response.code in (301, 302, 303, 307, 308):
                    new_url = response.headers.get('Location')
                    if not new_url:
                        break
                    
                    # SE O PRÓXIMO DESTINO FOR O MURO DO MAGALU (PERFDRIVE), O BOT SALTA FORA!
                    if 'perfdrive' in new_url.lower():
                        break 
                        
                    current_url = urllib.parse.urljoin(current_url, new_url)
                else:
                    break
            except urllib.error.HTTPError as e:
                # Se esbarrar num erro 403 do muro, o link que temos na mão já é o do produto certo!
                break
            except Exception as e:
                break
                
        url_final = current_url
        url_base = url_final.split('?')[0]
        
        # 1. SHOPEE
        if 'shopee' in url_base.lower():
            return f"{url_base}?utm_source={SHOPEE_ID}&utm_medium=affiliates"
        
        # 2. MERCADO LIVRE
        elif 'mercadolivre' in url_base.lower() or 'mlb' in url_base.lower() or 'meli' in url_base.lower():
            if '/social/' in url_base.lower():
                return "VITRINE_ML"
            return f"{url_base}?matt_tool={ML_TOOL}&matt_word={ML_WORD}"
            
        # 3. MAGALU
        elif 'magalu' in url_final.lower() or 'magazine' in url_final.lower():
            # Limpa qualquer formato antigo de loja do concorrente
            if 'magazinevoce.com.br' in url_base:
                url_base = re.sub(r'magazinevoce\.com\.br/magazine[^/]+/', 'magazineluiza.com.br/', url_base)
            
            # Injeta o teu DNA de vendedor
            return f"{url_base}?promoter_id={MAGALU_PROMOTER}&partner_id={MAGALU_PARTNER}"
            
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
                    texto_modificado = texto_modificado.replace(link, f"[🛒 CLICA AQUI PARA VER A OFERTA]({novo_link})")
                    deve_postar = True
                else:
                    texto_modificado = texto_modificado.replace(link, "")
        
        if mandar_pro_privado:
            texto_final = f"🚨 **ALERTA DE OFERTA BOA ESCONDIDA!** 🚨\n\n{texto_modificado}\n\n⚠️ *O bot não pegou na comissão porque é um link de vitrine do ML. Procura na app e publica manualmente!*"
            await client.send_message('me', texto_final, file=event.message.media, link_preview=False)
            print("🚨 Oferta de vitrine enviada para o privado!")
            
        elif deve_postar:
            texto_final = f"{texto_modificado}\n\n🔥 **Mais uma oferta na DVD Promo!**"
            await client.send_message(MEU_CANAL, texto_final, file=event.message.media, link_preview=False)
            print("✅ Oferta publicada com sucesso na DVD Promo!")
            
        else:
            print("🚫 Oferta ignorada: Não é produto válido ou loja desconhecida.")
            
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
