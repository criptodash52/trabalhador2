import os
import time
import json
import requests
from loguru import logger

TIKTOK_API_BASE = "https://open.tiktokapis.com/v2"

def obter_token_tiktok():
    """
    Carrega o token de acesso do TikTok a partir de token_tiktok.json.
    Se estiver expirado, renova via refresh_token.
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    token_path = os.path.join(root_dir, "token_tiktok.json")

    if not os.path.exists(token_path):
        logger.error(f"❌ Arquivo 'token_tiktok.json' não encontrado em {token_path}. Rode autenticar_tiktok.py primeiro.")
        return None

    try:
        with open(token_path, "r", encoding="utf-8") as f:
            token_data = json.load(f)

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_at = token_data.get("expires_at", 0)

        # Se o token expirou (ou expira nos próximos 60s), renova via refresh_token
        if time.time() >= (expires_at - 60):
            logger.info("🔄 Token do TikTok expirado ou próximo de expirar. Renovando automaticamente...")
            from core.config.settings import TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET

            if not refresh_token or not TIKTOK_CLIENT_KEY or not TIKTOK_CLIENT_SECRET:
                logger.error("❌ Impossível renovar token do TikTok sem refresh_token e credenciais.")
                return None

            url_refresh = f"{TIKTOK_API_BASE}/oauth/token/"
            payload = {
                "client_key": TIKTOK_CLIENT_KEY,
                "client_secret": TIKTOK_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            res = requests.post(url_refresh, data=payload, headers=headers, timeout=15)

            if res.status_code == 200:
                data = res.json()
                new_access = data.get("access_token")
                new_refresh = data.get("refresh_token", refresh_token)
                expires_in = data.get("expires_in", 86400)

                token_data["access_token"] = new_access
                token_data["refresh_token"] = new_refresh
                token_data["expires_at"] = time.time() + expires_in

                with open(token_path, "w", encoding="utf-8") as f_out:
                    json.dump(token_data, f_out, indent=2)

                logger.success("✅ Token do TikTok renovado e salvo com sucesso.")
                return new_access
            else:
                logger.error(f"❌ Erro ao renovar token do TikTok: {res.status_code} - {res.text}")
                return None

        return access_token

    except Exception as e:
        logger.error(f"❌ Erro ao carregar token do TikTok: {e}")
        return None


def postar_no_tiktok(caminho_video, titulo, legenda=None, privacidade="MUTUAL_FOLLOW_FRIENDS"):
    """
    Publica um vídeo no TikTok via Content Posting API (Direct Post / Upload).
    
    Args:
        caminho_video: Caminho do arquivo .mp4
        titulo: Título do vídeo
        legenda: Texto de legenda/hashtags
        privacidade: 'PUBLIC_TO_EVERYONE', 'MUTUAL_FOLLOW_FRIENDS', 'FOLLOWER_OF_CREATOR', 'SELF_ONLY'
    """
    access_token = obter_token_tiktok()
    if not access_token:
        logger.error("❌ Impossível publicar no TikTok sem access_token válido.")
        return None

    if not os.path.exists(caminho_video):
        logger.error(f"❌ Arquivo de vídeo não encontrado: {caminho_video}")
        return None

    tamanho_bytes = os.path.getsize(caminho_video)
    texto_final = titulo
    if legenda:
        texto_final = f"{titulo}\n\n{legenda}"

    logger.info(f"📤 Iniciando publicação no TikTok: '{titulo[:30]}...' ({tamanho_bytes / 1024 / 1024:.2f} MB)")

    try:
        # Passo 1: Inicializar a sessão de postagem
        url_init = f"{TIKTOK_API_BASE}/post/publish/video/init/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }
        body_init = {
            "post_info": {
                "title": texto_final[:2200],
                "privacy_level": privacidade,
                "disable_duet": False,
                "disable_stitch": False,
                "disable_comment": False
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": tamanho_bytes,
                "chunk_size": tamanho_bytes,
                "total_chunk_count": 1
            }
        }

        res_init = requests.post(url_init, json=body_init, headers=headers, timeout=30)
        if res_init.status_code != 200:
            logger.error(f"❌ Erro ao inicializar upload no TikTok: {res_init.status_code} - {res_init.text}")
            return None

        data_init = res_init.json()
        upload_url = data_init.get("data", {}).get("upload_url")
        publish_id = data_init.get("data", {}).get("publish_id")

        if not upload_url:
            logger.error(f"❌ upload_url não retornado pelo TikTok: {data_init}")
            return None

        # Passo 2: Upload do arquivo de vídeo para a upload_url fornecida pelo TikTok
        logger.info("⏳ Enviando arquivo de vídeo para o servidor do TikTok...")
        with open(caminho_video, "rb") as f_vid:
            headers_upload = {
                "Content-Type": "video/mp4",
                "Content-Length": str(tamanho_bytes),
                "Content-Range": f"bytes 0-{tamanho_bytes-1}/{tamanho_bytes}"
            }
            res_up = requests.put(upload_url, data=f_vid, headers=headers_upload, timeout=120)

        if res_up.status_code in [200, 201]:
            logger.success(f"✅ Vídeo enviado para o TikTok com sucesso! Publish ID: {publish_id}")
            return publish_id
        else:
            logger.error(f"❌ Erro ao enviar bytes do vídeo para o TikTok: {res_up.status_code} - {res_up.text}")
            return None

    except Exception as e:
        logger.error(f"❌ Erro ao postar vídeo no TikTok: {e}")
        return None
