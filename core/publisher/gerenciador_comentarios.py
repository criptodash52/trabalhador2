"""
Módulo de Resposta Automática a Comentários (core/publisher/gerenciador_comentarios.py)

Funcionalidades:
  1. Monitora comentários nos posts/Reels recentes usando a Instagram Graph API.
  2. Filtra comentários que contenham palavras-chave dinâmicas ativadoras de CTA
     (ex: FOCO, SABEDORIA, LIBERDADE, DISCIPLINA, CLAREZA, PAZ, LIVRO, PDF, QUERO).
  3. Responde o comentário publicamente: "Link na bio! Acessa lá 📲"
  4. Registra comentários já respondidos em arquivo local / Firebase para evitar respostas duplicadas.
"""

import os
import sys
import re
import json
import requests
from loguru import logger

# Adiciona a raiz do projeto ao sys.path para garantir execução direta no terminal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from core.config.settings import IG_ACCESS_TOKEN, IG_ACCOUNT_ID

# Palavras-chave gerais ativas para disparar a resposta
PALAVRAS_CHAVE_PADRAO = [
    "FOCO", "SABEDORIA", "LIBERDADE", "DISCIPLINA", "CLAREZA", "PAZ", "LIVRO", "PDF", "QUERO", "LINK", "EBOOK", "BAIXAR"
]

MENSAGEM_RESPOSTA_PADRAO = "Link na bio! Acessa lá 📲"

ARQUIVO_HISTORICO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "midia_temp", "comentarios_respondidos.json"))


def carregar_historico_respondidos() -> set:
    """Carrega IDs de comentários que já foram respondidos anteriormente."""
    if os.path.exists(ARQUIVO_HISTORICO):
        try:
            with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar histórico de comentários: {e}")
    return set()


def salvar_historico_respondidos(respondidos: set):
    """Salva os IDs de comentários respondidos no histórico local."""
    try:
        os.makedirs(os.path.dirname(ARQUIVO_HISTORICO), exist_ok=True)
        with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
            json.dump(list(respondidos), f, indent=2)
    except Exception as e:
        logger.warning(f"⚠️ Erro ao salvar histórico de comentários: {e}")


def obter_posts_recentes(limit: int = 5) -> list[dict]:
    """Busca os últimos posts publicados na conta do Instagram."""
    if not IG_ACCESS_TOKEN or not IG_ACCOUNT_ID:
        logger.error("❌ Credenciais do Instagram (IG_ACCESS_TOKEN / IG_ACCOUNT_ID) não configuradas.")
        return []

    url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media"
    params = {
        "fields": "id,caption,permalink,timestamp,comments_count",
        "limit": limit,
        "access_token": IG_ACCESS_TOKEN,
    }
    try:
        res = requests.get(url, params=params, timeout=15)
        if res.status_code == 200:
            dados = res.json().get("data", [])
            logger.info(f"📸 {len(dados)} posts recentes encontrados para monitoramento de comentários.")
            return dados
        else:
            logger.warning(f"⚠️ Erro ao buscar posts recentes (HTTP {res.status_code}): {res.text[:150]}")
    except Exception as e:
        logger.error(f"❌ Exceção ao buscar posts recentes: {e}")
    return []


def buscar_comentarios_do_post(media_id: str) -> list[dict]:
    """Busca os comentários de um post específico."""
    if not IG_ACCESS_TOKEN:
        return []

    url = f"https://graph.facebook.com/v19.0/{media_id}/comments"
    params = {
        "fields": "id,text,username,timestamp,from",
        "access_token": IG_ACCESS_TOKEN,
    }
    try:
        res = requests.get(url, params=params, timeout=15)
        if res.status_code == 200:
            return res.json().get("data", [])
        else:
            logger.warning(f"⚠️ Erro ao buscar comentários do post {media_id}: {res.text[:120]}")
    except Exception as e:
        logger.error(f"❌ Exceção ao buscar comentários do post {media_id}: {e}")
    return []


def responder_comentario_publico(comment_id: str, mensagem: str = MENSAGEM_RESPOSTA_PADRAO) -> bool:
    """Responde a um comentário publicamente no post com 'Link na bio! Acessa lá 📲'."""
    if not IG_ACCESS_TOKEN:
        return False

    url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"
    params = {
        "message": mensagem,
        "access_token": IG_ACCESS_TOKEN,
    }
    try:
        res = requests.post(url, params=params, timeout=15)
        if res.status_code in (200, 201):
            logger.success(f"💬 Comentário {comment_id} respondido: '{mensagem}'")
            return True
        else:
            logger.warning(f"⚠️ Erro ao responder comentário (HTTP {res.status_code}): {res.text[:120]}")
    except Exception as e:
        logger.error(f"❌ Exceção ao responder comentário: {e}")
    return False


def monitorar_e_responder_comentarios(palavras_chave: list[str] | None = None, limite_posts: int = 5) -> dict:
    """
    Monitora posts recentes e responde automaticamente a comentários que contenham a palavra-chave.
    Evita responder duas vezes o mesmo comentário.
    """
    palavras = [p.upper() for p in (palavras_chave or PALAVRAS_CHAVE_PADRAO)]
    logger.info(f"🔎 Iniciando monitoramento de comentários com palavras-chave: {palavras}")

    historico_respondidos = carregar_historico_respondidos()
    posts = obter_posts_recentes(limit=limite_posts)
    stats = {"posts_analisados": len(posts), "comentarios_lidos": 0, "respostas_enviadas": 0}

    for post in posts:
        media_id = post.get("id")
        if not media_id:
            continue

        comentarios = buscar_comentarios_do_post(media_id)
        stats["comentarios_lidos"] += len(comentarios)

        for c in comentarios:
            comment_id = c.get("id")
            if not comment_id or comment_id in historico_respondidos:
                continue  # Já foi respondido

            texto_c = c.get("text", "").upper()
            user_info = c.get("from", {})
            username = c.get("username") or user_info.get("username", "usuario_instagram")

            # Verifica se contém palavra-chave ativadora
            palavra_encontrada = next((p for p in palavras if re.search(r'\b' + re.escape(p) + r'\b', texto_c)), None)

            if palavra_encontrada:
                logger.info(f"🎯 Palavra-chave '{palavra_encontrada}' detectada no comentário de @{username}!")

                if responder_comentario_publico(comment_id):
                    historico_respondidos.add(comment_id)
                    stats["respostas_enviadas"] += 1

    salvar_historico_respondidos(historico_respondidos)
    logger.info(f"📊 Resumo: {stats}")
    return stats


# ---------------------------------------------------------------------------
# Bloco de execução direta no terminal
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("MONITOR DE COMENTARIOS INSTAGRAM")
    print("=" * 60)
    res = monitorar_e_responder_comentarios(limite_posts=5)
    print(f"\nConcluido! Respostas enviadas: {res['respostas_enviadas']}")
