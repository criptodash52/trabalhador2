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
    # Para posts de imagem única (story e story_tarde), limitamos a 20 palavras
    # para garantir que o texto caiba no layout sem sobrepor o emblema ou a marca d'água.
    if tipo in ["story", "story_tarde"] and "frase" in dados:
        frase_val = dados["frase"]
        if isinstance(frase_val, str):
            # Remove quebras de linha que a IA pode gerar
            frase_limpa = frase_val.replace("\n", " ").replace("\r", " ").strip()
            palavras = frase_limpa.split()
            if len(palavras) > 20:
                logger.warning(f"⚠️ [IA] Frase do {tipo} com {len(palavras)} palavras. Truncando para 20.")
                dados["frase"] = " ".join(palavras[:20]) + "..."
            else:
                dados["frase"] = frase_limpa
        elif isinstance(frase_val, list):
            # Para listas (story_tarde com 2 frases), limita cada item
            frases_limpas = []
            for f in frase_val:
                f_limpa = str(f).replace("\n", " ").replace("\r", " ").strip()
                palavras = f_limpa.split()
                if len(palavras) > 20:
                    logger.warning(f"⚠️ [IA] Frase do {tipo} (lista) com {len(palavras)} palavras. Truncando para 20.")
                    frases_limpas.append(" ".join(palavras[:20]) + "...")
                else:
                    frases_limpas.append(f_limpa)
            dados["frase"] = frases_limpas

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

    is_conquistador = (tipo == "reels_conquistador")
    
    if is_conquistador and not custom_tema:
        # Loop Cego: Ignora o Analytics e roda pelos 8 temas em sequência
        temas_lista = [f["nome"] for f in FONTES_SABEDORIA]
        idx = estado.get("index_conquistador", 0)
        if idx >= len(temas_lista): idx = 0
            
        tema_escolhido = temas_lista[idx]
        
        # Avança pro próximo dia
        estado["index_conquistador"] = (idx + 1) % len(temas_lista)
        salvar_estado(estado)
        logger.info(f"🎯 [CONQUISTADOR] Tema forçado pelo ciclo: {tema_escolhido}")

        # Busca histórico DESTE TEMA para evitar repetição de mensagens no Conquistador
        evitar_repeticao_msg = buscar_historico_por_tema(tema_escolhido, tipo_post="reels_conquistador", limite=6)
    elif not custom_tema:
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

        # NOVO FLUXO: Ciclo sequencial diário
        recomendacoes_file = "analytics/dados/recomendacoes.json"
        recomendacoes_semanais_file = "analytics/dados/recomendacoes_semanais.json"
        
        # Lê o contexto do analytics cruzado (diário/múltiplos períodos)
        try:
            if os.path.exists(recomendacoes_file):
                with open(recomendacoes_file, "r", encoding="utf-8") as f:
                    rec_cruzada = json.load(f)
                contexto_analytics += rec_cruzada.get("contexto_para_gemini", "") + "\n\n"

                # --- Fase 6: Injeção de Growth Score, ICC e Hipóteses Confirmadas ---
                gs_ref = rec_cruzada.get("growth_score_referencia", 0)
                if gs_ref > 0:
                    contexto_analytics += f"GROWTH SCORE DE REFERENCIA DA CONTA: {gs_ref:.4f}\n"
                    contexto_analytics += "  (Este e o benchmark atual. Posts acima deste valor impulsionam crescimento real.)\n\n"

                icc = rec_cruzada.get("icc_por_tema", {})
                if icc:
                    tema_icc_lider = max(icc, key=icc.get)
                    contexto_analytics += f"TEMA COM MAIOR ICC (converte curiosidade em seguidores): {tema_icc_lider.upper()} ({icc[tema_icc_lider]:.1%})\n\n"

        except Exception as e:
            logger.warning(f"Erro ao ler contexto do analytics cruzado: {e}")

        # Injeta hipóteses confirmadas da Memória Estratégica
        try:
            from core.analytics.motor_hipoteses import obter_hipoteses_confirmadas
            hipoteses = obter_hipoteses_confirmadas()
            if hipoteses:
                contexto_analytics += "CONHECIMENTO ESTRATEGICO VALIDADO (hipoteses confirmadas com dados reais):\n"
                for h in hipoteses[:5]:  # Limita a 5 para não inflar o prompt
                    contexto_analytics += f"  - {h['hipotese']} (Confianca: {h.get('confianca', 0):.0%}, Amostra: {h.get('amostra', 0)} posts)\n"
                contexto_analytics += "\n"
        except Exception:
            pass  # Motor ainda não rodou; ignora silenciosamente

        # Lê o contexto do analytics semanal (tendências)
        try:
            if os.path.exists(recomendacoes_semanais_file):
                with open(recomendacoes_semanais_file, "r", encoding="utf-8") as f:
                    rec_semanal = json.load(f)
                contexto_analytics += rec_semanal.get("contexto_para_gemini", "") + "\n\n"
        except Exception as e:
            logger.warning(f"Erro ao ler contexto do analytics semanal: {e}")

        # [NOVO] Adiciona a visão externa (Olhos da Rede)
        try:
            # Pega o nome do tema escolhido para fazer uma busca cirúrgica no YouTube
            nome_do_tema_atual = tema_escolhido.split(" (")[0]
            mundo_real = gerar_contexto_mundo_real(dias=7, tema_especifico=nome_do_tema_atual)
            if mundo_real:
                contexto_analytics += "\n====================\n" + mundo_real + "\n====================\n\n"
        except Exception as e:
            logger.warning(f"Erro ao coletar Olhos da Rede: {e}")

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
    tipos_com_cta = ["carousel", "reels", "reels_conquistador", "pexels_story", "reels_noite", "pexels_story_noite"]
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
        prompt = f"""
        Você cria uma sequência de Stories de Instagram para o período da tarde focada em clareza, maestria e autoridade.
        Sua missão é entregar uma dose diária de valor prático para ajustar a rota do dia, com tom sereno, firme e refinado (sem peso ou postura carrancuda).
        Estilo obrigatório para esta sequência: {estilo_escolhido}

        CONTEXTO DO DIA (use como bússola de valor — não copie literalmente):
        - Tema do dia: {detalhes_tema['nome']}
        - Ângulo de inspiração: "{sub_angulo}"
        - Tom emocional do dia: {sentimento_escolhido.upper() if sentimento_escolhido else 'REFLEXÃO'}

        CRIE UMA SEQUÊNCIA DE EXATAMENTE {num_slides_story} FRASES CURTAS CONECTADAS (ENTRE 5 E 8 PALAVRAS POR FRASE):
        PROIBIDO usar "..." de forma repetitiva — use no máximo 1 vez por sequência, somente quando criar tensão real.
        - SLIDE 1 (GANCHO CURTO DE TRANSIÇÃO): Abra com uma frase instigante sobre foco, discernimento ou maestria diante dos ruídos do dia (entre 10 e 15 palavras).
        - SLIDES INTERMEDIÁRIOS (PÍLULA DE CONHECIMENTO): Entregue uma sacada prática de sabedoria baseada no ângulo acima. Cada frase deve parecer um pensamento que normalmente só surge após muita experiência de vida, evitando frases clichê.
        - SLIDE FINAL (SÍNTESE DE AUTORIDADE): Encerre posicionando autoridade moral e lucidez, inspirando o leitor a concluir o dia com maestria e foco em seus princípios.
        - PROIBIDO tom de reclamação, cansaço excessivo, vitimismo ou conselhos óbvios.
        - NÃO inclua CTA, convite para seguir ou qualquer chamada para ação.
        - Não use ponto de exclamação.
        - Escolha se quer usar música de fundo ou não (true ou false).
        
        PERCEPÇÃO DE VALOR DO STORY:
        - Cada slide deve ser formulado para entregar valor real para quem te segue (audiência quente).
        - A autoridade do story deve vir exclusivamente da profundidade do raciocínio prático, gerando uma pequena mudança de perspectiva a quem consome.
        
        Responda APENAS em formato JSON válido assim (o array 'frase' DEVE ter EXATAMENTE {num_slides_story} itens):
        {{
          "frase": [
            "Slide 1 (Gancho curto de maestria)",
            "Slide 2 (Pílula de sabedoria prática)",
            "Slide {num_slides_story} (Síntese de autoridade)"
          ],
          "usar_musica": false
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

        2. SLIDES DE CONTEÚDO (entre 5 e 8 slides — o número exato deve variar livremente conforme a necessidade da mensagem):
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

        Responda APENAS em formato JSON válido assim (slides deve ter entre 5 e 8 itens):
        {{
          "titulo": "Título da capa aqui",
          "slides": [
            "Slide 1 — Gancho adaptado do sistema",
            "Slide 2 — Abertura de loop",
            "Slide 3 — Aprofunda o loop / mistério",
            "Slide 4 — Dor do cotidiano",
            "Slide 5 — Bate na ferida",
            "Slide 6 — Virada / insight (opcional)",
            "Slide 7 — Regra prática (opcional)",
            "Slide final — Xeque-mate reflexivo"
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
        Queries em inglês evocando a estética Rockstar: grandeza, shows lotados, luxo moderno, luzes intensas, amanhecer épico.
        PROIBIDO: cenas escuras, depressivas, chuva, isolamento, tristeza.
        (ex: stadium concert crowd lights, modern luxury penthouse sunrise, high energy stage performance, successful leader walking fast, luxury car driving bright city)

        Responda APENAS em formato JSON valido assim:
        {{
          "pexels_queries": [
            "stadium concert crowd lights 35mm",
            "modern luxury penthouse sunrise cinematic",
            "high energy stage performance crowd"
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
        
        # Puxa dados isolados para enriquecer a instrução direta no prompt
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

        # ── Rotação sequencial dos 5 pilares visuais ──────────────────────────
        # Garante que cada Reels Leads use um universo visual diferente,
        # evitando repetição e mantendo a estética cinematográfica do canal.
        PILARES_VISUAIS_LEADS = [
            {
                "nome": "Show e Multidão em Êxtase",
                "exemplo_query": "stadium concert crowd cheering stage lights high energy cinematic",
                "descricao": "shows lotados, multidões em êxtase, luzes de palco vibrantes, atmosfera de rockstar e grandeza",
            },
            {
                "nome": "Luxo e Poder",
                "exemplo_query": "luxury sports car driving bright modern city successful lifestyle 4k",
                "descricao": "carros de luxo, penthouses, ambientes premium, estilo de vida de altíssimo padrão, sol brilhando",
            },
            {
                "nome": "Amanhecer Épico e Visão",
                "exemplo_query": "successful person standing mountain top or modern building looking at epic sunrise",
                "descricao": "amanhecer glorioso, luz dourada da manhã, líderes olhando para o horizonte com visão de futuro",
            },
            {
                "nome": "Palco e Liderança",
                "exemplo_query": "charismatic leader speaking on stage spotlights audience applause",
                "descricao": "líderes palestrando, palcos iluminados, aplausos, carisma e magnetismo",
            },
            {
                "nome": "Celebração e Pertencimento",
                "exemplo_query": "exclusive party people celebrating cheering champagne luxury event",
                "descricao": "pessoas celebrando o topo, festas exclusivas, alegria, alta energia, ambiente festivo premium",
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

        prompt = f"""
        Você é um estrategista de conteúdo especialista em captação de leads no Instagram para o perfil "@codigo.da.sabedoria_".
        Sua missão é criar um VÍDEO DE ALTA CONVERSÃO (Reels Leads) de 4 A 6 SLIDES com um fluxo narrativo que vai da IDENTIFICAÇÃO EMPÁTICA à CLAREZA e culmina em uma ENTREGA TANGÍVEL.
        O perfil vende CLAREZA e DIREÇÃO — não acumula culpa ou depressão. O leitor deve sair sentindo que existe um caminho.

        REGRAS DE COPY E TOM DE VOZ (RIGOROSO):
        - TOM DE IDENTIFICAÇÃO, NÃO ACUSAÇÃO: Prefira perguntas de espelho ("Já aconteceu de você...", "Às vezes, sem perceber...") a frases que atacam ("Você falha porque...", "Você vive preso...").
        - EQUILÍBRIO: Para cada situação de dor identificada, o fluxo narrativo deve abrir um horizonte de esperança, clareza ou ação. Proibido empilhar dor atrás de dor sem saída.
        - PROIBIDO jargões abstratos de coach/guru (ex: "bússola interna", "negociação da sua verdade", "plenitude").
        - Substitua metáforas por SITUAÇÕES CONCRETAS DO DIA A DIA (ex: dizer 'sim' quando quer dizer 'não', guardar projetos na gaveta por receio, trabalhar o dia todo e sentir que correu em círculos).
        - Trate a Edição Semanal como um material prático, tangível e de valor imediato (checklist, guia em PDF, framework de passos).
        - SLIDES ENCADEADOS: Cada slide deve responder à pergunta ou tensão aberta pelo slide anterior. Proibido frases soltas e desconectadas.

        {evitar_repeticao_leads}

        ==== REFERÊNCIA DO TEMA DA SEMANA (EXTRAÍDO DO PDF) ====
        Título da Edição: "{titulo_pdf_limpo}"
        Solução Prática: "{solucao_pdf_limpo}"
        Contexto do Material: {resumo_pdf[:300]}
        =======================================================

        ANTES DE ESCREVER QUALQUER SLIDE, siga obrigatoriamente estas 3 etapas de raciocínio:

        ► ETAPA 1 — IDEIA CENTRAL (uma, nunca duas):
        Defina em UMA frase qual é a única ideia que este Reels vai comunicar.
        Exemplo: "A maioria das pessoas gasta energia no lugar errado e chama isso de produtividade."
        Tudo que não serve a essa ideia central deve ser descartado.

        ► ETAPA 2 — FLUXO LÓGICO ENCADEADO:
        Monte o argumento completo antes de escrever qualquer slide:
        A → B → C → D → E (CTA)
        Onde A leva naturalmente a B, B leva a C, etc.
        Regra absoluta: se um slide puder ser removido sem prejudicar o entendimento, reescreva a sequência.
        Siga este fluxo: (1) identificação empática → (2) por que isso acontece → (3) o que muda quando resolvido → (4) o material como solução → (5) CTA.

        ► ETAPA 3 — ESCOLHA A INTENÇÃO NARRATIVA:
        Escolha UMA das intenções abaixo para guiar o tom:
        - REFLEXÃO: "Existe uma diferença entre estar ocupado e construir algo."
        - INSPIRAÇÃO: "Ainda dá tempo de mudar de direção."
        - MUDANÇA DE PERSPECTIVA: "O problema talvez não seja falta de tempo."
        - ENSINO PRÁTICO: Um processo claro e aplicável imediatamente.
        - EXERCÍCIO: "Hoje faça apenas uma pergunta antes de aceitar qualquer compromisso."

        ESTRUTURA DOS SLIDES (ESCREVA SOMENTE APÓS COMPLETAR AS 3 ETAPAS ACIMA):

        SLIDE 1 — GANCHO (4 a 8 palavras):
        - Para o scroll com uma afirmação ousada, pergunta de identificação ou virada de perspectiva.
        - Exemplos: "Corra pelos seus sonhos. Não pelos alheios." / "Já aconteceu de você se sentir ocupado e vazio ao mesmo tempo?"

        SLIDES INTERMEDIÁRIOS — DESENVOLVIMENTO ENCADEADO (1 ideia por slide):
        - Tom empático, não acusatório: "Às vezes a gente corre muito, mas sem saber para onde." / "Quando você sabe o que priorizar, tudo fica mais leve."
        - PROIBIDO: empilhar 2 ou mais slides negativos consecutivos sem abrir horizonte de clareza.

        PENÚLTIMO SLIDE — SOLUÇÃO TANGÍVEL:
        - Apresente o material ("{titulo_pdf_limpo}") como a resposta natural ao que foi identificado nos slides anteriores.
        - Exemplo: "Este guia é um passo a passo para você saber exatamente o que priorizar."

        SLIDE FINAL — CTA COM ENTREGA TANGÍVEL (use \n para separar):
        - Parte Superior: promessa positiva e concreta.
        - Parte Inferior: instrução com 'SABEDORIA' em caixa alta e entre aspas simples.
        - Exemplo: "Receba o plano de 4 etapas para direcionar seu tempo. \n Aja com clareza: comente 'SABEDORIA' e receba o guia no Direct."

        PEXELS QUERY — PILAR OBRIGATÓRIO DESTA RODADA: "{pilar_nome}"
        A PRIMEIRA query do array pexels_queries DEVE ser: '{pilar_exemplo}'
        As demais queries devem complementar com o mesmo visual: {pilar_descricao}.
        PROIBIDO ESTRITAMENTE: vídeos de dor, chuva, depressão, isolamento, escuridão excessiva. Toda query DEVE evocar poder, luz, luxo, movimento ou multidão vibrando.

        LEGENDA (Máximo 3 a 4 linhas):
        - Focada no benefício direto e concreto, sem jargões.
        - DEVE terminar com a chamada destacando a palavra 'SABEDORIA' entre aspas simples. Exemplo: "Comente 'SABEDORIA' abaixo que eu te envio o guia prático no Direct 👇"
        - NÃO inclua hashtags.

        Responda APENAS em formato JSON válido assim (o array 'slides' DEVE conter de 4 a 6 frases, sendo a última o CTA unificado com \n):
        {{
          "cta_keyword": "SABEDORIA",
          "slides": [
            "Corra pelos seus sonhos. Não pelos alheios.",
            "Às vezes a gente está ocupado com tudo, menos com o que realmente importa.",
            "Energia sem direção é só cansaço disfaçado de produtividade.",
            "Este guia é um passo a passo para você saber exatamente o que priorizar.",
            "Receba o plano de 4 etapas para direcionar seu tempo e energia. \n Aja com clareza: comente 'SABEDORIA' e receba o guia no Direct."
          ],
          "pexels_queries": [
            "{pilar_exemplo}",
            "stadium crowd cheering stage lights high energy",
            "luxury lifestyle modern city sunset cinematic",
            "leader walking fast confident successful"
          ],
          "legenda": "A visão de futuro que você deseja já está escrita por grandes líderes. Se você quer o plano prático, comente 'SABEDORIA' que te envio o guia no Direct 👇"
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
                resposta = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                
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
            if tipo in ["reels", "reels_noite", "reels_conquistador", "pexels_story", "pexels_story_noite", "reels_leads"]:
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

