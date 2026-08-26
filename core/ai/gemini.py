import json
import random
import time
import os
from google import genai
from datetime import datetime, timezone

from core.config.settings import GEMINI_KEYS, GROQ_KEYS, OPENROUTER_KEY
from core.ai.prompts import FONTES_SABEDORIA, montar_instrucoes_copy
from core.ai.styles import sortear_estilo
from core.ai.olhos_da_rede import gerar_contexto_mundo_real
from core.config.state import carregar_estado, salvar_estado
from core.analytics.leitor_pdf import ler_resumo_ultimo_pdf
from loguru import logger


def buscar_historico_por_tema(tema, tipo_post=None, limite=8):
    """
    Busca os últimos posts do mesmo TEMA no historico_posts do Firebase.
    Filtra e ordena NO PYTHON para evitar dependência de índices compostos
    do Firebase que geram erros 400 silenciosos e deixam a IA rodar cega.
    """
    try:
        from core.analytics.db import get_db
        db = get_db()
        if not db:
            return ""

        # Busca apenas pelo tema (índice simples — nunca gera erro 400)
        docs = db.collection("historico_posts") \
                 .where("tema", "==", tema) \
                 .limit(40).stream()
        todos = [doc.to_dict() for doc in docs]

        # Filtra por tipo no Python, sem depender do Firebase
        if tipo_post:
            todos = [p for p in todos if p.get("tipo") == tipo_post]

        # Ordena do mais recente ao mais antigo no Python
        todos.sort(key=lambda x: x.get("data", ""), reverse=True)
        posts_anteriores = todos[:limite]

        if not posts_anteriores:
            return ""

        msg = "\n        PROIBIDO REPETIR (HISTÓRICO DO TEMA):\n"
        msg += f"        O tema de hoje é '{tema}'. Veja abaixo o que já foi publicado nesse tema recentemente.\n"
        msg += "        Você DEVE criar algo completamente diferente — novas frases, novas metáforas, novos ângulos:\n"
        for i, p in enumerate(posts_anteriores):
            frase = p.get("frase_visual") or ""
            # frase_visual pode ser lista (slides) ou string
            if isinstance(frase, list):
                frase = " | ".join(str(s) for s in frase[:3])
            legenda_trecho = (p.get("legenda") or "")[:120]
            data = p.get("data", "")[:10]
            tipo_reg = p.get("tipo", "")
            if frase or legenda_trecho:
                msg += f"        * Post {i+1} ({data}) [{tipo_reg}]: Frase='{str(frase)[:150]}' | Legenda='{legenda_trecho}...'\n"
        msg += "        Qualquer semelhança com os textos acima é inaceitável. Seja 100% original.\n"
        return msg

    except Exception as e:
        logger.warning(f"Erro ao buscar histórico por tema '{tema}': {e}")
        return ""

def buscar_historico_reels_leads(limite=6):
    """
    Busca os últimos reels_leads gerados em 'historico_reels_leads' no Firebase.
    Ordena NO PYTHON para evitar o erro 400 de índice composto do Firebase.
    Retorna string de contexto para a IA não repetir os mesmos ganchos e frases.
    """
    try:
        from core.analytics.db import get_db
        db = get_db()
        if not db:
            return ""
        # Busca sem order_by para não precisar de índice composto no Firebase
        docs = db.collection("historico_reels_leads").limit(30).stream()
        posts = [doc.to_dict() for doc in docs]
        # Ordena do mais recente ao mais antigo no Python
        posts.sort(key=lambda x: x.get("data", ""), reverse=True)
        posts = posts[:limite]
        if not posts:
            return ""
        msg = "\n        PROIBIDO REPETIR (HISTÓRICO DOS ÚLTIMOS REELS DE LEADS):\n"
        msg += "        Estes são os roteiros de captação já publicados. Crie algo 100% diferente em gancho, ângulo e frases de encerramento/CTA:\n"
        for i, p in enumerate(posts):
            titulo = p.get("titulo_pdf", "")
            gancho = (p.get("gancho_fase1") or "")[:120]
            cta_fechamento = (p.get("cta_final") or "")[:120]
            data = p.get("data", "")[:10]
            msg += f"        * Reels {i+1} ({data}): PDF='{titulo}' | Gancho='{gancho}' | Convite Final Usado='{cta_fechamento}'\n"
        msg += "        Qualquer semelhança com os ganchos ou frases finais acima é inaceitável. Seja 100% original em todo o roteiro.\n"
        return msg
    except Exception as e:
        logger.warning(f"Erro ao buscar histórico de reels_leads: {e}")
        return ""


def _pos_processar_dados(dados, tipo, tema_escolhido, detalhes_tema, gancho_categoria="", tipo_cta="", duracao_video=0, subtema="", tom_emocional=""):
    """
    Funcao auxiliar para centralizar o pos-processamento dos dados gerados (IA ou Contingencia).
    Injeta as hashtags correspondentes na legenda e os metadados de analytics no dicionario.
    """
    # (Hashtags foram removidas da legenda a pedido do usuário)
    # Metadados internos para o sistema de analytics (prefixo _ indica uso interno)
    dados["_gancho_categoria"] = gancho_categoria
    dados["_tipo_cta"]         = tipo_cta
    dados["_duracao_video"]    = duracao_video
    dados["_subtema"]          = subtema
    dados["_tom_emocional"]    = tom_emocional

    # ── Truncador de segurança para imagens estáticas ──
    # A IA às vezes gera frases muito longas ignorando o limite pedido no prompt.
    # Para posts de imagem única (story), limitamos a 20 palavras
    # para garantir que o texto caiba no layout sem sobrepor o emblema ou a marca d'água.
    if tipo == "story" and "frase" in dados:
        frase_val = dados["frase"]
        if isinstance(frase_val, str):
            # Remove quebras de linha que a IA pode gerar
            frase_limpa = frase_val.replace("\n", " ").replace("\r", " ").strip()
            palavras = frase_limpa.split()
            if len(palavras) > 20:
                logger.warning(f"⚠️ [IA] Frase do {tipo} com {len(palavras)} palavras. AVISO: Ultrapassou o limite recomendado de 20.")
            dados["frase"] = frase_limpa

    # ── Truncador + normalizador para slides do story_tarde ──
    # O story_tarde usa o campo 'slides' (lista), não 'frase'.
    # Limita cada slide a 18 palavras e converte '\\n' literal (escape do JSON)
    # para '\n' real (quebra de linha Python), garantindo que o CTA seja
    # dividido em dois blocos visuais (topo e baixo) e que 'SABEDORIA' fique dourada.
    if tipo == "story_tarde" and "slides" in dados:
        slides_val = dados["slides"]
        if isinstance(slides_val, list):
            slides_normalizados = []
            ultimo_idx = len(slides_val) - 1
            penultimo_idx = ultimo_idx - 1
            for idx, s in enumerate(slides_val):
                # Converte \\n literal → \n real (vem assim do JSON do Gemini)
                s_norm = str(s).replace("\\n", "\n").strip()
                # NUNCA trunca o último slide (CTA) nem o penúltimo (Título PDF)
                if idx >= penultimo_idx:
                    slides_normalizados.append(s_norm)
                    continue
                palavras = s_norm.replace("\n", " ").split()
                if len(palavras) > 10:
                    logger.warning(f"⚠️ [IA] Slide do story_tarde com {len(palavras)} palavras. AVISO: Ultrapassou o limite de 10 palavras.")
                slides_normalizados.append(s_norm)
            dados["slides"] = slides_normalizados

    # ── Truncador + normalizador para slides do reels_leads ──
    # Limita cada slide de corpo (não o CTA nem o Título PDF) a 15 palavras máximas.
    if tipo == "reels_leads" and "slides" in dados:
        slides_val = dados["slides"]
        if isinstance(slides_val, list):
            slides_normalizados = []
            ultimo_idx = len(slides_val) - 1
            penultimo_idx = ultimo_idx - 1
            for idx, s in enumerate(slides_val):
                s_norm = str(s).replace("\\n", "\n").strip()
                # NUNCA trunca o último slide (CTA) nem o penúltimo (Título PDF)
                if idx >= penultimo_idx:
                    slides_normalizados.append(s_norm)
                    continue
                palavras = s_norm.replace("\n", " ").split()
                if len(palavras) > 10:
                    logger.warning(f"⚠️ [IA] Slide do reels_leads com {len(palavras)} palavras. AVISO: Ultrapassou o limite de 10 palavras.")
                slides_normalizados.append(s_norm)
            dados["slides"] = slides_normalizados

    return dados

def gerar_conteudo_gemini(tipo, custom_tema=None, custom_mensagem=None):
    # Calcula número de slides para stories de forma alternada a cada dia (3 em um dia, 4 no outro)
    dia_ano = datetime.now(timezone.utc).timetuple().tm_yday
    num_slides_story = 3 if dia_ano % 2 == 0 else 4

    if tipo == "test":
        logger.info("Gerando conteudo de teste estatico...")
        prompt_visual = "A serene sunset reflecting on a calm lake, warm golden hour, realistic photograph"
        logger.info(f"Cena cinematografica (test): {prompt_visual}")
        return {
            "frase": "Seja forte e corajoso. Nao se apavore nem desanime, pois o Senhor, o seu Deus, estara com voce por onde voce andar.",
            "legenda": "Ambiente de automacao inicializado com sucesso no GitHub Actions!\n\nEste e um teste integrado disparado pelo bot para validar as permissoes e notificacoes do sistema.\n\n#bot #instagram #automacao #dev",
            "prompt_imagem": prompt_visual
        }, "espiritualidade", "teste"
        
    logger.info(f"🤖 Solicitando texto ao Gemini para post do tipo: {tipo.upper()}...")
    if not GEMINI_KEYS and not GROQ_KEYS and not OPENROUTER_KEY:
        raise ValueError("Nenhuma chave de API (Gemini, Groq ou OpenRouter) está configurada! Por favor, adicione-as ao arquivo .env ou Secrets.")
        
    # --- INTEGRAÇÃO COM ANALYTICS CRUZADO (ROLETA VICIADA) E CONQUISTADOR ---
    estado = carregar_estado()
    tema_escolhido = custom_tema
    contexto_analytics = ""
    evitar_repeticao_msg = ""
    
    agora = datetime.now(timezone.utc)
    dia_hoje_str = agora.strftime("%Y-%m-%d")

    is_conquistador = False
    
    if not custom_tema:
        # Se for o primeiro post do dia, rotaciona o tema sequencialmente
        if estado.get("data_tema_do_dia") == dia_hoje_str and estado.get("tema_do_dia"):
            tema_escolhido = estado["tema_do_dia"]
            logger.info(f"🎲 Tema do dia continuado: {tema_escolhido}")
        else:
            temas_lista = [f["nome"] for f in FONTES_SABEDORIA]
            idx = estado.get("index_tema_diario", 0)
            if idx >= len(temas_lista): idx = 0
            
            tema_escolhido = temas_lista[idx]
            
            estado["tema_do_dia"] = tema_escolhido
            estado["data_tema_do_dia"] = dia_hoje_str
            estado["index_tema_diario"] = (idx + 1) % len(temas_lista)
            salvar_estado(estado)
            logger.info(f"🎲 Novo tema sequencial diário ativado: {tema_escolhido}")

    if not custom_tema:
        # Busca histórico deste TEMA em TODOS os formatos (anti-repetição unificada)
        # Isso evita que uma ideia publicada em vídeo apareça como carrossel no mesmo dia
        evitar_repeticao_msg = buscar_historico_por_tema(tema_escolhido, tipo_post=None, limite=10)
        if evitar_repeticao_msg:
            logger.info(f"📚 Histórico unificado do tema '{tema_escolhido}' carregado (todos os formatos).")

        # NOVO FLUXO: Lê diretamente o contexto mestre gerado pela IA Estrategista
        recomendacoes_file = "analytics/dados/recomendacoes.json"
        
        try:
            if os.path.exists(recomendacoes_file):
                with open(recomendacoes_file, "r", encoding="utf-8") as f:
                    rec_cruzada = json.load(f)
                
                # Monta um super contexto com toda a inteligência gerada pela IA estrategista
                contexto_analytics += "=== DIRETRIZES ESTRATÉGICAS DA SEMANA (IA) ===\n"
                
                if rec_cruzada.get("vibe_da_semana"):
                    contexto_analytics += f"VIBE DA SEMANA: {rec_cruzada['vibe_da_semana']}\n\n"
                
                if rec_cruzada.get("padroes_campeoes"):
                    contexto_analytics += f"PADRÕES QUE BOMBARAM (Replique isso): {rec_cruzada['padroes_campeoes']}\n\n"
                
                if rec_cruzada.get("ganchos_exclusivos"):
                    ganchos_str = "\n  - ".join(rec_cruzada["ganchos_exclusivos"])
                    contexto_analytics += f"GANCHOS INÉDITOS SUGERIDOS:\n  - {ganchos_str}\n\n"
                
                if rec_cruzada.get("ideias_de_narrativa"):
                    narrativas_str = "\n  - ".join(rec_cruzada["ideias_de_narrativa"])
                    contexto_analytics += f"IDEIAS DE NARRATIVA PARA EXPLORAR:\n  - {narrativas_str}\n\n"
                
                if rec_cruzada.get("aviso_estrategico"):
                    contexto_analytics += f"AVISO URGENTE DA IA ESTRATEGISTA: {rec_cruzada['aviso_estrategico']}\n\n"
                
                # Também adiciona o resumo clássico (fallback matemático / resumo final)
                contexto_analytics += f"RESUMO DO CONTEXTO: {rec_cruzada.get('contexto_para_gemini', '')}\n\n"
                
                logger.info("✅ Super Contexto estratégico (IA) injetado no prompt.")
                
                try:
                    from core.utils.contexto import registrar_contexto
                    registrar_contexto("analytics_ativo", True)
                    registrar_contexto("analytics_vibe", rec_cruzada.get("vibe_da_semana", ""))
                    registrar_contexto("analytics_padroes", rec_cruzada.get("padroes_campeoes", ""))
                except Exception as ctx_err:
                    logger.debug(f"Erro ao registrar contexto analytics: {ctx_err}")
        except Exception as e:
            logger.warning(f"Erro ao ler contexto estratégico (recomendacoes.json): {e}")

    # Sorteia sentimento a cada postagem — sem travar por data
    # Assim cada publicação do dia carrega uma cor emocional diferente
    sentimento_escolhido = None
    if not is_conquistador:
        from core.ai.styles import SENTIMENTOS_CONFIG
        hist_sentimentos = estado.get("historico_sentimentos", [])
        # Filtra sentimentos ainda não usados recentemente
        opcoes_sentimentos = [s for s in SENTIMENTOS_CONFIG.keys() if s not in hist_sentimentos]
        if not opcoes_sentimentos:  # Todos já foram usados: reseta e recomeça
            hist_sentimentos = []
            opcoes_sentimentos = list(SENTIMENTOS_CONFIG.keys())
        sentimento_escolhido = random.choice(opcoes_sentimentos)
        hist_sentimentos.append(sentimento_escolhido)
        estado["historico_sentimentos"] = hist_sentimentos[-10:]  # Guarda os últimos 10
        estado["sentimento_do_dia"] = sentimento_escolhido  # Mantém compatível com rest of code
        salvar_estado(estado)
        logger.info(f"🧠 Sentimento da postagem: {sentimento_escolhido.upper()} (varia a cada post)")
        
    detalhes_tema = {"nome": tema_escolhido}
    logger.info(f"✨ Tema que guiará o bot hoje: {detalhes_tema['nome']}")
    
    # ---------------- CICLO SEQUENCIAL DE GANCHOS E CTAs ----------------
    hist_angulos = estado.get("historico_angulos", [])
    hist_estilos = estado.get("historico_estilos", [])

    # Índices sequenciais: avançam 1 por postagem
    indice_gancho             = estado.get("indice_gancho", 0)
    indice_gancho_conquistador = estado.get("indice_gancho_conquistador", 0)
    indice_cta                = estado.get("indice_cta", 0)
    indice_arquitetura        = estado.get("indice_arquitetura", 0)

    # Seleciona o índice correto de gancho conforme o modo da postagem
    idx_atual = indice_gancho_conquistador if is_conquistador else indice_gancho

    # Monta instrucoes de copy (gancho sequencial + cta sequencial + arquitetura narrativa + ângulo anti-repetição)
    instrucoes_copy, sub_angulo, gancho, descricao_categoria, categoria_gancho, novo_indice, categoria_cta, referencia_cta, novo_indice_cta, arquitetura, novo_indice_arquitetura = montar_instrucoes_copy(
        contexto_analytics=contexto_analytics,
        historico_fontes=hist_angulos,
        indice_gancho=idx_atual,
        indice_cta=indice_cta,
        indice_arquitetura=indice_arquitetura,
        is_conquistador=is_conquistador,
        sentimento_escolhido=sentimento_escolhido
    )

    # Injeta o histórico do tema no instrucoes_copy → propagado automaticamente para TODOS os tipos de post
    if evitar_repeticao_msg:
        instrucoes_copy += evitar_repeticao_msg

    if custom_mensagem:
        instrucoes_copy += f"\n\n====================\nMENSAGEM E CONCEITO OBRIGATÓRIO SOLICITADO PELO USUÁRIO NO DASHBOARD:\n\"{custom_mensagem}\"\nVocê DEVE obrigatoriamente construir a postagem com base nesta mensagem/ideia do usuário.\n====================\n"
        logger.info(f"💬 [Studio de Criação] Mensagem do usuário injetada no prompt: {custom_mensagem[:60]}...")

    # Estilo de abordagem sorteado (com anti-repetição)
    estilo_escolhido = sortear_estilo(hist_estilos)
    logger.info(f"🎭 Estilo de abordagem sorteado: {estilo_escolhido.split(':')[0].upper()}")
    logger.info(f"🎣 Mecanismo Psicológico: {categoria_gancho.upper()} | Slide 1: \"{gancho}\"")
    logger.info(f"📐 Arquitetura narrativa: {arquitetura['nome']}")
    
    try:
        from core.utils.contexto import registrar_contexto
        registrar_contexto("sub_angulo", sub_angulo)
        registrar_contexto("gancho_abertura", gancho)
        registrar_contexto("arquitetura_nome", arquitetura.get('nome', ''))
        registrar_contexto("sentimento_post", sentimento_escolhido or "")
        registrar_contexto("estilo_escolhido", estilo_escolhido.split(':')[0].strip() if estilo_escolhido else "")
    except Exception as ctx_err:
        logger.debug(f"Erro ao registrar contexto estratégico: {ctx_err}")

    # Atualiza histórico de ângulos e estilos (mantém os últimos 25)
    hist_angulos.append(sub_angulo)
    hist_estilos.append(estilo_escolhido)

    estado["historico_angulos"] = hist_angulos[-25:]
    estado["historico_estilos"] = hist_estilos[-25:]

    # Avança o índice do gancho no estado (separado por modo)
    if is_conquistador:
        estado["indice_gancho_conquistador"] = novo_indice
    else:
        estado["indice_gancho"] = novo_indice

    # Define se esta postagem consome e avança o índice de CTA e Arquitetura
    tipos_com_cta = ["carousel", "reels", "pexels_story", "reels_noite", "pexels_story_noite"]
    if tipo in tipos_com_cta:
        estado["indice_cta"] = novo_indice_cta
        estado["indice_arquitetura"] = novo_indice_arquitetura
        logger.info(f"📣 CTA sequencial #{indice_cta}: [{categoria_cta.upper()}] -> '{referencia_cta}'")

    salvar_estado(estado)
    # --------------------------------------------------------------------

    # Instruções de livros já estão embutidas na Sabedoria Viva.
    instrucoes_livros = ""


    if tipo == "story":
        prompt = f"""
        Você cria Stories de Instagram direcionados estritamente para pessoas que JÁ TE SEGUEM (audiência quente).
        Sua comunicação deve ser uma CONVERSA ÍNTIMA, EXCLUSIVA, PROPOSITAL E DIRECIONAL.
        Estilo obrigatório para este story: {estilo_escolhido}

        CONTEXTO DO DIA (use como bússola de valor — não copie literalmente):
        - Tema do dia: {detalhes_tema['nome']}
        - Ângulo de inspiração: "{sub_angulo}"
        - Tom emocional do dia: {sentimento_escolhido.upper() if sentimento_escolhido else 'REFLEXÃO'}

        DIRETRIZ DE ESCRITA E PERCEPÇÃO DE VALOR:
        - Fale de igual para igual, como um mentor compartilhando uma percepção pessoal profunda do seu dia a dia.
        - O story deve parecer um pensamento que normalmente só surge depois de muita experiência observando pessoas e a própria vida.
        - Escreva como alguém que fala pouco, mas quando fala muda a forma como o leitor enxerga uma situação.
        - Evite frases prontas ou conselhos de autoajuda vazios. O objetivo deixa de ser "motivação" e passa a ser "lucidez".
        - Escreva uma única frase curta e com altíssimo impacto emocional (entre 10 e 15 palavras) que gere uma pequena mudança de perspectiva.
        - NÃO use "..." de forma automática — use no máximo 1 vez por sequência, somente quando criar tensão real.
        - NÃO use ponto de exclamação. Use ponto final ou interrogação.
        - NÃO inclua CTA, convite para seguir ou qualquer chamada para ação.
        
        Responda APENAS em formato JSON válido assim:
        {{
          "frase": "Sua frase de conversa íntima com seu seguidor aqui"
        }}
        """
    elif tipo == "story_manha":
        prompt = f"""
        Você cria uma sequência de Stories de Instagram matinais de alta autoridade para sua audiência.
        Sua missão é entregar uma PÍLULA DE SABEDORIA MATINAL em pequena dose: clara, elevada, inspiradora e sem nenhum tom carrancudo ou pesado.
        Estilo obrigatório para esta sequência: {estilo_escolhido}

        CONTEXTO DO DIA (use como bússola de valor — não copie literalmente):
        - Tema do dia: {detalhes_tema['nome']}
        - Ângulo de inspiração: "{sub_angulo}"
        - Tom emocional do dia: {sentimento_escolhido.upper() if sentimento_escolhido else 'REFLEXÃO'}

        CRIE UMA SEQUÊNCIA DE EXATAMENTE {num_slides_story} FRASES CURTAS CONECTADAS (ENTRE 10 E 15 PALAVRAS POR FRASE):
        - SLIDE 1 (GANCHO CURTO DE AUTORIDADE): Abra com uma frase curta, elegante e provocativa de liderança (entre 10 e 15 palavras). Deve despertar curiosidade e posicionar autoridade imediata.
        - SLIDES INTERMEDIÁRIOS (ENTREGA DE VALOR PRÁTICO): Desenvolva uma pílula diária de sabedoria ou mentalidade baseada no ângulo acima. O conteúdo deve parecer um pensamento maduro e de alta lucidez, sem frases prontas.
        - SLIDE FINAL (DIREÇÃO E AUTORIDADE): Feche com uma síntese de autoridade moral que dê direção clara, lucidez e posicionamento firme para o dia.
        - PROIBIDO usar tom pesado, vitimista, cansado ou de autoajuda barata.
        - NÃO inclua CTA, convite para seguir ou qualquer chamada para ação.
        - Não use ponto de exclamação.
        - Escolha se quer usar música de fundo ou não no story (true ou false) de acordo com o tom da conversa.
        
        PERCEPÇÃO DE VALOR DO STORY:
        - Cada slide deve ser formulado para entregar valor real para quem te segue (audiência quente).
        - A autoridade do story deve vir exclusivamente da profundidade do raciocínio prático, gerando uma pequena mudança de perspectiva a quem consome.
        
        Responda APENAS em formato JSON válido assim (o array 'frase' DEVE ter EXATAMENTE {num_slides_story} itens):
        {{
          "frase": [
            "Slide 1 (Gancho curto de autoridade)",
            "Slide 2 (Pílula de valor prático)",
            "Slide {num_slides_story} (Síntese e direção de liderança)"
          ],
          "usar_musica": true
        }}
        """
    elif tipo == "story_tarde":
        resumo_pdf_tarde = ler_resumo_ultimo_pdf() or "Nenhum PDF encontrado. Construa o roteiro com base nos princípios filosóficos e de crescimento pessoal."
        titulo_pdf_tarde = "Material da Semana"
        bot_path_tarde = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        caminho_pdf_tarde = os.path.join(bot_path_tarde, "gerador_pdf", "output", "ultimo_conteudo.json")
        if os.path.exists(caminho_pdf_tarde):
            try:
                import json as _json
                with open(caminho_pdf_tarde, "r", encoding="utf-8") as _f:
                    _dados_pdf_tarde = _json.load(_f)
                titulo_pdf_tarde = _dados_pdf_tarde.get("titulo_pdf", "Material da Semana")
            except Exception as _e:
                logger.warning(f"Erro ao carregar PDF para story_tarde: {_e}")

        SINONIMOS_MODULO = ["guia devocional", "estudo bíblico", "mapa de oração", "manual de sabedoria", "devocional", "caderno de reflexão"]
        sinonimo_modulo = random.choice(SINONIMOS_MODULO)

        VARIACOES_CTA_TARDE = [
            f"Se você ainda não pegou o seu devocional desta semana, comente 'ORACAO' que te envio no Direct. \\n Receba o seu {sinonimo_modulo} para blindar sua fé.",
            f"Liberamos um {sinonimo_modulo} inédito para você. Comente 'ORACAO' para receber no Direct. \\n Fortaleça sua caminhada e seu propósito diário.",
            f"Sabedoria bíblica para aplicar no seu dia a dia. Comente 'SABEDORIA' e receba o {sinonimo_modulo}. \\n Edifique a sua casa e a sua mente com a Palavra.",
            f"Toda semana preparamos um {sinonimo_modulo} para enriquecer seu devocional. Comente 'ORACAO'. \\n Receba o material completo diretamente no seu Direct.",
            f"Para aprofundar seu momento com Deus hoje, comente 'ORACAO'. \\n Receba o seu {sinonimo_modulo} em instantes no Direct.",
        ]
        cta_tarde = random.choice(VARIACOES_CTA_TARDE)

        prompt = f"""
        Você é um mentor cristão e estrategista de conteúdo do perfil @valoresdopai.
        Sua função é criar uma sequência de STORIES em vídeo para sua comunidade — pessoas que buscam crescimento espiritual, oração e sabedoria bíblica.
        Elas te acompanham e confiam no seu ministério. Seu trabalho é criar uma mensagem que toque o coração e apresente o devocional desta semana como bênção para a caminhada delas.

        ═══════════════════════════════════════════════════
        DIFERENÇA FUNDAMENTAL DE AUDIÊNCIA:
        Esta NÃO é uma audiência fria. A pessoa já te acompanha.
        Portanto: tom acolhedor, bíblico e direto ao ponto.
        Fale como um pastor ou conselheiro sábio que traz uma palavra de encorajamento e direção.
        A confiança já existe — use-a para edificar vidas e direcionar à oração.
        ═══════════════════════════════════════════════════

        MATERIAL DA SEMANA (CENTRO DE TODA A NARRATIVA):
        - Título: "{titulo_pdf_tarde}"
        - Conteúdo resumido: {resumo_pdf_tarde[:350]}

        ═══════════════════════════════════════════════════
        DIRETRIZ ESPIRITUAL (injete com reverência):
        - A paz duradoura nasce da entrega a Deus e da obediência à Sua Palavra.
        - Não há batalha que resista à constância da oração no secreto.
        - Princípios bíblicos trazem clareza para decisões difíceis e guardam o coração.
        ═══════════════════════════════════════════════════

        ANTES DE ESCREVER, DEFINA INTERNAMENTE (não precisa aparecer no JSON):
        1. Qual é a dor ou dilema espiritual que este material acolhe?
        2. Qual promessa bíblica traz alívio e firmeza para o leitor?
        3. Por que este guia devocional é essencial para o momento que ele vive hoje?

        ═══════════════════════════════════════════════════
        ESTRUTURA OBRIGATÓRIA DA SEQUÊNCIA (5 OU 6 SLIDES):
        ═══════════════════════════════════════════════════

        SLIDE 1 — PARAR E RECONHECER (MÁXIMO 8 a 10 palavras):
        OBJETIVO COMPORTAMENTAL: fazer o seguidor pausar e sentir a relevância espiritual para a sua vida.
        Abra com uma reflexão bíblica ou observação de fé profunda.
        LIMITE ESTRITO: No máximo 8 a 10 palavras. DEVE caber em exatamente 2 ou 3 linhas na tela.
        Sem exclamação. Sem clichê vazio.

        SLIDES 2 e 3 — REVELAR E APROFUNDAR (MÁXIMO 8 a 10 palavras por slide):
        OBJETIVO COMPORTAMENTAL: trazer discernimento espiritual sobre cansaço, ansiedade, família ou decisões.
        Aponte o princípio das Escrituras que traz refúgio e clareza.
        LIMITE ESTRITO: No máximo 8 a 10 palavras por slide.
        PROIBIDO: tom acusatório, legalismo ou superficialidade.

        SLIDE 4 — A PONTE PARA O MATERIAL:
        OBJETIVO COMPORTAMENTAL: apresentar o estudo ou guia devocional como apoio para a vida devocional do seguidor.
        Frase de convite super enxuta (MÁXIMO 6 a 8 palavras). Modelo: "Para aprofundar sua oração, acesse o guia da semana."
        Em seguida, o título exato do material: "{titulo_pdf_tarde}".
        Se a frase + título ultrapassar 12 palavras: OBRIGATÓRIO dividir em 2 slides (Slide 4 = convite curto, Slide 5 = Título do PDF).

        SLIDE FINAL — CTA DIRETO (MÁXIMO 10 a 12 PALAVRAS NO TOTAL, dividido por \\n):
        OBJETIVO COMPORTAMENTAL: tornar a ação simples e imediata.
        Parte 1 (ANTES de \\n): no máximo 5 a 6 palavras. Modelo: "Comente 'ORACAO' para receber no Direct."
        Parte 2 (DEPOIS de \\n): no máximo 5 a 6 palavras. Modelo: "Receba o guia devocional desta semana."
        REGRA INEGOCIÁVEL: A soma de palavras da Parte 1 + Parte 2 NÃO PODE ultrapassar 12 palavras no total.

        ═══════════════════════════════════════════════════
        REGRAS ABSOLUTAS:
        ═══════════════════════════════════════════════════
        - Tom: sereno, pastoral, acolhedor e firme.
        - Foco em edificar a fé, a família e a oração.
        - PROIBIDO: chavões vazios ou tom mercadológico apelativo.
        - Não use "..." mais de uma vez na sequência inteira.

        PEXELS/PIXABAY QUERY:
        Crie queries cinemáticas no tema CONTEMPLAÇÃO, PAZ E NATUREZA BÍBLICA.
        Exemplos: "peaceful sunrise mountains golden hour cinematic" ou "ancient candle lighting open bible warm light"

        LEGENDA (3 a 4 linhas):
        - Reflexão edificante e breve sobre o estudo da semana.
        - Termine com variação natural do CTA. Exemplo: "Comente 'ORACAO' que te envio o devocional no Direct 👇"
        - NÃO inclua hashtags.

        Responda APENAS em formato JSON válido (o array 'slides' DEVE ter 5 ou 6 itens, o último com \\n):
        {{
          "cta_keyword": "ORACAO",
          "slides": [
            "Slide 1 — Reflexão bíblica que faz o seguidor pausar e refletir.",
            "Slide 2 — Traz clareza espiritual e descanso para a alma.",
            "Slide 3 — Revela a promessa e a direção de Deus para o momento.",
            "Slide 4 — Preparei um estudo completo sobre isso no {sinonimo_modulo} desta semana: {titulo_pdf_tarde}.",
            "Slide 5 (CTA) — Comente 'ORACAO' para receber direto no Direct. \\n Edifique a sua fé e seu momento devocional."
          ],
          "pexels_queries": [
            "peaceful sunrise mountains golden hour cinematic",
            "ancient candle lighting open bible warm light"
          ],
          "legenda": "Uma palavra de paz e direcionamento para sua semana. Comente 'ORACAO' que te envio o devocional no Direct 👇"
        }}
        """
    elif tipo == "carousel":
        prompt = f"""
        Você cria Carrosséis de Instagram com narrativa progressiva, ganchos magnéticos e contrastes cortantes.
        Estilo obrigatório para este carrossel: {estilo_escolhido}

        {instrucoes_copy}{instrucoes_livros}

        1. TÍTULO DA CAPA (máximo 6 palavras):
        - O título da capa deve ser construído DIRETAMENTE a partir do gancho sorteado nas instruções acima.
        - Adapte o gancho de referência ({descricao_categoria}) para um título curto e provocativo que force o clique.
        - Formatos aceitos:
          * Afirmação chocante curta: "O preço que você não vê."
          * Pergunta que agride: "Por que você faz isso de novo?"
          * Paradoxo: "Quanto mais você corre, mais parado fica."
          * Declaração de identidade: "Dois tipos de pessoa. Qual é você?"
        - PROIBIDO: títulos com "dicas", "aprenda a", "como fazer", "passos para", "top X".

        2. SLIDES DE CONTEÚDO (entre 5 e 8 slides — o número DEVE variar a cada postagem. NÃO use sempre o máximo. Escolha livremente entre 5, 6, 7 ou 8 conforme a necessidade da mensagem):
        - Cada slide: frase curtíssima e cirúrgica de no entre 10 e 15 palavras (ideal: entre 5 e 8). Sem rodeios.
        - PROIBIDO usar "..." em todo slide — use no máximo 1 vez por carrossel, somente quando criar tensão real.
        - A sequência dos slides deve seguir esta arquitetura narrativa FLUIDA:

          SLIDE 1 — GANCHO (Pattern Interrupt):
          Adapte o gancho de referência '{gancho}' ao ângulo do post. Frase curta, cortante, que para o scroll.
          Deve usar a estrutura do formato: {descricao_categoria}

          SLIDES 2-3 — ABERTURA DE LOOP (Efeito Zeigarnik):
          Abra um ciclo de curiosidade sem fechá-lo. Aprofunde a provocação do gancho.
          O leitor deve sentir que precisa virar o slide para descobrir o que vem a seguir.
          PROIBIDO entregar a solução aqui.

          SLIDES 4-5 — DOR DO COTIDIANO (Identificação visceral):
          Nomeie a dor concreta e reconhecível do dia a dia do leitor.
          Seja específico. O leitor deve pensar: "Isso sou eu. Exatamente."
          Bata na ferida antes de curar.

          SLIDES 6-7 (se houver) — VIRADA E INSIGHT:
          Entregue a verdade prática ou o contraste que muda a perspectiva.
          Uma lição crua, madura, aplicável. Sem moralismo barato.
          Exemplos de formato: "Nem todo afastamento é perda. Alguns é só livramento."
                               "Pra cobrar de 10 a 10, você não pode ser nove e meio."

          SLIDE FINAL — XEQUE-MATE:
          Frase reflexiva e poderosa para o leitor guardar mentalmente.
          Deve criar o desejo de salvar ou compartilhar. Feche com impacto, sem conclusão bonita e embalada.

        VALOR PERCEBIDO DO CARROSSEL (OBRIGATÓRIO):
        - Cada slide deve aumentar a sensação de que o leitor está entendendo um mecanismo oculto.
        - Não explique apenas "o que fazer".
        - Explique primeiro: por que isso acontece, qual é o erro invisível, qual princípio resolve esse erro.
        - O conhecimento deve parecer difícil de encontrar, mas fácil de entender depois da explicação.

        INSPIRAÇÃO LENDÁRIA DE NARRATIVA (Use como tempero de altíssimo impacto e epicidade):
        Você pode canalizar esta energia épica e mitológica de grande jornada e legado para construir ganchos ou desfechos memoráveis:
        "Riqueza, liberdade, poder. Os mestres e empreendedores que dominaram o mercado e conquistaram sua liberdade descobriram algo que mudou suas vidas para sempre. Antes de se retirarem dos holofotes, deixaram um único recado: 'Querem os resultados que conquistamos? Eles estão disponíveis para quem estiver disposto a aprender. Todo o conhecimento necessário foi deixado no mundo. Agora cabe a você encontrá-lo.' E assim começou a nova era dos que possuem sonhos inegociáveis."
        Use esta aura de mistério, sabedoria e busca por maestria para dar densidade e peso ao texto.

        3. LEGENDA:
        - Reforce a provocação do carrossel em 3-4 linhas usando linguagem direta e madura.
        - CTA OBRIGATÓRIO: A legenda DEVE terminar com a chamada para ação (CTA) adaptada conforme a 'DIRETRIZ OBRIGATÓRIA DE CTA' enviada nas instruções.
        - NUNCA termine com uma conclusão fechada. O leitor deve ter algo a dizer.
        - NÃO inclua hashtags.

        ATENÇÃO: O "titulo" da capa DEVE ser diferente do Slide 1. O título é uma frase curta de impacto (máx 6 palavras). O Slide 1 é o gancho completo. Não repita o mesmo texto nos dois.

        Responda APENAS em formato JSON válido assim (slides deve ter entre 5 e 8 itens — varie o número, não use sempre 8):
        {{
          "titulo": "Título curto da capa (máx 6 palavras)",
          "slides": [
            "Slide 1 — Gancho (Pattern Interrupt)",
            "Slide 2 — Abertura de loop",
            "Slide 3 — Aprofunda o loop",
            "Slide 4 — Dor do cotidiano",
            "Slide 5 — Xeque-mate reflexivo"
          ],
          "legenda": "Sua legenda completa aqui sem hashtags"
        }}
        """
    elif tipo == "reels":
        prompt = f"""
        Você é a Máquina de Construção de Curiosidade. Seu objetivo é criar um roteiro em slides que faça o usuário PARAR de rolar o feed e assistir até o final.
        Estilo obrigatório para este Reels: {estilo_escolhido}

        {instrucoes_copy}{instrucoes_livros}

        CRIE UMA SEQUÊNCIA NARRATIVA EXATA DE 6 SLIDES seguindo rigorosamente a estrutura oficial de 6 Fases (Nicholas Boothman):

        - Slide 1 / Fase 1 (Interrupção Mental - 0-2s): O Gancho/Quebra de Padrão. Nunca comece afirmando. Sempre comece criando uma lacuna mental com uma pergunta ou mistério irresistível. Use as fórmulas de ganchos: "Você acredita que...", "Existe uma mentira...", "Ninguém percebe que...", "O maior erro...", "Quase todo mundo...". (entre 10 e 15 palavras)
        - Slide 2 / Fase 2 (Identificação - 2-6s): Conexão direta com o espectador. Ele deve pensar: "Isso é sobre mim". Fale diretamente com o leitor usando "você", nunca "as pessoas". (entre 10 e 15 palavras)
        - Slide 3 / Fase 3 (Quebra de expectativa - 6-12s): Tensão e surpresa que mudam o rumo esperado. Use fórmulas como: "Mas o problema não é esse.", "Na verdade acontece exatamente o contrário.", "É aqui que quase todos erram.". (entre 10 e 15 palavras)
        - Slide 4 / Fase 4 (Desenvolvimento do Raciocínio): Desenvolva a ideia com lógica. Cada slide responde ao anterior. Entregue lucidez. (entre 10 e 15 palavras)
        - Slide 5 / Fase 5 (Reflexão - 25-35s): Frase memorável e inesquecível de altíssimo impacto (Xeque-mate). (entre 10 e 15 palavras)
        - Slide 6 / Fase 6 (Convite Invisível): CTA sutil que faz a pessoa pensar e agir em sua própria vida, sem pedir para seguir diretamente. Use fórmulas como: "Amanhã você vai tentar controlar tudo outra vez. Observe isso.", "Repare nisso durante o dia.", "Pense nisso antes de dormir.". (entre 10 e 15 palavras)

        REGRAS DE ESCRITA E RITMO VISUAL:
        * Todas as frases devem ser curtas, cortantes e limpas.
        * NÃO use pontos de exclamação.
        * PROIBIDO usar "..." de forma automática.

        LEGENDA:
        - Máximo 3 linhas. Foco em complementar a reflexão em tom direto.
        - NÃO inclua hashtags.

        Responda APENAS em formato JSON válido assim (deve ter exatamente 6 slides):
        {{
          "slides": [
            "Slide 1 (Interrupção Mental - Gancho)",
            "Slide 2 (Identificação - Foco no você)",
            "Slide 3 (Quebra de Expectativa)",
            "Slide 4 (Revelação)",
            "Slide 5 (Reflexão Memorável)",
            "Slide 6 (Convite Invisível)"
          ],
          "legenda": "Sua legenda aqui sem hashtags"
        }}
        """

    elif tipo == "reels_conquistador":
        prompt = f"""
        Você é o porta-voz de uma identidade viva e real. Não tenta convencer ninguém.
        Declara quem é — com densidade, coerência e autenticidade de quem viveu o que diz.
        {evitar_repeticao_msg}

        ===== PERSONA OBRIGATÓRIA: O CONQUISTADOR =====
        Esta é a essência que deve atravessar cada palavra:

        Fe profunda — nao como performance religiosa, mas como ancora interior e convicção de que ha proposito em tudo.
        Foco inabalavel — quem sabe para onde vai, nao se distrai com o que nao constroi.
        Iluminação — a busca continua por enxergar alem do obvio, do superficial e do imediato.
        Sabedoria — nao acumulo de informação, mas discernimento conquistado com experiencia e silencio.
        Espirito aventureiro — o conforto nunca foi o objetivo. A vida foi feita para ser vivida com ousadia.
        Batalhador — nao ha vitoria sem construção. Nao ha construção sem disciplina silenciosa e diaria.
        Sonhador — quem para de sonhar começa a encolher. O sonho e o combustivel da ação.
        Amante da liberdade — liberdade real nao e ausencia de responsabilidade, e fidelidade aos proprios valores.
        Valores familiares — familia e o fundamento. O que se conquista tem que ter raiz e legado.
        Amoroso — força e afeto nao se contradizem. O homem que ama com profundidade e o que mais cresce.
        Pensador — antes de agir, reflete. Antes de falar, pensa. A lentidao do raciocinio e virtude.
        Criador — a existencia pede que se construa algo com as maos, com a mente, com a alma.
        Conquistador — nao de pessoas, mas de versoes cada vez mais elevadas de si mesmo.
        Culto e estudioso — o livro, o silencio e a observação sao os melhores professores.
        Curioso — quem para de perguntar para de crescer.
        Criterioso — nao aceita tudo. Filtra com inteligencia. Escolhe com principio.
        Pontual e afetivo — respeito pelo tempo alheio e presença genuina nas relações.
        Visionario — enxerga o que ainda nao existe, mas que pode ser construido.
        ================================================

        CRIE UMA SEQUÊNCIA NARRATIVA DE 6 SLIDES que seja um MANIFESTO DE IDENTIDADE.
        Nao siga o modelo de curiosidade. Nao crie ganchos de suspense. Nao tente vender nada.
        Declare. Afirme. Construa com palavras.

        REGRAS DE ESTILO OBRIGATÓRIAS:
        - Tom: denso, intimo, real — como uma conversa entre pessoas que se respeitam
        - Cada slide deve parecer uma convicção vivida, nao uma frase motivacional generica
        - PROIBIDO frases de autoajuda vazias (ex: "acredite em voce", "seja sua melhor versao")
        - PROIBIDO qualquer CTA, convite para seguir, convite invisivel ou pergunta reflexiva
        - PROIBIDO ponto de exclamação
        - PROIBIDO "..." automatico — use no maximo 1 vez por sequencia, somente quando criar tensao real
        - Os slides podem variar: alguns curtos (5 a 8 palavras), outros mais densos (ate 14 palavras)
        - O arco narrativo deve ter coerencia: comeca com declaração, aprofunda com valor, termina com sentença firme

        EXEMPLOS DE TOM (nao copie — inspire-se):
        - "Nao persigo o sucesso. Construo quem precisa ser para merece-lo."
        - "A liberdade que busco nao e ausencia de compromisso. E fidelidade a mim mesmo."
        - "Fe nao e esperar que tudo de certo. E agir como se soubesse que dara."
        - "Familia nao e o que voce encontra. E o que voce decide proteger todos os dias."

        UNIVERSO VISUAL OBRIGATÓRIO:
        Queries em inglês evocando a estética de Solidão Urbana Contemporânea: cidades grandes à noite, arranha-céus, luzes urbanas vibrantes, iluminação dourada/âmbar, atmosfera 35mm.
        PROIBIDO: cenas de estádio de futebol, lutas, festas com bebidas, deserto ou praia diurna.
        (ex: contemporary urban solitude night city lights 35mm, modern skyscraper rooftop night golden light, city lights reflections wet street 4k)

        Responda APENAS em formato JSON valido assim:
        {{
          "pexels_queries": [
            "contemporary urban solitude night city lights 35mm",
            "modern skyscraper rooftop night golden light cinematic",
            "city lights reflections wet street 4k"
          ],
          "slides": [
            "Texto do Slide 1 (Declaracao de identidade)",
            "Texto do Slide 2 (Valor vivido)",
            "Texto do Slide 3 (Aprofundamento)",
            "Texto do Slide 4 (Convicção central)",
            "Texto do Slide 5 (Sentenca de sabedoria)",
            "Texto do Slide 6 (Fechamento firme — sem CTA)"
          ],
          "legenda": "Maximo 2 linhas. Extensao natural do manifesto. Sem hashtags. Sem CTA."
        }}
        """

    elif tipo == "pexels_story":
        prompt = f"""
        Você é a Máquina de Construção de Curiosidade adaptada para Stories com vídeo único e cinematográfico de fundo.
        Sua missão é criar uma narrativa limpa, envolvente e de alto impacto em um vídeo de fundo contínuo.
        Estilo obrigatório: {estilo_escolhido}

        {instrucoes_copy}{instrucoes_livros}

        CRIE UMA SEQUÊNCIA NARRATIVA DE 3 A 4 SLIDES que conduza o espectador por uma curva emocional completa:

        - Slide 1 (Gancho de Parada no Feed): Frase curta e impactante que prende imediatamente. Comece com: "Você acredita que...", "Existe uma mentira...", "Ninguém percebe que...", "O maior erro...", "Quase todo mundo...". (entre 10 e 15 palavras)
        - Slide 2 (Desenvolvimento do Raciocínio): Desenvolva a ideia iniciada no Slide 1 de forma lógica e progressiva. (entre 10 e 15 palavras)
        - Slide 3 (Revelação ou Insight): Insight simples, prático e marcante de psicologia ou filosofia. (entre 10 e 15 palavras)
        - Slide 4 (Encerramento — OPCIONAL): Frase de fechamento firme, sem CTA, sem convite para seguir. (entre 10 e 15 palavras)

        PEXELS QUERY — UM ÚNICO VÍDEO DE FUNDO CONTÍNUO:
        Crie UMA ÚNICA query em inglês de alta especificidade para encontrar o vídeo mais épico e de alta frequência possível:
        - Iluminação brilhante, luzes de palco, shows, luxo moderno ou amanhecer épico (stadium lights, modern luxury, sunrise golden hour, high energy crowd)
        - Estilo visual de altíssima qualidade (4k cinematic, premium lifestyle)
        - Prefira: palcos, carros de luxo em movimento, líderes caminhando, multidões vibrando.

        LEGENDA:
        - Máximo 3 linhas. SEM HASHTAGS.

        Responda APENAS em formato JSON válido assim:
        {{
          "slides": [
            "Slide 1 (Gancho)",
            "Slide 2 (Identificação)",
            "Slide 3 (Revelação)"
          ],
          "pexels_queries": [
            "stadium concert crowd lights cinematic 4k"
          ],
          "legenda": "Sua legenda aqui sem hashtags"
        }}
        """

    elif tipo == "reels_noite":
        prompt = f"""
        Você é a Máquina de Construção de Curiosidade no horário noturno (18h). Seu objetivo é capturar a atenção de quem está exausto do dia.
        Estilo obrigatório: {estilo_escolhido}

        {instrucoes_copy}{instrucoes_livros}

        CRIE UMA SEQUÊNCIA NARRATIVA EXATA DE 6 SLIDES seguindo rigorosamente a estrutura oficial de 6 Fases (Nicholas Boothman):

        - Slide 1 / Fase 1 (Interrupção Mental - 0-2s): Gancho inicial noturno curioso (ex: "Existe uma mentira que te contaram sobre o cansaço..."). Comece com: "Você acredita que...", "Existe uma mentira...", "Ninguém percebe que...", "O maior erro...", "Quase todo mundo...". (entre 10 e 15 palavras)
        - Slide 2 / Fase 2 (Identificação - 2-6s): Identificação imediata (ex: "Você chega em casa e sente que..."). Fale com "você". (entre 10 e 15 palavras)
        - Slide 3 / Fase 3 (Desenvolvimento): Desenvolva o raciocínio. (entre 10 e 15 palavras)
        - Slide 4 / Fase 4 (Explicação Lógica): Traga lucidez filosófica que responda ao conflito gerado. (entre 10 e 15 palavras)
        - Slide 5 / Fase 5 (Reflexão - 25-35s): Frase marcante sobre governar a mente. (entre 10 e 15 palavras)
        - Slide 6 / Fase 6 (Convite Invisível): Provocação silenciosa para a noite do leitor. (entre 10 e 15 palavras)

        LEGENDA:
        - Máximo 3 linhas.
        - SEM HASHTAGS.

        Responda APENAS em formato JSON válido assim:
        {{
          "slides": [
            "Slide 1 (Gancho)",
            "Slide 2 (Identificação)",
            "Slide 3 (Quebra)",
            "Slide 4 (Revelação)",
            "Slide 5 (Reflexão)",
            "Slide 6 (Convite)"
          ],
          "legenda": "Sua legenda aqui sem hashtags"
        }}
        """

    elif tipo == "pexels_story_noite":
        prompt = f"""
        Você é a Máquina de Construção de Curiosidade noturna (19h-21h) para Stories com vídeo único de fundo.
        Seu objetivo é criar um arco de descoberta mental e insight libertador em um vídeo de fundo elegante e contínuo.
        Estilo obrigatório: {estilo_escolhido}

        {instrucoes_copy}{instrucoes_livros}

        CRIE UMA SEQUÊNCIA NARRATIVA DE 3 A 4 SLIDES para a noite — tom sereno, denso e reflexivo:

        - Slide 1 (Gancho Noturno): Frase desafiadora e misteriosa que prende quem está no final do dia. Comece com: "Você acredita que...", "Existe uma mentira...", "Ninguém percebe que...", "O maior erro...", "Quase todo mundo...". (entre 10 e 15 palavras)
        - Slide 2 (Identificação Íntima): Foco em "você", tom próximo e noturno. (entre 10 e 15 palavras)
        - Slide 3 (Revelação ou Insight Noturno): Insight simples e profundo, ideal para refletir ao deitar. (entre 10 e 15 palavras)
        - Slide 4 (Encerramento — OPCIONAL): Frase final serena e firme, sem CTA. (entre 10 e 15 palavras)

        PEXELS QUERY — UM ÚNICO VÍDEO DE FUNDO NOTURNO (MAS DE ALTA FREQUÊNCIA):
        Crie UMA ÚNICA query em inglês de alta especificidade para o melhor vídeo noturno premium e inspirador:
        - Festas exclusivas, eventos noturnos, luzes de cidade vibrantes, celebrações de luxo (premium night event, luxury city lights, exclusive celebration, high end lifestyle night)
        - Textura cinematográfica moderna (4k cinematic night, vibrant city lights)
        - Prefira: luzes vibrantes de cidade moderna, celebrações, ambientes premium iluminados.

        LEGENDA:
        - Máximo 3 linhas. SEM HASHTAGS.

        Responda APENAS em formato JSON válido assim:
        {{
          "slides": [
            "Slide 1 (Gancho noturno)",
            "Slide 2 (Identificação íntima)",
            "Slide 3 (Revelação)"
          ],
          "pexels_queries": [
            "luxury city night lights premium event 4k cinematic"
          ],
          "legenda": "Sua legenda aqui sem hashtags"
        }}
        """

    elif tipo == "reels_leads":
        resumo_pdf = ler_resumo_ultimo_pdf() or "Nenhum PDF anterior encontrado. Crie um roteiro genérico focando em 'Hábitos Inquebráveis'."
        evitar_repeticao_leads = buscar_historico_reels_leads(limite=6)
        if evitar_repeticao_leads:
            logger.info("📚 Histórico de reels_leads carregado para anti-repetição.")

        titulo_pdf_limpo = "Material Exclusivo"
        solucao_pdf_limpo = "Método Prático"

        bot_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        caminho_arquivo = os.path.join(bot_path, "gerador_pdf", "output", "ultimo_conteudo.json")
        if os.path.exists(caminho_arquivo):
            try:
                with open(caminho_arquivo, "r", encoding="utf-8") as f:
                    dados_pdf = json.load(f)
                titulo_pdf_limpo = dados_pdf.get("titulo_pdf", "Material Exclusivo")
                plano = dados_pdf.get("plano_acao", {})
                solucao_pdf_limpo = plano.get("subtitulo", "Método Prático")
            except Exception as e:
                logger.warning(f"Erro ao obter titulo e solucao do PDF: {e}")

        # ── Rotação sequencial dos 5 pilares visuais cristãos ────────────────
        PILARES_VISUAIS_LEADS = [
            {
                "nome": "Oração & Blindagem Espiritual",
                "exemplo_query": "peaceful sunrise mountains praying hands light through clouds cinematic",
                "descricao": "amanhecer com luz dourada, mãos em oração, montanhas serenas, céu bíblico majestoso",
            },
            {
                "nome": "Sabedoria Bíblica & Antiguidade",
                "exemplo_query": "ancient library vintage scripture candle glowing light warm atmosphere 4k",
                "descricao": "escrituras antigas, pergaminhos, velas, arquitetura clássica, ambiente de sabedoria e estudo",
            },
            {
                "nome": "Guerra Espiritual & Superação",
                "exemplo_query": "dramatic storm warrior shield fire light breaking through darkness cinematic",
                "descricao": "tempestade imponente, fogo na forja, passos firmes no deserto, guerreiro revestido da armadura de Deus",
            },
            {
                "nome": "Paz & Alívio da Tempestade",
                "exemplo_query": "calm lake after storm warm sunset light reflection peaceful nature 4k",
                "descricao": "mar calmo após a tempestade, luz suave do entardecer, descanso e tranquilidade da alma",
            },
            {
                "nome": "Família, Honra e Legado",
                "exemplo_query": "father embracing family golden hour field olive tree warm sunlight",
                "descricao": "família unida, campos de oliveiras, abraço protetor, pôr do sol dourado, sacerdócio no lar",
            },
        ]
        estado_leads = carregar_estado()
        idx_pilar = estado_leads.get("index_pilar_reels_leads", 0) % len(PILARES_VISUAIS_LEADS)
        pilar_atual = PILARES_VISUAIS_LEADS[idx_pilar]
        estado_leads["index_pilar_reels_leads"] = (idx_pilar + 1) % len(PILARES_VISUAIS_LEADS)
        salvar_estado(estado_leads)
        pilar_nome = pilar_atual["nome"]
        pilar_exemplo = pilar_atual["exemplo_query"]
        pilar_descricao = pilar_atual["descricao"]
        logger.info(f"🎨 [REELS_LEADS] Pilar visual #{idx_pilar+1} forçado: {pilar_nome.upper()}")
        # ─────────────────────────────────────────────────────────────────────

        # ── Sorteio declarado do mecanismo persuasivo ─────────────────────────
        MECANISMOS_PERSUASIVOS = [
            {
                "nome": "IDENTIDADE EM CRISTO",
                "descricao": "Desperta a consciência de filho de Deus e sacerdote do lar. Mostra a diferença entre viver pelo padrão do mundo e viver segundo o propósito do Reino.",
                "exemplo_gancho": "Você não foi chamado para se conformar com este mundo.",
            },
            {
                "nome": "CONTRASTE ESPIRITUAL",
                "descricao": "Coloca dois caminhos lado a lado. Mostra que o esforço humano sem a bênção de Deus é apenas cansaço, mas com Deus há descanso e vitória.",
                "exemplo_gancho": "Dois homens podem enfrentar o mesmo deserto. Um murmura; o outro é forjado.",
            },
            {
                "nome": "SABEDORIA OCULTA",
                "descricao": "Apresenta um princípio bíblico profundo que a maioria ignora na correria do dia a dia, gerando fome por revelação.",
                "exemplo_gancho": "Existe um princípio em Provérbios que guarda a sua casa de ruínas.",
            },
            {
                "nome": "REFÚGIO & ALÍVIO",
                "descricao": "Remove o peso da culpa e convida o leitor a entregar as cargas nas mãos de Deus em oração sincera.",
                "exemplo_gancho": "O seu cansaço não é falta de força física; é sobrecarga na alma.",
            },
            {
                "nome": "VIGILÂNCIA & GUERRA",
                "descricao": "Convoca o homem/mulher de fé a guardar as portas do lar e revestir-se da armadura de Deus contra as armadilhas espirituais.",
                "exemplo_gancho": "Se você não blindar a sua mente no secreto, o mundo roubará a sua paz.",
            },
        ]
        idx_mecanismo = estado_leads.get("index_mecanismo_reels_leads", 0) % len(MECANISMOS_PERSUASIVOS)
        mecanismo_atual = MECANISMOS_PERSUASIVOS[idx_mecanismo]
        estado_leads["index_mecanismo_reels_leads"] = (idx_mecanismo + 1) % len(MECANISMOS_PERSUASIVOS)
        salvar_estado(estado_leads)
        mecanismo_nome = mecanismo_atual["nome"]
        mecanismo_descricao = mecanismo_atual["descricao"]
        mecanismo_gancho = mecanismo_atual["exemplo_gancho"]
        logger.info(f"🧠 [REELS_LEADS] Mecanismo persuasivo #{idx_mecanismo+1}: {mecanismo_nome}")
        # ─────────────────────────────────────────────────────────────────────

        prompt = f"""
        Você é um mentor cristão e comunicador bíblico de alta autoridade para o perfil @valoresdopai.
        Sua função é criar um REEL em vídeo de alta retenção voltado a pessoas que buscam fortalecimento espiritual, sabedoria bíblica e direção em oração.

        ═══════════════════════════════════════════════════
        MECANISMO PERSUASIVO DESTA GERAÇÃO: {mecanismo_nome}
        {mecanismo_descricao}
        Exemplo de gancho para este mecanismo: "{mecanismo_gancho}"
        VOCÊ DEVE CONSTRUIR TODA A SEQUÊNCIA USANDO EXCLUSIVAMENTE ESTE MECANISMO.
        ═══════════════════════════════════════════════════

        MATERIAL DA SEMANA (ESTUDO DEVOCIONAL / GUIA BÍBLICO):
        - Título: "{titulo_pdf_limpo}"
        - Solução Prática: "{solucao_pdf_limpo}"
        - Contexto: {resumo_pdf[:300]}

        {evitar_repeticao_leads}

        ═══════════════════════════════════════════════════
        FILOSOFIA BÍBLICA:
        - A verdadeira autoridade nasce da oração e da submissão a Deus.
        - As tempestades da vida refinam o caráter dos justos.
        - Quem edifica sua casa sobre a Rocha não é abalado pelos ventos.
        ═══════════════════════════════════════════════════

        ANTES DE ESCREVER, DEFINA INTERNAMENTE (não precisa aparecer no JSON):
        1. A única verdade bíblica que este Reel vai proclamar (uma frase).
        2. A reflexão ou convicção de fé que cada slide precisa provocar.
        3. A condução lógica ao guia devocional da semana como ferramenta de oração.

        ═══════════════════════════════════════════════════
        ESTRUTURA OBRIGATÓRIA DOS SLIDES (6 OU 7 SLIDES):
        ═══════════════════════════════════════════════════

        SLIDE 1 — PARAR O SCROLL (MÁXIMO 8 a 10 palavras):
        OBJETIVO: prender a atenção com verdade bíblica incisiva.
        Use o mecanismo {mecanismo_nome} desde o início.
        LIMITE ESTRITO: No máximo 8 a 10 palavras. DEVE caber em exatamente 2 ou 3 linhas.

        SLIDES 2 e 3 — IDENTIFICAÇÃO ESPIRITUAL (MÁXIMO 8 a 10 palavras por slide):
        OBJETIVO: tocar na dor, no deserto ou no dilema de fé com acolhimento.
        Descreva situações reais do dia a dia da pessoa.
        LIMITE ESTRITO: No máximo 8 a 10 palavras por slide.

        SLIDE 4 — DIREÇÃO BÍBLICA: A REVELAÇÃO (MÁXIMO 8 a 10 palavras):
        OBJETIVO: apontar para a soberania, a graça ou o princípio bíblico que resolve a questão.

        SLIDE 5 — CONVITE AO ESTUDO DEVOCIONAL:
        OBJETIVO: apresentar o guia da semana como bênção.
        Frase de convite super enxuta (MÁXIMO 6 a 8 palavras). Exemplo: "Preparei um estudo profundo sobre isso:"
        Apresente o nome EXATO do material: "{titulo_pdf_limpo}".
        Se ultrapassar 12 palavras no total: OBRIGATÓRIO dividir em 2 slides (Slide 5 = convite, Slide 6 = Título).

        SLIDE FINAL — CTA DE ORAÇÃO (MÁXIMO 10 a 12 PALAVRAS NO TOTAL, dividido por \\n):
        Parte 1 (ANTES de \\n): no máximo 5 a 6 palavras. Modelo: "Comente 'ORACAO' para receber no Direct."
        Parte 2 (DEPOIS de \\n): no máximo 5 a 6 palavras. Modelo: "Receba o guia devocional completo."
        REGRA INEGOCIÁVEL: A soma de palavras da Parte 1 + Parte 2 NÃO PODE ultrapassar 12 palavras.

        ═══════════════════════════════════════════════════
        REGRAS ABSOLUTAS:
        ═══════════════════════════════════════════════════
        - Tom: sóbrio, pastoral, firme, de profunda autoridade cristã.
        - PROIBIDO: chavões mercadológicos, promessas vazias ou sensacionalismo.
        - Use ponto final ou interrogação. Não use exclamações.

        PEXELS QUERY — PILAR VISUAL OBRIGATÓRIO: "{pilar_nome}"
        A PRIMEIRA query do array pexels_queries DEVE ser: '{pilar_exemplo}'
        As demais complementam o mesmo universo visual: {pilar_descricao}.

        LEGENDA (3 a 4 linhas):
        - Breve reflexão pastoral sobre o tema.
        - Termine com variação do CTA. Exemplo: "Comente 'ORACAO' que te envio o devocional no Direct 👇"
        - NÃO inclua hashtags.

        Responda APENAS em formato JSON válido (o array 'slides' DEVE conter 6 OU 7 frases, a última com \\n):
        {{
          "cta_keyword": "ORACAO",
          "slides": [
            "Gancho bíblico com mecanismo {mecanismo_nome}.",
            "Identificação da batalha de fé que o leitor enfrenta.",
            "Aprofundamento com acolhimento pastoral e clareza.",
            "Princípio da Palavra que traz luz e direção.",
            "Preparei um estudo completo sobre isso:",
            "{titulo_pdf_limpo}.",
            "Comente 'ORACAO' para receber no Direct. \\n Fortaleça sua vida devocional e sua fé."
          ],
          "pexels_queries": [
            "{pilar_exemplo}",
            "praying hands morning light mountains biblical landscape cinematic",
            "ancient scriptures vintage book light dust particles 4k"
          ],
          "legenda": "Uma palavra de sabedoria e fé para edificar sua caminhada. Comente 'ORACAO' que te envio o devocional no Direct 👇"
        }}
        """
    else:
        raise ValueError(f"Tipo inválido: {tipo}")

    # [NOVO] Adiciona a exigência dos 5 novos metadados na raiz do JSON, independente do tipo de post
    prompt += """
    MUITO IMPORTANTE: Além da estrutura exigida acima, você DEVE retornar as seguintes 5 chaves NA RAIZ do seu JSON:
    - "objetivo": O objetivo principal deste post (ex: "Educar", "Vender", "Inspirar", "Entreter")
    - "categoria_imagem": A estética visual sugerida (ex: "Minimalista", "Cores Quentes", "Texto Dinâmico", "B-roll")
    - "categoria_musica": A vibração sonora sugerida (ex: "Lofi", "Phonk", "Acústico", "Misterioso", "Sem Música")
    - "estrutura_narrativa": A forma como a história é contada (ex: "Problema-Solução", "Lista", "Storytelling", "Ameaça-Alívio")
    - "complexidade": O nível intelectual do conteúdo ("Baixa", "Média", "Alta")
    """

    # Função auxiliar para extrair JSON de markdown
    def extrair_json(texto):
        # Remove blocos markdown (```json ... ```) e eventuais espaços
        import re
        texto = texto.strip()
        padrao = r'```(?:json)?\s*(.*?)\s*```'
        match = re.search(padrao, texto, re.DOTALL)
        if match:
            texto = match.group(1)
        # Tenta parsear
        return json.loads(texto)

    # LOOP DE TENTATIVAS (Múltiplas chaves)
    max_tentativas_por_chave = 3
    
    for key_index, current_key in enumerate(GEMINI_KEYS):
        logger.info(f"Tentando usar chave Gemini {key_index + 1}/{len(GEMINI_KEYS)}...")
        client = genai.Client(api_key=current_key)
        
        for tentativa in range(max_tentativas_por_chave):
            try:
                # Tenta modelo gemini-2.5-flash ou gemini-3.6-flash (para novas contas do Google AI Studio)
                try:
                    resposta = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                except Exception as e_mod:
                    if "not found" in str(e_mod).lower() or "404" in str(e_mod):
                        resposta = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
                    else:
                        raise e_mod
                
                # Extração e parse robusto
                try:
                    dados = extrair_json(resposta.text)
                except Exception as e:
                    logger.error(f"Erro ao parsear JSON na Tentativa {tentativa+1}. Texto bruto: {resposta.text}")
                    raise Exception(f"Gemini nao retornou um JSON valido: {e}")
                
                # Pos-processamento centralizado
                dados = _pos_processar_dados(
                    dados, tipo, tema_escolhido, detalhes_tema,
                    gancho_categoria=descricao_categoria, tipo_cta=categoria_cta,
                    subtema=sub_angulo, tom_emocional=estilo_escolhido
                )
                    
                return dados, tema_escolhido, estilo_escolhido
                
            except Exception as e:
                err_msg = str(e).lower()
                if "429" in err_msg or "resource_exhausted" in err_msg or "quota" in err_msg:
                    logger.warning(f"⚠️ Cota esgotada na chave {key_index + 1} (429). Passando para a próxima chave...")
                    break # Sai do loop de tentativas e vai para a próxima chave
                
                if tentativa < max_tentativas_por_chave - 1:
                    logger.warning(f"⚠️ Erro ao chamar Gemini (Chave {key_index + 1}, Tentativa {tentativa+1}/{max_tentativas_por_chave}): {e}. Tentando novamente em 5 segundos...")
                    time.sleep(5)
                else:
                    logger.error(f"❌ Falha ao obter resposta na chave {key_index + 1} após {max_tentativas_por_chave} tentativas.")
                    
    # Se sair do loop do Gemini, todas as chaves falharam.
    logger.warning("⚠️ Gemini esgotado. Tentando GROQ (llama-3.3-70b)...")

    # ─── FALLBACK 1: GROQ ───
    for groq_index, groq_key in enumerate(GROQ_KEYS):
        logger.info(f"🔑 Tentando usar chave Groq {groq_index + 1}/{len(GROQ_KEYS)}...")
        try:
            import requests as _req
            groq_resp = _req.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 4096, "temperature": 0.9},
                timeout=60
            )
            if groq_resp.status_code == 200:
                texto_groq = groq_resp.json()["choices"][0]["message"]["content"]
                dados = extrair_json(texto_groq)
                # Pos-processamento centralizado
                dados = _pos_processar_dados(
                    dados, tipo, tema_escolhido, detalhes_tema,
                    gancho_categoria=descricao_categoria, tipo_cta=categoria_cta,
                    subtema=sub_angulo, tom_emocional=estilo_escolhido
                )
                logger.success(f"✅ [GROQ] Conteúdo gerado com sucesso pela chave {groq_index + 1}!")
                return dados, tema_escolhido, estilo_escolhido
            elif groq_resp.status_code == 429:
                logger.warning(f"⚠️ Groq chave {groq_index + 1}: cota esgotada. Tentando próxima...")
            else:
                logger.warning(f"⚠️ Groq chave {groq_index + 1}: erro HTTP {groq_resp.status_code}.")
        except Exception as e:
            logger.warning(f"⚠️ Groq chave {groq_index + 1} falhou: {str(e)[:100]}")

    # ─── FALLBACK 2: OPENROUTER ───
    if OPENROUTER_KEY:
        logger.warning("⚠️ Groq esgotado. Tentando OpenRouter (GPT-4o-mini)...")
        try:
            import requests as _req
            or_resp = _req.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
                json={"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "max_tokens": 4096},
                timeout=60
            )
            if or_resp.status_code == 200:
                texto_or = or_resp.json()["choices"][0]["message"]["content"]
                dados = extrair_json(texto_or)
                # Pos-processamento centralizado
                dados = _pos_processar_dados(
                    dados, tipo, tema_escolhido, detalhes_tema,
                    gancho_categoria=descricao_categoria, tipo_cta=categoria_cta,
                    subtema=sub_angulo, tom_emocional=estilo_escolhido
                )
                logger.success("✅ [OPENROUTER] Conteúdo gerado com sucesso!")
                return dados, tema_escolhido, estilo_escolhido
            else:
                logger.warning(f"⚠️ OpenRouter falhou: HTTP {or_resp.status_code} - {or_resp.text[:100]}")
        except Exception as e:
            logger.warning(f"⚠️ OpenRouter falhou: {str(e)[:100]}")

    # ─── FALLBACK FINAL: MENSAGENS DE EMERGÊNCIA ───
    logger.warning("🚨 [SAÍDA DE EMERGÊNCIA] Todos os provedores falharam. Carregando post estático de contingência...")
    try:
        emergencia_file = "core/ai/mensagens_emergencia.json"
        if os.path.exists(emergencia_file):
            with open(emergencia_file, "r", encoding="utf-8") as f:
                emergencias = json.load(f)
            
            # Identifica o tema e normaliza
            tema_key = tema_escolhido.lower() if tema_escolhido else "superacao"
            if tema_key not in emergencias:
                tema_key = "superacao"
                
            # Mapeia os tipos de postagens para as chaves principais do JSON (story, reels, carousel)
            tipo_key = "story"
            if tipo in ["reels", "reels_noite", "pexels_story", "pexels_story_noite", "reels_leads"]:
                tipo_key = "reels"
            elif tipo == "carousel":
                tipo_key = "carousel"
            
            # Sorteia uma das mensagens prontas
            lista_opcoes = emergencias.get(tema_key, {}).get(tipo_key, [])
            if lista_opcoes:
                import copy
                # Faz cópia para não alterar o dicionário original carregado em memória
                dados = copy.deepcopy(random.choice(lista_opcoes))
                
                # Pos-processamento centralizado
                dados = _pos_processar_dados(
                    dados, tipo, tema_escolhido, detalhes_tema,
                    gancho_categoria=descricao_categoria, tipo_cta=categoria_cta,
                    subtema=sub_angulo, tom_emocional=estilo_escolhido
                )
                
                logger.success(f"🛡️ [SAÍDA DE EMERGÊNCIA] Mensagem de contingência recuperada para Tema: {tema_key.upper()} | Formato: {tipo_key.upper()}")
                return dados, tema_escolhido, estilo_escolhido
                
    except Exception as e_emergencia:
        logger.error(f"❌ Erro grave no sistema de emergência: {e_emergencia}")

    raise ValueError(f"❌ Falha crítica: Todas as {len(GEMINI_KEYS)} chaves do Gemini falharam ou estão sem cota.")

