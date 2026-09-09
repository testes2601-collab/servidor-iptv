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
            # Inicia o navegador com permissões de rede liberadas
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-web-security"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            page = context.new_page()

            # Intercepta as chamadas de rede antes de virarem blob:
            def on_request(request):
                nonlocal m3u8_detectado, referer_detectado
                url = request.url
                
                # Ignora rastreadores e anúncios
                if any(ad in url for ad in ["analytics", "doubleclick", "google", "facebook", "whos.amung.us"]):
                    return

                # Captura a URL real do file.txt ou m3u8 na CDN
                if ("file.txt" in url or "cloudfront" in url or ".m3u8" in url) and not m3u8_detectado:
                    if not url.endswith(".js") and not url.endswith(".css"):
                        m3u8_detectado = url
                        headers = request.headers
                        if "referer" in headers:
                            referer_detectado = headers["referer"]
                        print(f"🎯 Link capturado da rede: {url}")

            page.on("request", on_request)

            print(f"🔄 Acessando {URL_ALVO}...")
            page.goto(URL_ALVO, wait_until="domcontentloaded", timeout=45000)
            time.sleep(4)

            # Clica no centro do player para disparar a requisição de vídeo
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

    # Atualiza o arquivo de configuração
    if m3u8_detectado:
        config = {
            "url": m3u8_detectado,
            "referer": referer_detectado,
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        print(f"✅ Sucesso! Novo link gerado: {m3u8_detectado}")
        with open("stream_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    else:
        print("❌ Falha ao capturar novo link nesta tentativa.")

if __name__ == "__main__":
    capturar_stream()
