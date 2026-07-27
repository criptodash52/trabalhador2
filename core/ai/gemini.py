import json
import random
import time
import os
from google import genai
from datetime import datetime, timezone

from core.config.settings import GEMINI_KEYS, GROQ_KEYS, OPENROUTER_KEY
from core.ai.prompts import TEMAS_MAPEADOS, montar_instrucoes_copy
from core.ai.styles import sortear_estilo
from core.ai.olhos_da_rede import gerar_contexto_mundo_real
from core.config.state import carregar_estado, salvar_estado
from core.analytics.leitor_pdf import ler_resumo_ultimo_pdf
from loguru import logger


def buscar_historico_por_tema(tema, tipo_post=None, limite=8):
    """
    Busca os últimos posts do mesmo TEMA no historico_posts do Firebase.
    Retorna uma string de contexto para ser injetada no prompt da IA,
    instruindo-a a não repetir as frases e ideias já usadas nesse tema.
    """
    try:
        from core.analytics.db import get_db
        db = get_db()
        if not db:
            return ""

        # Consulta: mesmo tema, ordenado do mais recente ao mais antigo
        query = db.collection("historico_posts").where("tema", "==", tema)
        if tipo_post:
            query = query.where("tipo", "==", tipo_post)
        docs = query.order_by("data", direction="DESCENDING").limit(limite).stream()
        posts_anteriores = [doc.to_dict() for doc in docs]

        if not posts_anteriores:
            return ""

        msg = "\n        PROIBIDO REPETIR (HISTÓRICO DO TEMA):\n"
        msg += f"        O tema de hoje é '{tema}'. Veja abaixo o que já foi publicado nesse tema recentemente.\n"
        msg += "        Você DEVE criar algo completamente diferente — novas frases, novas metáforas, novos ângulos:\n"
        for i, p in enumerate(posts_anteriores):
            frase = p.get("frase_visual") or ""
            legenda_trecho = (p.get("legenda") or "")[:120]
            data = p.get("data", "")[:10]
            if frase or legenda_trecho:
                msg += f"        * Post {i+1} ({data}): Frase='{frase[:150]}' | Legenda='{legenda_trecho}...'\n"
        msg += "        Qualquer semelhança com os textos acima é inaceitável. Seja 100% original.\n"
        return msg

    except Exception as e:
        logger.warning(f"Erro ao buscar histórico por tema '{tema}': {e}")
        return ""

def buscar_historico_reels_leads(limite=6):
    """
    Busca os últimos reels_leads gerados em 'historico_reels_leads' no Firebase.
    Retorna string de contexto para a IA não repetir os mesmos ganchos e frases.
    """
    try:
        from core.analytics.db import get_db
        db = get_db()
        if not db:
            return ""
        docs = db.collection("historico_reels_leads") \
                 .order_by("data", direction="DESCENDING") \
                 .limit(limite).stream()
        posts = [doc.to_dict() for doc in docs]
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
    if "legenda" in dados and detalhes_tema and "hashtags" in detalhes_tema:
        tags = " ".join(detalhes_tema["hashtags"])
        if not any(tag in dados["legenda"] for tag in detalhes_tema["hashtags"]):
            dados["legenda"] = f"{dados['legenda'].strip()}\n\n{tags}"
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

def gerar_conteudo_gemini(tipo):
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
    tema_escolhido = None
    contexto_analytics = ""
    evitar_repeticao_msg = ""
    
    agora = datetime.now(timezone.utc)
    dia_hoje_str = agora.strftime("%Y-%m-%d")

    is_conquistador = (tipo == "reels_conquistador")
    
    if is_conquistador:
        # Loop Cego: Ignora o Analytics e roda pelos 8 temas em sequência
        temas_lista = list(TEMAS_MAPEADOS.keys())
        idx = estado.get("index_conquistador", 0)
        if idx >= len(temas_lista): idx = 0
            
        tema_escolhido = temas_lista[idx]
        
        # Avança pro próximo dia
        estado["index_conquistador"] = (idx + 1) % len(temas_lista)
        salvar_estado(estado)
        logger.info(f"🎯 [CONQUISTADOR] Tema forçado pelo ciclo: {tema_escolhido}")

        # Busca histórico DESTE TEMA para evitar repetição de mensagens no Conquistador
        evitar_repeticao_msg = buscar_historico_por_tema(tema_escolhido, tipo_post="reels_conquistador", limite=6)
    else:
        # Se for o primeiro post do dia, rotaciona o tema sequencialmente
        if estado.get("data_tema_do_dia") == dia_hoje_str and estado.get("tema_do_dia"):
            tema_escolhido = estado["tema_do_dia"]
            logger.info(f"🎲 Tema do dia continuado: {tema_escolhido}")
        else:
            temas_lista = list(TEMAS_MAPEADOS.keys())
            idx = estado.get("index_tema_diario", 0)
            if idx >= len(temas_lista): idx = 0
            
            tema_escolhido = temas_lista[idx]
            
            estado["tema_do_dia"] = tema_escolhido
            estado["data_tema_do_dia"] = dia_hoje_str
            estado["index_tema_diario"] = (idx + 1) % len(temas_lista)
            salvar_estado(estado)
            logger.info(f"🎲 Novo tema sequencial diário ativado: {tema_escolhido}")

        # Busca histórico DESTE TEMA no historico_posts para não repetir a mensagem
        evitar_repeticao_msg = buscar_historico_por_tema(tema_escolhido, tipo_post=tipo, limite=8)
        if evitar_repeticao_msg:
            logger.info(f"📚 Histórico do tema '{tema_escolhido}' carregado para anti-repetição.")

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
            nome_do_tema_atual = TEMAS_MAPEADOS[tema_escolhido]['nome'] if tema_escolhido in TEMAS_MAPEADOS else None
            mundo_real = gerar_contexto_mundo_real(dias=7, tema_especifico=nome_do_tema_atual)
            if mundo_real:
                contexto_analytics += "\n====================\n" + mundo_real + "\n====================\n\n"
        except Exception as e:
            logger.warning(f"Erro ao coletar Olhos da Rede: {e}")

    # Sorteia sentimento do dia de forma persistente ou diária (apenas para posts comuns - não conquistador)
    sentimento_escolhido = None
    if not is_conquistador:
        from core.ai.styles import SENTIMENTOS_CONFIG
        if estado.get("data_sentimento_do_dia") == dia_hoje_str and estado.get("sentimento_do_dia"):
            sentimento_escolhido = estado["sentimento_do_dia"]
            logger.info(f"🧠 Sentimento do dia continuado: {sentimento_escolhido.upper()}")
        else:
            # Sorteia sentimento diário
            sentimento_escolhido = random.choice(list(SENTIMENTOS_CONFIG.keys()))
            estado["sentimento_do_dia"] = sentimento_escolhido
            estado["data_sentimento_do_dia"] = dia_hoje_str
            salvar_estado(estado)
            logger.info(f"🧠 Novo sentimento diário sorteado: {sentimento_escolhido.upper()}")
        
    detalhes_tema = TEMAS_MAPEADOS[tema_escolhido]
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
    instrucoes_copy, sub_angulo, gancho, descricao_categoria, novo_indice, categoria_cta, referencia_cta, novo_indice_cta, arquitetura, novo_indice_arquitetura = montar_instrucoes_copy(
        detalhes_tema, contexto_analytics, hist_angulos, idx_atual, indice_cta, indice_arquitetura=indice_arquitetura, is_conquistador=is_conquistador, sentimento_escolhido=sentimento_escolhido
    )

    # Injeta o histórico do tema no instrucoes_copy → propagado automaticamente para TODOS os tipos de post
    if evitar_repeticao_msg:
        instrucoes_copy += evitar_repeticao_msg

    # Estilo de abordagem sorteado (com anti-repetição)
    estilo_escolhido = sortear_estilo(hist_estilos)
    logger.info(f"🎭 Estilo de abordagem sorteado: {estilo_escolhido.split(':')[0].upper()}")
    logger.info(f"🎣 Gancho sequencial #{idx_atual}: [{gancho[:50]}...]")
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

    # Injeção da Base Bibliográfica (Livros) para posts que suportam profundidade
    livros_base = detalhes_tema.get("inspira", "")
    if livros_base and tipo != "reels_leads":
        instrucoes_livros = f"\n        BASE BIBLIOGRÁFICA (PROFUNDIDADE OBRIGATÓRIA):\n        - Inspire-se fortemente nos conceitos, filosofias e maturidade das seguintes obras: {livros_base}\n        - Traga o peso dessas referências para o conteúdo, sem perder a linguagem direta e moderna."
    else:
        instrucoes_livros = ""


    if tipo == "story":
        prompt = f"""
        Você cria Stories de Instagram direcionados estritamente para pessoas que JÁ TE SEGUEM (audiência quente).
        Sua comunicação deve ser uma CONVERSA ÍNTIMA, EXCLUSIVA, PROPOSITAL E DIRECIONAL.
        Estilo obrigatório para este story: {estilo_escolhido}

        {instrucoes_copy}{instrucoes_livros}

        DIRETRIZ DE ESCRITA:
        - Fale de igual para igual, como um mentor compartilhando uma percepção pessoal profunda do seu dia a dia.
        - Não use ganchos artificiais ou fórmulas de interrupção de padrão frias. Comece o diálogo diretamente.
        - Escreva uma única frase curta e com altíssimo impacto emocional (máximo de 15 palavras).
        - NÃO use ponto de exclamação. Use ponto final ou interrogação.
        
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

        {instrucoes_copy}{instrucoes_livros}

        CRIE UMA SEQUÊNCIA DE EXATAMENTE {num_slides_story} FRASES CURTAS CONECTADAS (MÁXIMO DE 12 PALAVRAS POR FRASE):
        - SLIDE 1 (GANCHO CURTO DE AUTORIDADE): Abra com uma frase curta, elegante e provocativa de liderança (máx 10 palavras). Deve despertar curiosidade e posicionar autoridade imediata.
        - SLIDES INTERMEDIÁRIOS (ENTREGA DE VALOR PRÁTICO): Desenvolva uma pílula diária de sabedoria ou mentalidade baseada no ângulo: "{sub_angulo}". Seja direto, prático e motivador de forma madura.
        - SLIDE FINAL (DIREÇÃO E AUTORIDADE): Feche com uma síntese poderosa que dê direção clara e posicionamento firme para o dia.
        - PROIBIDO usar tom pesado, vitimista, cansado ou carrancudo.
        - Não use ponto de exclamação.
        - Escolha se quer usar música de fundo ou não no story (true ou false) de acordo com o tom da conversa.
        
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

        {instrucoes_copy}{instrucoes_livros}

        CRIE UMA SEQUÊNCIA DE EXATAMENTE {num_slides_story} FRASES CURTAS CONECTADAS (MÁXIMO DE 12 PALAVRAS POR FRASE):
        - SLIDE 1 (GANCHO CURTO DE TRANSIÇÃO): Abra com uma frase instigante sobre foco, discernimento ou maestria diante dos ruídos do dia (máx 10 palavras).
        - SLIDES INTERMEDIÁRIOS (PÍLULA DE CONHECIMENTO): Entregue uma sacada prática de sabedoria derivada do ângulo: "{sub_angulo}". Mostre o caminho com elegância e clareza.
        - SLIDE FINAL (SÍNTESE DE AUTORIDADE): Encerre posicionando autoridade madura e inspirando o leitor a concluir o dia com maestria.
        - PROIBIDO tom de reclamação, cansaço excessivo ou fardo.
        - Não use ponto de exclamação.
        - Escolha se quer usar música de fundo ou não (true ou false).
        
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
        - Cada slide: frase curtíssima e cirúrgica de no MÁXIMO 12 palavras. Sem rodeios.
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
        Você é um especialista em storytelling magnético e neurociência aplicada ao conteúdo digital.
        Seu objetivo é criar um roteiro em slides que faça o usuário PARAR de rolar o feed e assistir até o final.
        Estilo obrigatório para este Reels: {estilo_escolhido}

        {instrucoes_copy}{instrucoes_livros}

        CRIE UMA SEQUÊNCIA NARRATIVA DINÂMICA DE 3 A 5 SLIDES (o número exato deve flutuar livremente entre 3 e 5 a cada execução) seguindo esta estrutura fluida:

        - Slide 1: O Gancho/Quebra de Padrão (Pattern Interrupt) — Frase super provocativa e inesperada para parar o scroll.
        - Slides intermediários (1 a 3 slides): Aprofundamento do tema, mistério ou dor do cotidiano, seguido da entrega de valor ou insight prático.
        - ÚLTIMO SLIDE (obrigatório): CTA — Fusão de impacto com convite sutil e elegante para seguir o perfil (ex: "Se você busca respostas que a maioria ignora, acompanhe o perfil.").

        REGRAS DE ESCUTA E RITMO VISUAL:
        * Misture o comprimento das frases! Curtas e cortantes (4-8 palavras) para dinamismo. Algumas mais longas (até 25 palavras) para profundidade.
        * LIMITE MÁXIMO ESTRITO: Nenhuma frase pode passar de 25 palavras.
        * NÃO use pontos de exclamação.

        LEGENDA:
        - Máximo 3 linhas. Tom de quem viveu aquilo, não de quem está ensinando.
        - CTA OBRIGATÓRIO: A legenda DEVE obrigatoriamente terminar com a chamada para ação (CTA) adaptada conforme a 'DIRETRIZ OBRIGATÓRIA DE CTA' enviada nas instruções.
        - NUNCA termine com uma frase bonita e fechada. Sempre com uma pergunta em aberto.
        - NÃO inclua hashtags.

        Responda APENAS em formato JSON válido assim (DEVE ter de 3 a 5 slides, sendo o último SEMPRE o CTA):
        {{
          "slides": [
            "Slide 1 (Gancho rápido)",
            "Slide 2 (Aprofundamento / Insight)",
            "Slide 3 (CTA — convite sutil para seguir)"
          ],
          "legenda": "Sua legenda aqui sem hashtags"
        }}
        """
    elif tipo == "reels_conquistador":
        prompt = f"""
        Você é a representação viva de uma alma sábia, motivada e aventureira. O seu tom é INSPIRADOR, SÁBIO, ARGUMENTADOR, CURIOSO, VALENTE E CORAJOSO.
        Você ESBANJA ALEGRIA de viver, contempla o belo da criação e busca a liberdade com espírito aventureiro.
        Sua visão é imaterial: seus pilares sagrados são AMOR, FAMÍLIA, AMIZADE VERDADEIRA, IGUALDADE e LIBERDADE.
        Use os recursos oratórios da persona: fale com elegância e proximidade, de igual para igual, inspirando as pessoas a viverem com propósito e coragem.
        {evitar_repeticao_msg}

        INSPIRAÇÕES E PILARES OBRIGATÓRIOS:
        - "Armadilhas da Mente" (Augusto Cury): Domínio sobre os pensamentos e gestão da emoção.
        - Sabedoria Sapiencial: Citações e essência das palavras de Salomão e Jesus.
        - "O Poder da Ação" (Paulo Vieira): Despertar para a coragem, consistência e execução real.
        - Espírito Aventureiro: A alegria de explorar a vida, aprender, amar e proteger quem amamos.

        O QUE VOCÊ REPUDIA (NUNCA VALORIZE):
        - Pessoas arrogantes, soberbas e vaidosas.
        - Filosofia barata de autoajuda vazia.
        - Amor falso, hipocrisia e interesses puramente materialistas.
        - Traição de princípios e deslealdade.

        ESTRUTURA DO VÍDEO MANIFESTO (9 CENAS INSPIRADORAS — MÁXIMO 15 PALAVRAS POR CENA):
        - Cena 1 (Abertura Aventureira/Contemplativa): Um convite inspirador e curioso sobre a beleza da vida, a jornada ou o valor do tempo (SEM soco no estômago ou agressividade).
        - Cena 2: A contemplação do belo da vida e a clareza sobre o que realmente importa.
        - Cena 3: A sabedoria atemporal que liberta a mente das aparências (influência de Salomão/Jesus).
        - Cena 4: O resgate dos valores sagrados (família, igualdade e amigos leais).
        - Cena 5: A coragem e o espírito valente de agir e superar desafios (Poder da Ação).
        - Cena 6: O desapego das ilusões materiais e a rejeição da arrogância/autoajuda vazia.
        - Cena 7: A reconexão com a verdadeira essência, amor e liberdade de viver com propósito.
        - Cena 8: A frase final de impacto: nobre, inspiradora e inesquecível.
        - Cena 9 (Slide Final - CTA Imponente): Um convite sutil, nobre e alinhado para acompanhar a jornada da sabedoria no perfil. NUNCA use jargões de vendas.

        REQUISITO ANTI-REPETIÇÃO: Crie analogias e metáforas 100% inéditas baseadas em elementos reais da vida, da natureza e da jornada humana.

        LEGENDA DO POST:
        - Máximo de 3 linhas de reflexão poética e direta sobre o tema abordado.
        - SEM HASHTAGS.
        - SEM PEDIDO DE COMENTÁRIO OU COMPARTILHAMENTO.

        UNIVERSO VISUAL OBRIGATÓRIO — REELS CONQUISTADOR:
        As queries devem evocar a grandiosidade e sabedoria cibernética em tons de ouro e noite: metrópoles ciberpunk, néon noturno, multidão em movimento nas cidades, arquitetura tecnológica futurista com iluminação dourada nobre, reflexos néon na chuva. NUNCA vídeos genéricos de campo.

        Responda APENAS em formato JSON válido assim:
        {{
          "pexels_queries": [
            "cyberpunk city night neon lights crowd",
            "dark gold futuristic tech architecture",
            "glowing neural network cyber city night"
          ],
          "slides": [
            "Texto da Cena 1",
            "Texto da Cena 2",
            "Texto da Cena 3",
            "Texto da Cena 4",
            "Texto da Cena 5",
            "Texto da Cena 6",
            "Texto da Cena 7",
            "Texto da Cena 8",
            "Texto da Cena 9 (CTA Imponente)"
          ],
          "legenda": "Sua legenda aqui"
        }}
        """

    elif tipo == "pexels_story":
        prompt = f"""
        Você é um roteirista de storytelling de alta conversão para o Instagram.
        Sua missão é criar uma narrativa em slides que PRENDA a atenção desde a primeira frase e conduza o espectador por uma jornada emocional completa.
        Estilo obrigatório: {estilo_escolhido}

        {instrucoes_copy}{instrucoes_livros}

        ===== ESTRUTURA NARRATIVA EM ARCO OBRIGATÓRIA (4 SLIDES) =====

        SLIDE 1 — GANCHO DE IDENTIFICAÇÃO VISCERAL (OBRIGATÓRIO):
        Esta frase PARA o feed imediatamente. Ela precisa fazer o leitor sentir: "É exatamente eu."
        Use UMA destas fórmulas (não copie, crie uma versão inédita conectada ao tema do dia):
        - Confissão de identidade: "Eu era aquela pessoa que..." / "Durante anos eu acreditei que..."
        - Ruptura de crença: "Sempre pensei que trabalhando mais, chegaria lá. Até entender que estava errado."
        - Provocação de reconhecimento: "Você acorda todo dia pra fazer tudo de novo... e onde isso está te levando?"
        - Eco de tentativa: "Eu sei que você já tentou. A questão é: funcionou?"
        REGRA: Máximo 12 palavras. Primeira pessoa ou segunda pessoa direta. Sem jargões de coach.

        SLIDE 2 — EMPATIA COM O PROBLEMA (OBRIGATÓRIO):
        Agora você CONECTA com a dor do dia a dia. Mostre que entende COMO É viver aquela luta.
        - "Eu sei como é acordar cansado de uma rotina que parece não levar a lugar nenhum."
        - "A sensação de estar sempre correndo, mas nunca chegando onde queria estar."
        - Descreva o problema de forma específica, cotidiana e reconhecível. Nada genérico.
        - Finalize com uma virada sutil: "Mas tem uma coisa que mudou tudo pra mim."
        REGRA: 15 a 25 palavras. Tom íntimo, humano e empático.

        SLIDE 3 — A SOLUÇÃO (OBRIGATÓRIO):
        Aqui você entrega a virada de mentalidade, o insight prático ou a lição dos livros.
        - Apresente a solução de forma simples, clara e aplicável.
        - Use a sabedoria do tema para mostrar o caminho concreto.
        - Deve soar como uma descoberta genuína, não como conselho vazio.
        REGRA: 15 a 25 palavras. Tom de revelação e clareza.

        SLIDE 4 — CTA ELEGANTE (OBRIGATÓRIO — SEMPRE O ÚLTIMO):
        Convite natural e fluido para seguir o perfil ou comentar. Conectado ao que foi dito.
        - Não use jargões de vendas ou pressão.
        - Exemplos de tom: "Se isso fez sentido pra você, me segue. Tem muito mais por aqui."
        REGRA: Máximo 15 palavras. Tom pessoal, não comercial.

        PEXELS QUERY:
        - Escolha buscas em inglês para vídeos B-roll evocativos, naturais e cinematográficos (luz matinal, natureza, parques, água, trilhas, luz solar).

        LEGENDA:
        - Máximo 3 linhas. Tom próximo, maduro e reflexivo.
        - CTA OBRIGATÓRIO: A legenda DEVE terminar com a chamada para ação (CTA) adaptada conforme a diretriz recebida.
        - NÃO inclua hashtags.

        Responda APENAS em formato JSON válido assim:
        {{
          "slides": [
            "Slide 1 — Gancho de identificação visceral (máx 12 palavras)",
            "Slide 2 — Empatia com o problema + virada sutil",
            "Slide 3 — A solução / insight prático",
            "Slide 4 — CTA elegante e pessoal"
          ],
          "pexels_queries": [
            "golden sunrise meadow mist peaceful",
            "person walking forest trail morning light",
            "calm river reflection nature tranquil"
          ],
          "legenda": "Sua legenda aqui sem hashtags"
        }}
        """
    elif tipo == "reels_noite":
        prompt = f"""
        Você é um roteirista de storytelling para o Instagram especializado no horário das 18h — quando as pessoas estão saindo do trabalho, exaustas, e ainda sem uma resposta pra o dia.
        Sua missão é criar uma narrativa em slides que PRENDA do primeiro ao último segundo.
        Estilo obrigatório: {estilo_escolhido}

        {instrucoes_copy}{instrucoes_livros}

        ===== ESTRUTURA NARRATIVA EM ARCO OBRIGATÓRIA (4 A 5 SLIDES) =====

        SLIDE 1 — GANCHO DE IDENTIFICAÇÃO NOTURNA (OBRIGATÓRIO):
        Uma frase curta e impactante que o leitor sente como "isso sou eu".
        Use o gancho de referência: '{gancho}' apenas como energia. Crie algo 100% original.
        Fórmulas de impacto (não copie, recrie com o tema):
        - "Você está exausto de novo. E amanhã vai ser igual."
        - "Eu ficava chegando em casa sem saber por que ainda estava lutando."
        - "Mais um dia entregue. O que ficou pra você?"
        REGRA: Máximo 10 palavras. Precisa parar o scroll instantaneamente.

        SLIDE 2 — EMPATIA COM O PROBLEMA DO DIA A DIA (OBRIGATÓRIO):
        Conecte com a luta real: a sensação de trabalhar muito e não ver resultado, de estar presente sem estar, de dar pra todo mundo e não sobrar nada pra si.
        Mostre que ENTENDE como é. Seja específico e humano.
        Finalize com a abertura para a solução: "Mas existe uma saída."
        REGRA: 15 a 25 palavras. Tom de quem já passou por isso.

        SLIDE 3 — A SOLUÇÃO / VIRADA DE MENTALIDADE (OBRIGATÓRIO):
        Entregue o insight real, a lição prática dos livros, o caminho concreto.
        Mostre a solução de forma clara, simples e aplicável à vida real.
        REGRA: 15 a 25 palavras. Tom de revelação genuína.

        SLIDE 4/5 — CTA ELEGANTE (OBRIGATÓRIO — SEMPRE O ÚLTIMO):
        Convite sutil e fluido para seguir o perfil. Conectado com o que foi dito.
        REGRA: Máximo 15 palavras. Tom pessoal e caloroso.

        LEGENDA:
        - Máximo 3 linhas. Tom maduro, sereno e reflexivo.
        - CTA OBRIGATÓRIO: A legenda DEVE terminar com o CTA de engajamento adaptado.
        - NÃO inclua hashtags.

        Responda APENAS em formato JSON válido assim:
        {{
          "slides": [
            "Slide 1 — Gancho de identificação noturna (máx 10 palavras)",
            "Slide 2 — Empatia com o problema + abertura da solução",
            "Slide 3 — A solução / virada de mentalidade",
            "Slide 4 — CTA elegante e pessoal"
          ],
          "legenda": "Sua legenda aqui sem hashtags"
        }}
        """
    elif tipo == "pexels_story_noite":
        prompt = f"""
        Você é um roteirista de storytelling noturno para o Instagram. Horário: 19h-21h.
        Sua missão é criar uma narrativa em slides que conecte emocionalmente com quem está encerrando o dia e buscando sentido no silêncio da noite.
        Estilo obrigatório: {estilo_escolhido}

        {instrucoes_copy}{instrucoes_livros}

        ===== ESTRUTURA NARRATIVA EM ARCO OBRIGATÓRIA (4 A 5 SLIDES) =====

        SLIDE 1 — GANCHO DE IDENTIFICAÇÃO NOTURNA (OBRIGATÓRIO):
        Uma frase curta que toca a ferida do fim do dia — cansaço, rotina, busca por mais.
        Adapte o gancho de referência: '{gancho}' com sensibilidade e autenticidade.
        Fórmulas de impacto (crie uma versão original):
        - "Você deita e ainda não sabe se está indo pro lugar certo."
        - "Eu passei anos achando que o cansaço era o preço normal da vida."
        - "Tem noites em que a cabeça não para. E você sabe bem o motivo."
        REGRA: Máximo 12 palavras. Tom íntimo, de quem entende.

        SLIDE 2 — EMPATIA COM O PROBLEMA (OBRIGATÓRIO):
        Conecte com a luta cotidiana real: a sensação de estar no automático, de sacrificar a vida esperando um futuro que não chega.
        Mostre que ENTENDE e que existe um ponto de mudança.
        REGRA: 15 a 25 palavras. Tom acolhedor e empático.

        SLIDE 3 — A SOLUÇÃO / INSIGHT DE MUDANÇA (OBRIGATÓRIO):
        O insight prático, a sabedoria real, a virada de mentalidade que muda tudo.
        Entregue de forma simples, clara e reconfortante.
        REGRA: 15 a 25 palavras. Tom de revelação e alívio.

        SLIDE 4/5 — CTA ACOLHEDOR (OBRIGATÓRIO — SEMPRE O ÚLTIMO):
        Convite caloroso e natural para seguir o perfil. Deve fluir como continuação da história.
        REGRA: Máximo 15 palavras. Tom íntimo, não comercial.

        PEXELS QUERY:
        - Termos em inglês noturnos e quentes: warm amber room cozy, rain window amber glow, coffee steam night, silent city lights.

        LEGENDA:
        - Máximo 3 linhas. Tom caloroso, sereno e autoral.
        - CTA OBRIGATÓRIO: A legenda DEVE terminar com a chamada para ação (CTA).
        - NÃO inclua hashtags.

        Responda APENAS em formato JSON válido assim:
        {{
          "slides": [
            "Slide 1 — Gancho de identificação noturna (máx 12 palavras)",
            "Slide 2 — Empatia com o problema do dia a dia",
            "Slide 3 — O insight / solução que muda o jogo",
            "Slide 4 — CTA acolhedor de encerramento"
          ],
          "pexels_queries": [
            "warm ambient bedroom cozy night",
            "rain window city lights amber glow",
            "fireplace intimate evening interior warm"
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

        prompt = f"""
        Você é um especialista em captação de leads por vídeo curto no Instagram.
        Sua missão é criar um TRAILER MAGNÉTICO de 3 a 5 slides que funcione como uma isca irresistível para o PDF gratuito.
        O objetivo é simples: fazer quem assiste querer o PDF e clicar no link da bio.
        Estilo obrigatório: {estilo_escolhido}

        {instrucoes_copy}{instrucoes_livros}
        {evitar_repeticao_leads}

        ==== CONTEÚDO BASE (EXTRAÍDO DO ÚLTIMO PDF GERADO) ====
        {resumo_pdf}
        ======================================================

        VOCABULÁRIO DE ALTO VALOR PERCEBIDO (OBRIGATÓRIO USAR EM CADA POST):
        Nunca use termos fracos como "baixar PDF" ou "arquivo". Alterne livremente entre estes termos de alto valor:
        - Nomes do Material: Guia Definitivo, Playbook, Blueprint, Framework, Método, Dossiê, Compêndio, Arsenal de Conhecimento, Kit de Recursos, Leitura Estratégica, Material Exclusivo.
        - Verbos de Ação: Liberar, Acessar, Obter, Explorar, Consultar, Destravar.

        ESTRUTURA OBRIGATÓRIA — TRAILER DE ALTA CONVERSÃO (3 A 5 SLIDES):

        SLIDE 1 — GANCHO VISCERAL (obrigatório):
        - Ataque a dor principal do material de forma direta e cirúrgica.
        - Use a estrutura do gancho de referência de hoje: "{gancho}" (formato: {descricao_categoria}).
        - Máximo 12 palavras. Frase que para o scroll imediatamente.
        - NÃO mencione link, bio ou material aqui.

        SLIDE 2 — APROFUNDAMENTO DA DOR (obrigatório):
        - Aprofunde a dor do Slide 1. Crie o loop de curiosidade.
        - Deixe o espectador pensando: "como eu resolvo isso?" sem dar a resposta inteira ainda.
        - Máximo 15 palavras. Tom íntimo e empático.

        SLIDE 3 — A REVELAÇÃO DA SOLUÇÃO (obrigatório):
        - Revele que a solução prática foi mapeada e está estruturada no material.
        - Conecte com a transformação exata do material: "{solucao_pdf_limpo}".
        - Use um dos termos de alto valor (ex: "Estruturei o Playbook...", "Mapeei no Dossiê...").
        - Máximo 15 palavras. Tom esperançoso e direto.

        SLIDE 4 — QUEBRA DE OBJEÇÃO (opcional, use se quiser 4 ou 5 slides):
        - Destrua a principal desculpa ou dúvida de quem ainda hesita.
        - Exemplo de tom: "Não precisa de horas. São passos práticos aplicáveis hoje."
        - Máximo 12 palavras.

        ÚLTIMO SLIDE — CTA DE ALTA CONVERSÃO CONECTADO AO MATERIAL (obrigatório, sempre o slide final):
        - Deve citar a promessa da obra da semana: "{titulo_pdf_limpo}".
        - Alterne a frase do último slide usando uma destas estruturas de alto impacto:
          * "Para acessar o Guia Definitivo '{titulo_pdf_limpo}', toque no link do meu perfil agora."
          * "Libere o Playbook completo '{titulo_pdf_limpo}' no link do meu perfil."
          * "Comente [PALAVRA-CHAVE] ou acesse o link no meu perfil para obter o Dossiê '{titulo_pdf_limpo}'."
          * "O Blueprint '{titulo_pdf_limpo}' está disponível gratuitamente no link do perfil."
        - Máximo 20 palavras.

        REGRAS ABSOLUTAS:
        * Máximo de 20 palavras por slide.
        * PROIBIDO mencionar link ou bio antes do último slide.
        * NÃO use ponto de exclamação.
        * O número de slides deve variar livremente entre 3 e 5 a cada postagem.

        PEXELS QUERY:
        Escolha buscas em inglês altamente visuais e cinematográficas. Alterne obrigatoriamente entre estes 5 pilares de imagem de acordo com o sentimento "{sentimento_escolhido}":
        1. Pessoas correndo à noite pela cidade com iluminação néon/âmbar (ex: 'person running night city street neon lights runner')
        2. Pessoas em disputa e combate físico intenso (boxe, MMA, treino em ringue/saco de pancadas - ex: 'boxing fight training night intense fighter combat', 'MMA fighter training workout night')
        3. Corridas de bike noturnas no néon urbano (ex: 'night cycling bicycle rider city neon lights')
        4. Cidades futurísticas, modernas, arranha-céus noturnos com luzes douradas e néon (ex: 'futuristic city night skyline modern skyscrapers neon')
        5. Pessoas estudando/trabalhando concentradas no silêncio da noite (ex: 'focused person studying late night warm lamp light')

        LEGENDA:
        - Máximo 3 linhas. Focada em empatia e conexão emocional com a dor debatida.
        - PALAVRA-CHAVE E CTA OBRIGATÓRIO: Escolha uma palavra-chave em CAIXA ALTA relacionada ao tema (ex: "FOCO", "DISCIPLINA", "CLAREZA", "MÉTODO").
        - A legenda DEVE terminar conectada ao material da semana: "Para acessar o Material Exclusivo '{titulo_pdf_limpo}', comente [PALAVRA-CHAVE] 👇 ou acesse o link no perfil."
        - NÃO inclua hashtags.

        UNIVERSO VISUAL OBRIGATÓRIO — REELS LEADS:
        As queries devem variadamente evocar:
        - Pessoas correndo à noite em ruas urbanas iluminadas por néon ou luzes quentes;
        - Disputas esportivas intensas, lutas de boxe, treinos de MMA e ringues de combate noturnos;
        - Corridas de bicicleta noturnas na cidade sob luzes néon;
        - Cidades futurísticas e modernas, metrópoles cyberpunk e arranha-céus noturnos;
        - Foco compenetrado e estudo sob luz de luminária noturna.
        NUNCA vídeos alegres de praia, natureza genérica de dia ou café da manhã casual.

        Responda APENAS em formato JSON válido assim (o array 'slides' DEVE ter de 3 a 5 frases curtas, sendo o ÚLTIMO sempre o CTA):
        {{
          "cta_keyword": "FOCO",
          "slides": [
            "Slide 1 (Gancho visceral — a dor em 1 frase)",
            "Slide 2 (Aprofundamento da dor / loop de curiosidade)",
            "Slide 3 (A solução existe — promessa de transformação)",
            "Slide 4 (Quebra de objeção — opcional)",
            "Slide 5 (CTA elegante — link do perfil)"
          ],
          "pexels_queries": [
            "person running night city street neon lights runner",
            "boxing fight training night intense fighter combat",
            "futuristic city night skyline modern skyscrapers neon"
          ],
          "legenda": "Sua legenda aqui com convite para comentar a palavra-chave sem hashtags"
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

