"""
conteudo.py — Gerador de Conteúdo Narrativo via Gemini AI

Recebe o briefing (tema + livro + contexto da semana) e retorna
o conteúdo completo do PDF em formato estruturado.
"""
import os
import json
import sys
import time

BOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BOT_PATH)

from google import genai
from google.genai import types
from google.genai import errors
from dotenv import load_dotenv

# Carrega variáveis de ambiente do bot
load_dotenv(os.path.join(BOT_PATH, ".env"))


PROMPT_TEMPLATE = """
Você é um mentor espiritual e escritor da comunidade "@valoresdopai". Sua especialidade é escrever guias devocionais profundos, manuais de sabedoria bíblica e planos de oração focados em "FÉ, ORAÇÃO E SABEDORIA EM AÇÃO".

Sua missão é entregar um e-book devocional e prático, preparando o leitor para blindar sua fé, sua mente e sua família com base nas Escrituras.

BRIEFING DA SEMANA:
- Tema central: {nome_display}
- Livro / Estudo base: "{livro_base}"
- Dor de ancoragem: "{dor_central}"

DADOS DE INTERAÇÃO DO PERFIL (O que mais tocou a comunidade recentemente):
{dados_performance_perfil}

CONTEXTO DO MUNDO REAL NESTA SEMANA:
{contexto_semana}

SUA MISSÃO:
Escreva um GUIA DEVOCIONAL E PRÁTICO DE TRANSFORMAÇÃO. O PDF deve entregar uma EXPERIÊNCIA guiada com base na Palavra de Deus, estruturada em ensinamentos bíblicos aplicáveis, orações direcionadas e passos de fé para a rotina diária.

ESTRUTURA DA NARRATIVA (Obrigatório seguir em cada capítulo):
- Emoção & Conexão: Acolha o leitor na sua dor ou luta atual ({dor_central}) com empatia pastoral.
- Fundamento Bíblico: Uma passagem, princípio ou história das Escrituras (inspirado em {livro_base}) que traz luz e direção.
- Lição Prática & Oração: A aplicação concreta na vida diária e como se posicionar em oração e atitude.

DIRETRIZES DE VALOR:
- Tom de voz: Pastoral, reverente, firme e acolhedor. Focado em edificar a fé e o sacerdócio no lar.
- Plano Devocional: O e-book deve culminar em um Plano Prático de Oração e Ação de 7 a 21 dias que a pessoa consiga aplicar imediatamente.

REGRAS DE FORMATAÇÃO DE TEXTO E JSON:
- Use apenas texto simples, pontos e vírgulas.
- É PROIBIDO usar emojis, caracteres especiais, aspas redondas ou travessões longos. Use apenas aspas duplas retas (") e hífens simples (-).
- CRÍTICO: NUNCA use quebras de linha literais (Enter) dentro dos textos do JSON. Escreva tudo na mesma linha contínua.
- REGRA DE IMAGENS: Para a capa, cada capítulo e o plano devocional, crie um "prompt_imagem". Deve ser um descritivo em INGLÊS focado em fotografia hiper-realista, iluminação chiaroscuro, paisagens bíblicas sagradas ou cenas de oração.

ESTRUTURA OBRIGATÓRIA EM JSON (TUDO 100% DINÂMICO):

{{
  "titulo_pdf": "Título magnético inédito focando em método e clareza",
  "subtitulo_pdf": "Subtítulo de benefício direto (ex: O método passo a passo para assumir o controle)",
  "prompt_imagem_capa": "Cinematic dark moody photography of a glowing hourglass in the dark, 8k",
  "capa_cards": [
    {{"titulo": "Crie um título curto e inédito para o card de diagnóstico", "texto": "Escreva aqui o diagnóstico da dor {dor_central} em até 30 palavras — direto e incisivo.", "pergunta_destaque": "Crie uma pergunta que cutuca a ferida do leitor em no máximo 10 palavras."}},
    {{"titulo": "Crie um título curto e inédito para o card do método", "texto": "Descreva o método ou benefício central do livro {livro_base} em até 20 palavras."}},
    {{"titulo": "Crie um título curto e inédito para o card do ritmo ou ganho", "texto": "Qual o ganho concreto que o leitor tem ao aplicar isso? Até 15 palavras."}},
    {{"titulo": "Crie um título curto e inédito para o card da identidade ou princípio", "texto": "Escreva um princípio transformador em até 12 palavras.", "citacao_destaque": "Crie uma citação de até 10 palavras da essência do {livro_base}. Sempre termine com: Código da Sabedoria."}}
  ],
  "capitulos": [
    {{
      "numero": 1,
      "titulo": "Título inédito dinâmico para o Diagnóstico",
      "prompt_imagem": "Cinematic moody dark photography of a tired man looking at a mirror, 8k",
      "paragrafos": [
        "Parágrafo 1 — EMOÇÃO: Toque na dor {dor_central}. Mostre o custo invisível da rotina automática e da falta de clareza mental.",
        "Parágrafo 2 — HISTÓRIA: Conte um breve fato, estudo ou metáfora inspirada no livro {livro_base} sobre alguém que rompeu a inércia.",
        "Parágrafo 3 — LIÇÃO: Ensinamento prático — como identificar o que estava te segurando sem perceber e dar o primeiro passo hoje."
      ]
    }},
    {{
      "numero": 2,
      "titulo": "Título inédito dinâmico para o Controle ou Perspectiva",
      "prompt_imagem": "Cinematic dark moody photography of a glowing book and a sharp sword, 8k",
      "paragrafos": [
        "Parágrafo 1 — EMOÇÃO: A dificuldade de manter o foco e o cérebro que prefere o sofrimento conhecido à mudança.",
        "Parágrafo 2 — HISTÓRIA: Metáfora ou exemplo prático do livro {livro_base} sobre o controle dos próprios impulsos.",
        "Parágrafo 3 — LIÇÃO: Ensinamento prático — A técnica exata para dominar a própria atenção e reprogramar a mentalidade."
      ]
    }},
    {{
      "numero": 3,
      "titulo": "Título inédito dinâmico para Ação e Planejamento",
      "prompt_imagem": "Cinematic dark moody photography of a compass guiding the way in a storm, 8k",
      "paragrafos": [
        "Parágrafo 1 — EMOÇÃO: O sentimento de trabalhar exausto sem nunca sentir que está chegando a algum lugar.",
        "Parágrafo 2 — HISTÓRIA: Um insight poderoso do livro {livro_base} sobre planejamento, antecipação e escolha de metas reais.",
        "Parágrafo 3 — LIÇÃO: Ensinamento prático — Como desenhar um plano à prova de desculpas para a sua semana."
      ]
    }}
  ],
  "citacao_destaque": "Citação impactante de sabedoria e fé baseada em {livro_base}.",
  "titulo_citacao": "Princípio Eterno",
  "verso_base": "Um versículo bíblico fundamental (ex: Salmos, Provérbios ou Evangelhos) que ancore a lição prática de fé e sabedoria.",
  "referencia_verso": "Referência Bíblica (ex: Salmos 23:1, Provérbios 3:5-6)",
  "plano_acao": {{
    "titulo_secao": "Crie um título totalmente original para este plano — pode ser um devocional de 7, 14 ou 21 dias de oração, pilares de blindagem espiritual, ou passos de sabedoria prática baseados em {livro_base}.",
    "prompt_imagem": "Crie um prompt cinematográfico em inglês para a imagem do plano devocional, hiper-realista, iluminação sagrada chiaroscuro, 8k.",
    "subtitulo": "Crie um subtítulo que explique de forma inspiradora como executar este devocional na prática.",
    "passos": [
      "ATENÇÃO: Crie entre 3 e 6 passos/dias — cada passo deve ter: numero (inteiro), titulo (inédito e criativo) e descricao (orientação prática de oração, reflexão e atitude, baseada nas Escrituras)."
    ]
  }},
  "fechamento": "A sua vitória não começa no barulho do mundo, mas na fidelidade e na oração no secreto. Permaneça firme na Rocha.",
  "titulo_fechamento": "VALORES DO PAI",
  "rodape": "Valores do Pai — Fé, Honra e Sabedoria em Ação.",
  "landing_page": {{
    "promessa_clara": "Crie uma promessa forte em até 10 palavras (Ex: 21 DIAS PARA BLINDAR SUA FÉ E SUA FAMÍLIA).",
    "beneficios": [
      "Escreva um benefício espiritual prático em até 15 palavras (Ex: Encontre paz real e vença as noites de ansiedade pela oração).",
      "Escreva um benefício espiritual prático em até 15 palavras.",
      "Escreva um benefício espiritual prático em até 15 palavras.",
      "Escreva um benefício espiritual prático em até 15 palavras.",
      "Escreva um benefício espiritual prático em até 15 palavras."
    ]
  }}
}}

Retorne APENAS o JSON, sem texto antes ou depois.
"""


def gerar_conteudo_pdf(briefing: dict) -> dict:
    print("[Conteudo] Chamando Gemini AI para gerar o conteudo do PDF...")

    import random
    nomes_possiveis = ["Lucas", "Mateus", "Gabriel", "Thiago", "Felipe", "Daniel", "Andre", "Rafael", "Samuel", "Davi", "Elias", "Josue", "Calebe", "Pedro", "Joao"]
    nome_sorteado = random.choice(nomes_possiveis)
    print(f"[Conteudo] Nome do personagem sorteado para esta edicao: {nome_sorteado}")

    prompt = PROMPT_TEMPLATE.format(
        nome_display=briefing["nome_display"],
        livro_base=briefing["livro_base"],
        dor_central=briefing["dor_central"],
        dados_performance_perfil=briefing.get("dados_performance_perfil", "Sem dados recentes."),
        contexto_semana=briefing["contexto_semana"],
        nome_personagem=nome_sorteado
    )

    for num_chave in range(1, 11):
        chave_atual = os.getenv(f"GEMINI_API_KEY_{num_chave}")
        if not chave_atual:
            continue
            
        try:
            print(f"[Conteudo] Tentando gerar conteudo com GEMINI_API_KEY_{num_chave}...")
            client_atual = genai.Client(api_key=chave_atual)

            import concurrent.futures
            def _chamar_gemini():
                for modelo in ["gemini-2.5-flash", "gemini-3.6-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
                    try:
                        resp = client_atual.models.generate_content(
                            model=modelo,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                temperature=0.85,
                                max_output_tokens=8192,
                            )
                        )
                        return resp.text
                    except Exception as e_model:
                        if "404" in str(e_model) or "not found" in str(e_model).lower():
                            continue  # Tenta o proximo modelo
                        raise  # Outro erro — propaga
                raise Exception("Nenhum modelo Gemini disponivel para esta chave.")

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_chamar_gemini)
                try:
                    texto_bruto = future.result(timeout=45)  # 45s de timeout por chave
                except concurrent.futures.TimeoutError:
                    print(f"   [Timeout] GEMINI_API_KEY_{num_chave} nao respondeu em 45s. Tentando proxima...")
                    continue

            texto_resposta = texto_bruto.strip()

            if texto_resposta.startswith("```json"):
                texto_resposta = texto_resposta[7:]
            if texto_resposta.startswith("```"):
                texto_resposta = texto_resposta[3:]
            if texto_resposta.endswith("```"):
                texto_resposta = texto_resposta[:-3]

            conteudo = json.loads(texto_resposta.strip())
            print(f"[Conteudo] Conteudo gerado com sucesso! Titulo: '{conteudo.get('titulo_pdf', 'N/A')}'")
            return conteudo

        except Exception as e:
            print(f"Falha com GEMINI_API_KEY_{num_chave} (Erro: {str(e)[:100]}). Tentando proxima chave...")
            time.sleep(2)
            continue

    # ── FALLBACK GROQ: todas as chaves Gemini falharam ou travaram ──
    print("[Conteudo] Gemini indisponivel. Acionando GROQ como fallback de conteudo...")
    try:
        from groq import Groq
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            groq_client = Groq(api_key=groq_key)
            resposta_groq = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.85,
                max_tokens=8192,
                timeout=60
            )
            texto_resposta = resposta_groq.choices[0].message.content.strip()
            if texto_resposta.startswith("```json"):
                texto_resposta = texto_resposta[7:]
            if texto_resposta.startswith("```"):
                texto_resposta = texto_resposta[3:]
            if texto_resposta.endswith("```"):
                texto_resposta = texto_resposta[:-3]
            conteudo = json.loads(texto_resposta.strip())
            print(f"[Conteudo] GROQ gerou o conteudo! Titulo: '{conteudo.get('titulo_pdf', 'N/A')}'")
            return conteudo
        else:
            print("[Conteudo] GROQ_API_KEY nao encontrada no .env")
    except Exception as e_groq:
        print(f"[Conteudo] Falha no Groq tambem: {str(e_groq)[:120]}")
                
    print("🚨 TODAS as chaves da API do Gemini falharam! Acionando SAÍDA DE EMERGÊNCIA (PDF Coringa Cristão)...")
    
    # SAÍDA DE EMERGÊNCIA: Retorna um conteúdo devocional de alto nível
    conteudo_emergencia = {
      "titulo_pdf": "Blindagem Espiritual & Paz na Tempestade",
      "subtitulo_pdf": "O guia devocional para vencer a ansiedade e fortalecer sua fé no secreto.",
      "prompt_imagem_capa": "Cinematic biblical photography of an open vintage bible illuminated by divine golden sunbeams, 8k",
      "capa_cards": [
        {"titulo": "A Batalha", "texto": "A ansiedade e o medo tentam roubar a sua paz antes mesmo do dia começar. A sobrecarga na alma é o sinal de que você está tentando carregar sozinho um peso que pertence a Deus.", "pergunta_destaque": "Você tem entregado suas lutas em oração ou apenas acumulado cansaço?"},
        {"titulo": "O Refúgio", "texto": "A paz verdadeira não nasce da ausência de problemas, mas da presença inegociável de Deus. Quando você dobra os joelhos no secreto, Ele acalma a tempestade ao seu redor."},
        {"titulo": "O Propósito", "texto": "Edificar o seu altar diário e blindar a sua mente e sua casa com as promessas da Palavra."},
        {"titulo": "A Promessa", "texto": "Mil cairão ao teu lado, mas tu permanecerás firme se tua casa estiver sobre a Rocha.", "citacao_destaque": "\"Aquietai-vos e sabei que Eu sou Deus. — Salmos 46:10\""}
      ],
      "capitulos": [
        {
          "numero": 1,
          "titulo": "O Altar no Secreto",
          "prompt_imagem": "Cinematic dark moody chiaroscuro photography of hands folded in prayer by candlelight, 8k",
          "paragrafos": [
            "Existe uma batalha diária que não é travada contra pessoas, mas nas regiões do espírito e nos pensamentos que tentam consumir sua calma. Quando as cobranças do mundo batem à porta, a primeira coisa que o inimigo tenta roubar é a sua constância devocional.",
            "Davi encontrava força para enfrentar gigantes e exércitos inteiros porque antes de entrar em qualquer campo de batalha, ele derramava sua alma perante o Senhor. O seu momento a sós com Deus não é um ritual religioso; é o oxigênio que sustenta sua fé.",
            "Quando você aprende a fechar a porta do seu quarto e orar ao Pai que vê em secreto, você descobre que nenhuma tempestade terrena pode derrubar quem é sustentado pela graça soberana."
          ]
        },
        {
          "numero": 2,
          "titulo": "Vencendo a Ansiedade pela Palavra",
          "prompt_imagem": "Cinematic photography of an ancient parchment scroll with divine sunbeam through stone window, 8k",
          "paragrafos": [
            "A ansiedade sussurra mentiras sobre o seu futuro, tentando fazer você esquecer a fidelidade de Deus no passado. Mas as Escrituras nos ensinam em Filipenses 4 a não andar ansiosos por coisa alguma, antes apresentar tudo a Deus em oração.",
            "A paz que excede todo o entendimento humano não é uma ilusão; é o escudo protetor que guarda o seu coração quando as circunstâncias ao redor parecem incertas.",
            "Substitua o ciclo da preocupação pelo ciclo da gratidão e da intercessão. Cada vez que um pensamento de medo tentar invadir sua mente, responda com uma promessa bíblica declarada em voz alta."
          ]
        },
        {
          "numero": 3,
          "titulo": "O Sacerdócio e a Proteção do Lar",
          "prompt_imagem": "Cinematic photography of a father blessing his family warm golden hour light olive grove, 8k",
          "paragrafos": [
            "Sua casa é o seu primeiro e mais importante ministério. Edificar os muros espirituais da sua família exige vigilância, oração contínua e um testemunho de honra e integridade inegociáveis.",
            "Neemias nos ensina que para reconstruir os muros destruídos, precisamos segurar a ferramenta de trabalho com uma mão e a espada da fé com a outra, lutando pelos nossos lares e filhos.",
            "Assuma o seu posicionamento espiritual. Seja a coluna de fé e serenidade que sua família precisa ver nos dias difíceis."
          ]
        }
      ],
      "citacao_destaque": "Entrega o teu caminho ao Senhor; confia nele, e ele tudo fará. — Salmos 37:5",
      "titulo_citacao": "Princípio Eterno",
      "verso_base": "O Senhor é o meu pastor; de nada terei falta. Em verdes pastagens me faz repousar e me conduz a águas tranquilas.",
      "referencia_verso": "Salmos 23:1-2",
      "plano_acao": {
        "titulo_secao": "Jornada de 7 Dias de Oração & Blindagem",
        "prompt_imagem": "Cinematic photography of an open bible and candle on rustic wooden table, 8k",
        "subtitulo": "Sete dias de consagração e renovação espiritual.",
        "passos": [
          {"numero": 1, "titulo": "Dia 1: Oração de Entrega Total", "descricao": "Dedique 15 minutos ao acordar para listar todas as suas preocupações e entregá-las conscientemente a Deus."},
          {"numero": 2, "titulo": "Dia 2: Blindagem da Mente", "descricao": "Medite no Salmo 91 e declare a proteção do Altíssimo sobre sua mente, trabalho e família."},
          {"numero": 3, "titulo": "Dia 3: Quebra de Rancores e Perdão", "descricao": "Exercite o perdão sincero em oração, liberando qualquer mágoa acumulada para desfrutar da liberdade em Cristo."},
          {"numero": 4, "titulo": "Dia 4: Consagração do Trabalho", "descricao": "Apresente seus projetos e finanças a Deus, pedindo sabedoria prática como a de Salomão para tomar decisões."},
          {"numero": 5, "titulo": "Dia 5: Clamor pela Família", "descricao": "Reúna sua família ou ore individualmente ungindo o seu lar com orações de paz e proteção espiritual."},
          {"numero": 6, "titulo": "Dia 6: Louvor na Tempestade", "descricao": "Agradeça a Deus pelas vitórias invisíveis e louve antes mesmo de ver a resposta manifestada."},
          {"numero": 7, "titulo": "Dia 7: Renovação do Altar", "descricao": "Estabeleça um compromisso inegociável de manter seu devocional diário como prioridade máxima da sua rotina."}
        ]
      },
      "fechamento": "Permaneça firme na Palavra e constante na oração. Deus está cuidando de tudo enquanto você descansa na Sua fidelidade.",
      "titulo_fechamento": "VALORES DO PAI",
      "rodape": "Valores do Pai — Fé, Honra e Sabedoria em Ação."
    }
    
    return conteudo_emergencia
