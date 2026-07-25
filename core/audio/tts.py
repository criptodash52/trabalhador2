"""
Módulo de Geração de Voz Neural / Narração por IA (core/audio/tts.py)

Mecanismo em Cascata Inteligente:
1. Prioridade 1: ElevenLabs API (Voz Neural de Altíssima Fidelidade com ID configurado)
2. Fallback 2: Microsoft Edge TTS (Voz Neural pt-BR-AntonioNeural 100% gratuita e sem limite)
"""

import os
import requests
import uuid
import asyncio
from loguru import logger
from core.config.settings import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID

VOICE_ID_PADRAO = ELEVENLABS_VOICE_ID or "ulzsiMeCbfKyTPCNhCD5"

def gerar_narracao_elevenlabs(texto, voice_id=None, caminho_saida=None):
    """
    Gera narração via API oficial do ElevenLabs.
    """
    if not ELEVENLABS_API_KEY:
        logger.warning("⚠️ ELEVENLABS_API_KEY não configurada. Alternando para fallback gratuito.")
        return None

    vid = voice_id or VOICE_ID_PADRAO
    if not caminho_saida:
        os.makedirs("midia_temp", exist_ok=True)
        caminho_saida = f"midia_temp/narracao_elevenlabs_{uuid.uuid4().hex[:8]}.mp3"

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{vid}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    payload = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.3,
            "use_speaker_boost": True
        }
    }

    try:
        logger.info(f"🎙️ [ElevenLabs] Gerando narração por voz (Voice ID: {vid})...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            with open(caminho_saida, "wb") as f:
                f.write(response.content)
            logger.success(f"✅ Narração ElevenLabs salva em: {caminho_saida}")
            return caminho_saida
        else:
            logger.warning(f"⚠️ Resposta da API ElevenLabs (Status {response.status_code}): {response.text}")
            return None
    except Exception as e:
        logger.error(f"❌ Erro ao conectar à API ElevenLabs: {e}")
        return None


async def _gerar_edge_tts_async(texto, caminho_saida, voz="pt-BR-AntonioNeural"):
    """Função assíncrona auxiliar para o Edge TTS."""
    import edge_tts
    communicate = edge_tts.Communicate(texto, voz)
    await communicate.save(caminho_saida)


def gerar_narracao_edge_tts(texto, caminho_saida=None, voz="pt-BR-AntonioNeural"):
    """
    Gera narração gratuita usando a biblioteca edge-tts (Microsoft Azure Neural Voices).
    """
    if not caminho_saida:
        os.makedirs("midia_temp", exist_ok=True)
        caminho_saida = f"midia_temp/narracao_edge_{uuid.uuid4().hex[:8]}.mp3"

    try:
        logger.info(f"🎙️ [Edge-TTS] Gerando narração com voz neural ({voz})...")
        try:
            asyncio.run(_gerar_edge_tts_async(texto, caminho_saida, voz=voz))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_gerar_edge_tts_async(texto, caminho_saida, voz=voz))

        if os.path.exists(caminho_saida) and os.path.getsize(caminho_saida) > 0:
            logger.success(f"✅ Narração Edge-TTS salva em: {caminho_saida}")
            return caminho_saida
    except Exception as e:
        logger.warning(f"⚠️ Erro no Edge-TTS (verifique se a lib 'edge-tts' está instalada): {e}")
    
    return None


def gerar_audio_narracao(texto, voice_id=None, caminho_saida=None):
    """
    Função Principal de Áudio em Cascata:
    1º Tenta ElevenLabs
    2º Tenta Edge-TTS (Microsoft Neural Gratuito)
    """
    # Garante que o texto é limpo para áudio
    if isinstance(texto, list):
        texto_limpo = " ".join(str(x) for x in texto if x)
    else:
        texto_limpo = str(texto)

    texto_limpo = texto_limpo.replace("\n", " ").strip()
    if not texto_limpo:
        return None

    # Tenta 1: ElevenLabs
    audio_path = gerar_narracao_elevenlabs(texto_limpo, voice_id=voice_id, caminho_saida=caminho_saida)
    if audio_path and os.path.exists(audio_path):
        return audio_path

    # Tenta 2: Edge-TTS (Fallback Gratuito)
    logger.info("🔄 Ativando Fallback de voz neural gratuita (Edge-TTS)...")
    audio_path_fallback = gerar_narracao_edge_tts(texto_limpo, caminho_saida=caminho_saida)
    if audio_path_fallback and os.path.exists(audio_path_fallback):
        return audio_path_fallback

    logger.error("❌ Todas as tentativas de geração de narração falharam.")
    return None
