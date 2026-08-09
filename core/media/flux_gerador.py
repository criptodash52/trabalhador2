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
    os.getenv("HF_TOKEN_1", "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"),   # conta 1
    os.getenv("HF_TOKEN_2", "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"),   # conta 40
    os.getenv("HF_TOKEN_3", "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"),   # conta 04
    os.getenv("HF_TOKEN_4", "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"),   # conta 05
    os.getenv("HF_TOKEN_5", "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"),   # conta 03
]
HF_TOKENS = [t for t in HF_TOKENS if t]

# Palavras-chave que identificam erro de cota excedida (pula imediatamente)
COTA_EXCEDIDA_KEYWORDS = ["zerogpu quota", "quota", "exceeded"]

# ============================================================
# POOL DE CIDADES (variacao aleatoria a cada geracao)
# ============================================================
_CIDADES = [
    "Tokyo", "New York", "London", "Paris", "Shanghai",
    "Seoul", "Sao Paulo", "Chicago", "Hong Kong", "Amsterdam",
    "Berlin", "Bangkok", "Singapore", "Dubai", "Buenos Aires",
    "Mexico City", "Istanbul", "Toronto", "Sydney", "Milan",
]

# ============================================================
# POOL DE EFEITOS ATMOSFERICOS (um selecionado aleatoriamente)
# ============================================================
_EFEITOS_ATMOSFERICOS = [
    "light drizzle with wet reflections on the pavement",
    "heavy rain with water puddles reflecting neon lights",
    "dense urban fog with glowing halos around streetlights",
    "thin mist drifting between buildings",
    "light snowfall with snowflakes visible under streetlamps",
    "blizzard with snow swirling in the wind",
    "freezing fog with ice crystals in the air",
    "low-hanging storm clouds with distant lightning",
    "wet streets after rain with mirror-like reflections",
    "humid night air with visible condensation on glass surfaces",
]

# ============================================================
# POOL DE ANGULOS / PERSPECTIVAS (um selecionado aleatoriamente)
# ============================================================
_ANGULOS = [
    "shot from the rooftop of a skyscraper looking down at the streets below",
    "aerial view from a high-rise building terrace, looking down diagonally",
    "bird's-eye view from a drone hovering above the city",
    "shot from a high-floor apartment window looking down at the street",
    "top-down perspective from a pedestrian bridge above the scene",
    "low angle looking up at towering buildings disappearing into the fog",
    "eye-level shot on the street with deep perspective vanishing point",
    "shot through a rain-covered floor-to-ceiling glass window from inside a high floor",
    "counter-plunge angle from a fire escape high above the alley",
    "wide establishing shot from a rooftop edge at night",
]

# ============================================================
# MATRIZ DE SUBTEMAS - todos 100% noturnos
# Tupla: (subtema, descricao_da_cena)
# ============================================================
_MATRIZ_PROMPTS = [
    (
        "a person isolated in the middle of a crowd",
        "A busy urban avenue at night, hundreds of people walking in different directions, and only one person completely still, watching the crowd pass by.",
    ),
    (
        "isolation inside public transportation",
        "A crowded subway car at night. Everyone is physically close but each person is absorbed in their own world. One passenger stares out the window, distant from the others.",
    ),
    (
        "solitude caused by technology",
        "A busy cafe at night. Every table has at least one person, but all of them are staring at screens. No one talks. One person in the background looks around, searching for real connection.",
    ),
    (
        "solitude in a nocturnal work environment",
        "A glass corporate office at night. Only one person remains working, illuminated by a computer screen. The other floors of the building in the background are dark.",
    ),
    (
        "isolation surrounded by skyscrapers",
        "A person standing alone in the middle of an empty street between illuminated skyscrapers at night. The buildings rise in perspective toward the cloudy sky. The person stands motionless looking up.",
    ),
    (
        "solitude in urban relationships",
        "A couple at a sophisticated restaurant at night. Sitting face to face, but each one looking in opposite directions, lost in their own thoughts. The table is elegantly set, but the silence is palpable.",
    ),
    (
        "solitude in hyperconnectivity",
        "An urban bedroom at midnight. A person lying in bed, illuminated only by the glow of a phone screen. The window in the background shows the city that never sleeps, but the room is completely lonely.",
    ),
    (
        "urban anonymity at the subway station",
        "A crowded metro station at night. Hundreds of people move in different directions but none looks at another. One figure stands still, watching the human flow.",
    ),
    (
        "solitude facing the speed of the city",
        "A busy street at night captured with long exposure. Cars form trails of light in motion, people have become blurred shadows. Only one figure remains sharp, standing still in the middle of the chaos.",
    ),
    (
        "contrast between nature and urban solitude",
        "An urban park at night. Ancient trees line a stone path illuminated by lampposts. A person walks alone, small among the trees, while towering skyscrapers dominate the background skyline.",
    ),
    (
        "solitude in the rain on an empty bridge",
        "A pedestrian bridge over an urban river at night, pouring rain. A single figure leans on the railing looking at the city lights reflected in the water below. No one else is around.",
    ),
    (
        "watching the sleeping city from above",
        "A person standing alone on a rooftop terrace at night, looking out over an endless sea of city lights stretching to the horizon. Wind moves their clothes. The city is alive but indifferent.",
    ),
    (
        "solitude in a luxury hotel room",
        "A person standing at a floor-to-ceiling window of a high-rise hotel room at night, looking down at the illuminated city below. The room behind them is dark. They are surrounded by comfort but utterly alone.",
    ),
    (
        "the last one awake in the city",
        "A 24-hour diner at night, completely empty except for one customer sitting at the counter nursing a coffee. Through the window, the wet street reflects neon signs. The city outside is silent.",
    ),
    (
        "solitude in a night market",
        "A vibrant night market with colorful lanterns and food stalls. One person walks slowly through it alone, surrounded by strangers and noise, completely absorbed in their own thoughts.",
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

    # Seleciona subtema pelo dia do ano (rotacao automatica)
    dia_do_ano = datetime.now().timetuple().tm_yday
    idx_matriz = dia_do_ano % len(_MATRIZ_PROMPTS)
    subtema, cena = _MATRIZ_PROMPTS[idx_matriz]

    # Seleciona cidade, efeito atmosferico e angulo aleatoriamente (variacao por postagem)
    cidade = random.choice(_CIDADES)
    efeito = random.choice(_EFEITOS_ATMOSFERICOS)
    angulo = random.choice(_ANGULOS)

    prompt = (
        f"Theme: contemporary urban solitude. City: {cidade}, at night.\n"
        f"Subtheme: {subtema}.\n"
        f"{cena}\n"
        f"Atmospheric effect: {efeito}.\n"
        f"Camera angle: {angulo}.\n"
        f"Style: cinematic photography, realistic, 35mm camera, deep depth of field, "
        f"urban night lighting, golden and amber tones mixed with cool shadows, "
        f"Kodak Portra aesthetic, professional photographic quality, highly detailed textures.\n"
        f"No text, logos, watermarks or brands in the image."
    )

    logger.info(f"[FLUX] Subtema: '{subtema}' | Cidade: {cidade} | Efeito: {efeito[:30]}... | Dimensoes: {width}x{height}")


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

                client = Client("black-forest-labs/FLUX.1-schnell")
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
