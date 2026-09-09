# -*- coding: utf-8 -*-
import json
import time
import os

URL_ALVO = "https://alerquina54105.embedtv.lat/espn"

def capturar_stream():
    m3u8_detectado = None
    referer_detectado = URL_ALVO

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-web-security"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            page = context.new_page()

            def on_request(request):
                nonlocal m3u8_detectado, referer_detectado
                url = request.url
                
                # Bloqueia estritamente mediacdn, anúncios e rastreadores
                dominios_bloqueados = ["mediacdn.net", "analytics", "doubleclick", "google", "facebook", "whos.amung.us"]
                if any(bad in url for bad in dominios_bloqueados):
                    return

                # REGRA RÍGIDA: Exige file.txt ou extensão .txt
                url_sem_parametros = url.split("?")
                if ("file.txt" in url or url_sem_parametros.endswith(".txt")) and not m3u8_detectado:
                    m3u8_detectado = url
                    headers = request.headers
                    if "referer" in headers:
                        referer_detectado = headers["referer"]
                    print(f"🎯 Link .txt real capturado: {url}")

            page.on("request", on_request)

            print(f"🔄 Acessando {URL_ALVO}...")
            page.goto(URL_ALVO, wait_until="domcontentloaded", timeout=45000)
            time.sleep(4)

            # Clica no player para acionar o carregamento da CDN
            try:
                page.mouse.click(640, 360)
                time.sleep(2)
                page.mouse.click(640, 360)
            except Exception:
                pass

            time.sleep(8)
            browser.close()
    except Exception as e:
        print(f"⚠️ Aviso na navegação: {e}")

    # Atualiza o arquivo de configuração apenas se encontrar um .txt válido
    if m3u8_detectado:
        config = {
            "url": m3u8_detectado,
            "referer": referer_detectado,
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        print(f"✅ Sucesso! Link .txt salvo: {m3u8_detectado}")
        with open("stream_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    else:
        print("❌ Falha: Nenhum link .txt válido foi encontrado nesta tentativa.")

if __name__ == "__main__":
    capturar_stream()
