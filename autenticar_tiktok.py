import os
import json
import time
import urllib.parse
import webbrowser
import requests
from core.config.settings import TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET

REDIRECT_URI = "https://sistema-op-marketing.vercel.app/"


def autenticar():
    print("==========================================")
    print(" 🎵 FLUXO DE AUTENTICACAO DO TIKTOK")
    print("==========================================")

    if not TIKTOK_CLIENT_KEY or not TIKTOK_CLIENT_SECRET:
        print("ERRO: TIKTOK_CLIENT_KEY ou TIKTOK_CLIENT_SECRET nao estao configurados no .env!")
        return

    csrf_state = "tiktok_auth_" + str(int(time.time()))
    scopes = "user.info.basic,video.upload"

    auth_url = (
        f"https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={TIKTOK_CLIENT_KEY}"
        f"&scope={urllib.parse.quote(scopes)}"
        f"&response_type=code"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&state={csrf_state}"
    )

    print("\n1. Abrindo navegador para voce autorizar o TikTok...")
    print(f"   URL: {auth_url}\n")
    webbrowser.open(auth_url)

    print("=" * 60)
    print("INSTRUCAO IMPORTANTE:")
    print("Apos clicar em 'Permitir/Authorize' no navegador,")
    print("o TikTok vai te redirecionar para a pagina do GitHub.")
    print("Olhe para a BARRA DE ENDERECOS do navegador.")
    print("Ela vai parecer com isso:")
    print("  https://github.com/gustavocapichoni/trabalhador1?code=XXXXX&state=YYY")
    print("")
    print("Copie APENAS o valor que vem depois de '?code='")
    print("(tudo antes do '&state')")
    print("=" * 60)

    auth_code = input("\nCole aqui o codigo copiado da URL e pressione ENTER: ").strip()

    # Remove qualquer parte extra caso o usuario cole a URL inteira
    if "code=" in auth_code:
        auth_code = auth_code.split("code=")[1].split("&")[0]

    if not auth_code:
        print("\nERRO: Codigo vazio! Tente novamente.")
        return

    print("\n Trocando codigo por Token de Acesso...")

    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    payload = {
        "client_key": TIKTOK_CLIENT_KEY,
        "client_secret": TIKTOK_CLIENT_SECRET,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    res = requests.post(token_url, data=payload, headers=headers, timeout=15)

    print(f"\nResposta da API TikTok (status {res.status_code}):")
    print(res.text)


    if res.status_code == 200:
        data = res.json()
        access_token = data.get("access_token")

        if not access_token:
            print("\nERRO: O TikTok retornou status 200 mas o access_token esta vazio!")
            print("Isso geralmente significa que o codigo de autorizacao expirou.")
            print("Por favor, rode o script novamente e use o codigo IMEDIATAMENTE apos autorizar.")
            return

        token_info = {
            "access_token": access_token,
            "refresh_token": data.get("refresh_token"),
            "open_id": data.get("open_id"),
            "scope": data.get("scope"),
            "expires_at": time.time() + data.get("expires_in", 86400)
        }

        with open("token_tiktok.json", "w", encoding="utf-8") as f:
            json.dump(token_info, f, indent=2)

        print("\nSUCESSO! O arquivo 'token_tiktok.json' foi criado com token valido!")
        print(f"open_id: {data.get('open_id')}")
        print("O Trabalhador1 ja pode postar no TikTok automaticamente.")
    else:
        print(f"\nERRO ao obter token: Status {res.status_code}")
        print(res.text)


if __name__ == "__main__":
    autenticar()

