import os
import json
import time
import urllib.parse
import webbrowser
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from core.config.settings import TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET

PORT = 8080
REDIRECT_URI = f"http://localhost:{PORT}/callback"
AUTH_CODE = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global AUTH_CODE
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            AUTH_CODE = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
            <html>
            <body style="font-family: Arial; text-align: center; padding-top: 50px; background: #121212; color: #fff;">
                <h1 style="color: #00f2fe;">✅ Autenticação do TikTok Concluída!</h1>
                <p>O arquivo <strong>token_tiktok.json</strong> foi gerado. Você pode fechar esta aba.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write("Erro na autenticacao.".encode("utf-8"))

    def log_message(self, format, *args):
        return  # Silencia logs padrão do HTTP Server


def autenticar():
    print("==========================================")
    print(" 🎵 FLUXO DE AUTENTICAÇÃO DO TIKTOK")
    print("==========================================")

    if not TIKTOK_CLIENT_KEY or not TIKTOK_CLIENT_SECRET:
        print("❌ TIKTOK_CLIENT_KEY ou TIKTOK_CLIENT_SECRET não estão configurados no arquivo .env!")
        print("Por favor, preencha essas variáveis no seu arquivo .env antes de continuar.")
        return

    csrf_state = "tiktok_auth_" + str(int(time.time()))
    scopes = "user.info.basic,video.upload,video.publish"

    auth_url = (
        f"https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={TIKTOK_CLIENT_KEY}"
        f"&scope={scopes}"
        f"&response_type=code"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&state={csrf_state}"
    )

    print(f"\n1. Abrindo navegador para autorização do TikTok...")
    print(f"URL: {auth_url}\n")
    webbrowser.open(auth_url)

    # Inicia servidor local temporário para escutar o callback
    server = HTTPServer(("localhost", PORT), OAuthHandler)
    print("⏳ Aguardando confirmação no navegador...")

    while AUTH_CODE is None:
        server.handle_request()

    print("\n✅ Código de autorização recebido! Trocando por Token de Acesso...")

    # Troca o código por access_token e refresh_token
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    payload = {
        "client_key": TIKTOK_CLIENT_KEY,
        "client_secret": TIKTOK_CLIENT_SECRET,
        "code": AUTH_CODE,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    res = requests.post(token_url, data=payload, headers=headers, timeout=15)

    if res.status_code == 200:
        data = res.json()
        token_info = {
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),
            "open_id": data.get("open_id"),
            "scope": data.get("scope"),
            "expires_at": time.time() + data.get("expires_in", 86400)
        }

        with open("token_tiktok.json", "w", encoding="utf-8") as f:
            json.dump(token_info, f, indent=2)

        print("\n🎉 SUCESSO! O arquivo 'token_tiktok.json' foi criado na raiz do projeto!")
        print("O Trabalhador1 já pode postar no TikTok automaticamente.")
    else:
        print(f"\n❌ Erro ao obter token do TikTok: Status {res.status_code}")
        print(res.text)


if __name__ == "__main__":
    autenticar()
