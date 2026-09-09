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
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            page = context.new_page()

            def on_request(request):
                nonlocal m3u8_detectado, referer_detectado
                url = request.url
                
                # Ignora anúncios e contadores externos
                dominios_ignorar = ["mediacdn.net", "analytics", "doubleclick", "google", "facebook", "favicon", "whos.amung.us"]
                if any(df in url for df in dominios_ignorar):
                    return

                # PRIORIDADE MÁXIMA: Capturar explicitamente o arquivo "file.txt" da CDN
                if "file.txt" in url or "cloudfront" in url:
                    m3u8_detectado = url
                    headers = request.headers
                    if "referer" in headers:
                        referer_detectado = headers["referer"]
                    print(f"🎯 [FILE.TXT CAPTURADO]: {url}")
                    return

                # PRIORIDADE SECUNDÁRIA: Outros manifestos .m3u8 válidos
                if not m3u8_detectado and any(p in url for p in [".m3u8", ".m3u", "/live/", "/secure/"]):
                    if not url.endswith(".js") and not url.endswith(".css"):
                        m3u8_detectado = url
                        headers = request.headers
                        if "referer" in headers:
                            referer_detectado = headers["referer"]

            page.on("request", on_request)

            try:
                print(f"🔄 Acessando {URL_ALVO}...")
                page.goto(URL_ALVO, wait_until="domcontentloaded", timeout=30000)
                time.sleep(4)

                try:
                    page.mouse.click(400, 300)
                except Exception:
                    pass

                time.sleep(8)
            except Exception as e:
                print(f"⚠️ Aviso na navegação: {e}")

            browser.close()
    except Exception as e:
        print(f"⚠️ Aviso no Playwright: {e}")

    # Mantém o último link válido se a busca falhar
    config_antiga = {}
    if os.path.exists("stream_config.json"):
        try:
            with open("stream_config.json", "r", encoding="utf-8") as f:
                config_antiga = json.load(f)
        except Exception:
            pass

    if m3u8_detectado:
        config = {
            "url": m3u8_detectado,
            "referer": referer_detectado,
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        print(f"✅ Sucesso! Link file.txt gerado: {m3u8_detectado}")
    elif config_antiga.get("url"):
        config = config_antiga
        config["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        print("⚠️ Mantendo link anterior válido.")
    else:
        config = {
            "url": "https://a5a7158118e59ee590424b55bb9aed17.s21-cloudfront-net.lat/embedtv/a6c82895309a9d179c74f8d2f4fdf916/file.txt",
            "referer": "https://alerquina54105.embedtv.lat/",
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        print("⚠️ Aplicando link de contingência.")

    with open("stream_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

if __name__ == "__main__":
    capturar_stream()
