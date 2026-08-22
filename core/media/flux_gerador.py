"""
flux_gerador.py
---------------
Modulo de geracao de imagens via FLUX.1-schnell (Hugging Face).

Responsabilidades:
  - Gerenciar rodizio entre 5 tokens HF (conta 1, 40, 04, 05, 03)
  - Montar prompts variados via matriz: Tema -> Subtema -> Angulo -> Ambiente -> Horario
  - Retry inteligente: outro erro -> tenta 3x com pausa; cota excedida -> pula imediatamente
  - Retornar caminho da imagem gerada, ou None se todos os tokens falharem
"""

import os
import time
import random
import shutil
from datetime import datetime
from loguru import logger

# ============================================================
# TOKENS HF (5 contas em rodizio)
# ============================================================
HF_TOKENS = [
    os.getenv("HF_TOKEN_1"),
    os.getenv("HF_TOKEN_2"),
    os.getenv("HF_TOKEN_3"),
    os.getenv("HF_TOKEN_4"),
    os.getenv("HF_TOKEN_5"),
]
HF_TOKENS = [t for t in HF_TOKENS if t]

# Palavras-chave que identificam erro de cota excedida (pula imediatamente)
COTA_EXCEDIDA_KEYWORDS = ["zerogpu quota", "quota", "exceeded"]

# ============================================================
# POOL DE LOCAÇÕES BÍBLICAS E HISTÓRICAS
# ============================================================
_LOCACOES_BIBLICAS = [
    "Mount Sinai desert", "ancient Judean wilderness", "Garden of Gethsemane olive grove",
    "Sea of Galilee coast at dawn", "historic Jerusalem stone courtyard",
    "ancient monastery library in Cappadocia", "peaceful valley of Jezreel at sunrise",
    "mountaintop overlooking Jordan Valley", "ancient Roman stone aqueduct in Judea",
    "historic biblical desert canyon under stars"
]

# ============================================================
# POOL DE EFEITOS ATMOSFÉRICOS (Iluminação Sagrada e Luz Natural)
# ============================================================
_EFEITOS_ATMOSFERICOS = [
    "dramatic sunbeams penetrating through thick storm clouds, golden hour haze",
    "soft morning mist over desert mountains with warm ambient glow",
    "chiaroscuro lighting with deep warm natural window light and sharp realistic shadows",
    "gentle sunrise light filtering through ancient olive branches",
    "starry clear desert night sky with dramatic milky way and soft ambient twilight",
    "dramatic storm clouds breaking with golden light shining upon the valley",
    "soft dust particles illuminated by divine light ray through stone arches",
    "peaceful dawn with calm lake water reflections of mountain silhouettes"
]

# ============================================================
# POOL DE ÂNGULOS / PERSPECTIVAS
# ============================================================
_ANGULOS = [
    "wide establishing cinematic shot from a high mountain cliff at sunrise",
    "dramatic low angle looking up at a solitary figure standing firm on ancient stone",
    "intimate side profile chiaroscuro portrait with dramatic soft shadow",
    "close-up detail shot of hands resting on an ancient worn leather Bible with golden morning light",
    "atmospheric medium shot of a man deep in prayer in a quiet stone sanctuary illuminated by sunlight",
    "epic wide vista of a traveller walking through an expansive golden desert valley",
    "eye-level respectful shot of a historic wooden table with scripture scroll and natural sunlight"
]

# ============================================================
# MATRIZ DE SUBTEMAS CRISTÃOS — 100% CINEMATOGRÁFICO
# Tupla: (subtema, descricao_da_cena)
# ============================================================
_MATRIZ_PROMPTS = [
    # ── 1. ORAÇÃO & BLINDAGEM ESPIRITUAL NO SECRETO ──
    (
        "solitary prayer at sunrise mountain peak",
        "A devout man kneeling in prayer on an ancient rocky mountain summit at dawn. Golden sunbeams bursting through the horizon, creating a breathtaking spiritual atmosphere.",
    ),
    (
        "hands in prayer with divine light rays",
        "Close-up of weathered, strong praying hands holding an ancient wooden cross or resting on stone, illuminated by a single warm beam of heavenly morning sunlight from above.",
    ),
    (
        "quiet prayer room with morning sunlight",
        "A humble rustic stone room at dawn. A solitary person sitting quietly before a wooden table with morning sunbeams streaming through the stone window, deep in communion and peace.",
    ),

    # ── 2. SABEDORIA BÍBLICA & ESCRITURAS ANTIGAS ──
    (
        "ancient parchment scroll and vintage bible",
        "A historic wooden desk illuminated by warm natural morning light. An open vintage Bible with delicate aged pages, inkwell and an ancient scroll in sharp realistic detail.",
    ),
    (
        "classical ancient monastery library with sunlight",
        "A grand classical library with high stone archways, tall wooden bookshelves filled with ancient theological books, with morning sunbeams streaming across the stone floor.",
    ),
    (
        "thoughtful sage studying ancient scripture",
        "A wise, contemplative elder in traditional linen garments reading a holy scripture by soft natural window light, thoughtful facial expression, chiaroscuro lighting.",
    ),

    # ── 3. GUERRA ESPIRITUAL & SUPERAÇÃO NO DESERTO ──
    (
        "warrior standing firm in desert storm",
        "A resilient man in humble armor standing immovable against a dramatic desert storm. Storm clouds swirling behind him as golden light breaks from heaven.",
    ),
    (
        "walking through the valley of shadow into light",
        "A lone figure walking with courage through a dramatic narrow stone canyon toward an intensely glowing sunrise at the end of the path.",
    ),
    (
        "ancient shield and sword beside glowing altar",
        "An ancient weathered shield bearing a cross emblem resting against a stone altar, illuminated by sacred divine golden sunlight.",
    ),

    # ── 4. PAZ, DESCANSO & NATUREZA CONTEMPLATIVA ──
    (
        "peaceful olive grove at golden hour",
        "An ancient grove of gnarled olive trees bathed in warm golden hour light. Serene, peaceful breeze with grass and mountain backdrop.",
    ),
    (
        "calm waters and green pastures biblical valley",
        "A majestic calm river reflecting the morning sky, surrounded by green pastures and distant blue mountains, evoking the 23rd Psalm.",
    ),
    (
        "peaceful stone bridge over calm waters at dusk",
        "A historic stone arch bridge overlooking calm waters under a serene starry twilight sky and distant mountains.",
    ),
]


def gerar_imagem_flux(tipo: str, tema_escolhido: str = None, nome_arquivo: str = None):
    """
    Gera uma imagem via FLUX.1-schnell com rodizio de tokens e retry inteligente.

    Args:
        tipo: Tipo de post ('reels', 'reels_noite', 'story_manha', 'carousel')
        tema_escolhido: Tema do post (apenas para log, nao altera o visual)
        nome_arquivo: Caminho de saida. Se None, usa nome automatico.

    Returns:
        Caminho absoluto da imagem gerada, ou None se todos os tokens falharem.
    """
    try:
        from gradio_client import Client
    except ImportError:
        logger.warning("[FLUX] gradio_client nao instalado. Pulando geracao por IA.")
        return None

    # Dimensoes por tipo de post
    if tipo == "carousel":
        width, height = 2160, 1080
    else:  # reels, reels_noite, story_manha
        width, height = 1080, 1920

    # Seleciona subtema aleatoriamente a cada postagem (evita repeticao no mesmo dia)
    subtema, cena = random.choice(_MATRIZ_PROMPTS)

    # Seleciona locação bíblica, efeito atmosférico e ângulo aleatoriamente
    locacao = random.choice(_LOCACOES_BIBLICAS)
    efeito = random.choice(_EFEITOS_ATMOSFERICOS)
    angulo = random.choice(_ANGULOS)

    prompt = (
        f"Subject: authentic documentary scene, real human beings, {subtema}.\n"
        f"Environment: {locacao}.\n"
        f"{cena}\n"
        f"Atmosphere & Lighting: {efeito}, cinematic natural light.\n"
        f"Composition: {angulo}.\n"
        f"Visual Style: raw unedited 35mm photograph, shot on Kodak Portra 400, real human skin texture, pores, fine wrinkles, authentic natural fabric weave, ultra-sharp focus, cinematic depth of field, National Geographic style documentary portrait.\n"
        f"Negative constraints: candles, candlelight, wax candle, religious altar candles, no painting, no illustration, no drawing, no CGI, no 3D render, no cartoon, no anime, no smooth plastic skin, no digital art, no fake filters, no text, no watermark."
    )

    logger.info(f"[FLUX] Subtema: '{subtema}' | Locação: {locacao} | Efeito: {efeito[:30]}... | Dimensões: {width}x{height}")


    # Carrega estado para saber qual token usar a seguir
    try:
        from core.config.state import carregar_estado, salvar_estado
        estado = carregar_estado()
        idx_token_inicio = (estado.get("ultimo_hf_token_idx", -1) + 1) % len(HF_TOKENS)
    except Exception:
        estado = {}
        idx_token_inicio = 0

    # Tenta cada token em sequencia a partir do proximo apos o ultimo usado
    for i in range(len(HF_TOKENS)):
        idx_token = (idx_token_inicio + i) % len(HF_TOKENS)
        token = HF_TOKENS[idx_token]
        token_label = f"token {idx_token + 1}"

        # Define o token no ambiente para o gradio_client usar
        os.environ["HF_TOKEN"] = token

        MAX_TENTATIVAS = 3
        for tentativa in range(1, MAX_TENTATIVAS + 1):
            try:
                logger.info(f"[FLUX] Usando {token_label} (tentativa {tentativa}/{MAX_TENTATIVAS})...")

                client = Client("black-forest-labs/FLUX.1-schnell", token=token)
                result = client.predict(
                    prompt=prompt,
                    seed=random.randint(0, 2147483647),
                    randomize_seed=True,
                    width=float(width),
                    height=float(height),
                    num_inference_steps=4,
                    api_name="/infer"
                )

                # Extrai o caminho do arquivo gerado
                if isinstance(result, tuple):
                    caminho_temp = result[0]
                elif isinstance(result, dict):
                    caminho_temp = result.get("path") or result.get("url")
                else:
                    caminho_temp = result

                if isinstance(caminho_temp, dict):
                    caminho_temp = caminho_temp.get("path") or caminho_temp.get("url")

                if not caminho_temp or not os.path.exists(str(caminho_temp)):
                    raise ValueError(f"Caminho invalido retornado pelo FLUX: {caminho_temp}")

                # Copia para caminho definitivo
                if nome_arquivo is None:
                    import uuid
                    nome_arquivo = f"flux_bg_{uuid.uuid4().hex}.png"

                shutil.copy(str(caminho_temp), nome_arquivo)
                logger.success(f"[FLUX] Imagem gerada com sucesso via {token_label}! Arquivo: {nome_arquivo}")

                # Salva qual token foi o ultimo usado
                try:
                    estado["ultimo_hf_token_idx"] = idx_token
                    salvar_estado(estado)
                except Exception:
                    pass

                return os.path.abspath(nome_arquivo)

            except Exception as e:
                erro_str = str(e).lower()

                # Erro de cota: pula imediatamente para o proximo token
                if any(kw in erro_str for kw in COTA_EXCEDIDA_KEYWORDS):
                    logger.warning(f"[FLUX] {token_label}: cota excedida. Pulando para proximo token...")
                    break  # Sai do loop de tentativas, vai para o proximo token

                # Outro erro: aguarda e tenta novamente
                logger.warning(f"[FLUX] {token_label} tentativa {tentativa}: {e}")
                if tentativa < MAX_TENTATIVAS:
                    espera = random.randint(3, 5)
                    logger.info(f"[FLUX] Aguardando {espera}s antes de tentar novamente...")
                    time.sleep(espera)
                else:
                    logger.warning(f"[FLUX] {token_label}: esgotou {MAX_TENTATIVAS} tentativas. Pulando...")

    logger.error("[FLUX] Todos os tokens falharam. Acionando fallback (banco de imagens).")
    return None
