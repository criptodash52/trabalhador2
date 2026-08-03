import random
from core.ai.styles import REGRAS_COPY_BASE, proximo_gancho, proximo_gancho_conquistador, GANCHOS_POR_CATEGORIA, proximo_cta, proxima_arquitetura

# ==========================================
# TEMAS E SUB-ÂNGULOS APROFUNDADOS
# ==========================================
FONTES_SABEDORIA = [
    {
        "nome": "O Poder do Hábito (Charles Duhigg)",
        "essencia": "A quebra de padrões automáticos. Como criar rotinas de campeões e dominar a execução impecável no dia a dia."
    },
    {
        "nome": "Blink (Malcolm Gladwell)",
        "essencia": "O poder do instinto e da decisão rápida. Como pessoas de alto nível tomam decisões precisas em milissegundos confiando na própria mente."
    },
    {
        "nome": "Pai Rico, Pai Pobre (Robert Kiyosaki)",
        "essencia": "A mentalidade de dono e investidor. Como o dinheiro trabalha para quem tem coragem e visão, e como a maioria foge do risco para viver no aperto."
    },
    {
        "nome": "Mais Esperto que o Diabo (Napoleon Hill)",
        "essencia": "A fuga do ritmo hipnótico e da alienação. Como assumir o controle absoluto do próprio destino e rejeitar a mediocridade das massas."
    },
    {
        "nome": "O Poder da Ação (Paulo Vieira)",
        "essencia": "Acorda para a vida que você merece. A responsabilidade inegociável de sair da passividade e executar com intensidade agora."
    },
    {
        "nome": "Provérbios de Salomão",
        "essencia": "A sabedoria milenar do homem mais rico e sábio. Princípios eternos de riqueza, prudência, domínio próprio e excelência."
    },
    {
        "nome": "Malcolm X / Nelson Mandela",
        "essencia": "O poder da autodeterminação, liderança implacável e a coragem de não aceitar a realidade imposta pelo sistema."
    },
    {
        "nome": "Marianne Williamson",
        "essencia": "Nosso maior medo é a nossa própria luz. O poder brilhante e magnífico que existe dentro de nós. Parar de se encolher para agradar os outros."
    },
    {
        "nome": "A Arte da Guerra (Sun Tzu)",
        "essencia": "O planejamento frio e a execução tática cirúrgica. Vencer antes mesmo de entrar no campo de batalha."
    }
]

PERSONAS_MAPEADAS = {
    "O LÍDER CARISMÁTICO": "Tom de quem puxa a multidão. Fala sobre ambição, aproveitar a vida como se não houvesse amanhã, viver em êxtase e conquistar o topo. Eletrizante, apaixonado, contagiante.",
    "O VISIONÁRIO": "Comunicações que inspiram ação e grandeza. Estilo magnético de quem constrói o futuro, desafia o status quo e recusa o básico.",
    "O SÁBIO REI": "Traz verdades atemporais sobre riqueza, prosperidade e como governar a própria vida com majestade e domínio emocional inabalável.",
    "A ESTRELA (O ÍMÃ)": "Foca em autoconfiança absurda, luz própria brilhante e atração magnética. Tem a certeza absoluta do próprio valor e convida os outros a brilharem também."
}

def montar_instrucoes_copy(contexto_analytics="", historico_fontes=None, indice_gancho=0, indice_cta=0, indice_arquitetura=0, is_conquistador=False, sentimento_escolhido=None):
    """Monta o bloco de instrução de copy injetado em todos os prompts, evitando repetições."""
    if historico_fontes is None: historico_fontes = []

    # Sorteia Fonte de Sabedoria (Roleta anti-repetição)
    opcoes_fontes = [f for f in FONTES_SABEDORIA if f["nome"] not in historico_fontes]
    if not opcoes_fontes: # Reseta se todos já foram usados
        historico_fontes.clear()
        opcoes_fontes = FONTES_SABEDORIA
    fonte_escolhida = random.choice(opcoes_fontes)
    nome_fonte = fonte_escolhida["nome"]
    essencia_fonte = fonte_escolhida["essencia"]
    
    # Sorteia Persona
    nome_persona = random.choice(list(PERSONAS_MAPEADAS.keys()))
    desc_persona = PERSONAS_MAPEADAS[nome_persona]
    
    # O sub_angulo agora é o nome da fonte de sabedoria, para ser salvo no historico de ângulos.
    sub_angulo = nome_fonte
    
    # Avança o gancho na sequência linear
    if is_conquistador:
        gancho, novo_indice = proximo_gancho_conquistador(indice_gancho)
        categoria_gancho = "conflito"
    else:
        gancho, novo_indice, categoria_gancho = proximo_gancho(indice_gancho)

    # Avança o CTA na sequência linear
    categoria_cta, referencia_cta, novo_indice_cta = proximo_cta(indice_cta)

    # Avança a arquitetura narrativa na sequência linear
    arquitetura, novo_indice_arquitetura = proxima_arquitetura(indice_arquitetura)

    # Descrições de cada mecanismo psicológico — orientam a IA sobre o GATILHO do Slide 1
    descricoes_categoria = {
        "curiosidade":    "CURIOSIDADE — Crie uma lacuna irresistível de informação. O leitor deve sentir que está prestes a descobrir algo que a elite sabe.",
        "medo":           "OUSADIA — Provoque a fome de arriscar alto. O leitor precisa sentir a urgência de viver algo épico.",
        "identidade":     "IDENTIDADE — Force o leitor a se perguntar 'Em qual grupo de alta performance estou?'. Provoque ambição.",
        "pertencimento":  "PERTENCIMENTO — Faça o leitor sentir a energia de uma tribo vencedora. A frase soa como um aliado inabalável.",
        "contradicao":    "CONTRADIÇÃO — Apresente uma verdade que contraria o conformismo. O leitor espera o senso comum e recebe pura visão.",
        "autoridade":     "AUTORIDADE — Abra com uma máxima incontestável. Domínio e certeza absolutos.",
        "esperanca":      "GRANDEZA — Fale com quem quer chegar no topo. A frase deve soar como um chamado à glória.",
        "escassez":       "ESCASSEZ — Gere urgência para o sucesso. O leitor deve sentir que a vida é curta demais para não ser incrível.",
        "narrativa":      "NARRATIVA — Abra uma cena magnética. A história começa e instiga curiosidade e poder.",
        "culpa":          "DESAFIO — Espelhe a estagnação do leitor sem ser clínico. Provoque-o a se levantar e agir com força.",
        # Fallbacks
        "conflito":       "CONFLITO — Tome uma posição ousada e polarizadora. Provoque reacão magnética.",
        "afirmacao_que_choca": "AFIRMAÇÃO — Abra com uma visão grandiosa que quebre a crença limitante do leitor.",
    }
    descricao_categoria = descricoes_categoria.get(categoria_gancho, "AFIRMAÇÃO — Abra com uma visão grandiosa e ousada.")

    # Injeta a diretriz de sentimento do dia no copy base
    diretriz_sentimento = ""
    if sentimento_escolhido:
        from core.ai.styles import SENTIMENTOS_CONFIG
        config_emocional = SENTIMENTOS_CONFIG.get(sentimento_escolhido)
        if config_emocional:
            diretriz_sentimento = f"\n    DIRETRIZ DE SENTIMENTO DO DIA (Ativar Emoção: {sentimento_escolhido.upper()}):\n    - {config_emocional['tom']}\n    - Cada frase e palavra deve ser desenhada para evocar este exato sentimento no leitor.\n"

    # ================================================================
    # NOVAS INTENÇÕES E FLUXOS NARRATIVOS (Efeito Rockstar / Sabedoria Viva)
    # ================================================================
    INTENCOES_NARRATIVAS = [
        "REFLEXÃO — Focar na diferença entre viver de forma reativa e construir algo duradouro.",
        "INSPIRAÇÃO — Comunicar que a mudança de rumo é possível a qualquer momento.",
        "MUDANÇA DE PERSPECTIVA — Fazer o leitor questionar as velhas convicções (ex: o problema não é falta de tempo, é de foco).",
        "FILOSOFIA DA FELICIDADE — Uma máxima sobre como governar as próprias escolhas e buscar plenitude.",
        "ENSINO PRÁTICO — Uma regra de ouro ou princípio da genialidade para aplicar hoje.",
        "HISTÓRIA/RELATO — Narrar uma mudança interna, um bastidor de vitória ou um preço pago pelo sucesso.",
        "EXERCÍCIO DE PODER — Propor uma única ação simples que altera o estado do leitor imediatamente."
    ]
    
    FLUXOS_NARRATIVOS = [
        "CURIOSIDADE → CONTEXTO → EXEMPLO PRÁTICO → QUEBRA DE EXPECTATIVA → SOLUÇÃO → CTA",
        "REFLEXÃO → IDENTIFICAÇÃO (SITUAÇÃO CONCRETA) → EXPLICAÇÃO DO MECANISMO → INSIGHT CHOCANTE → AÇÃO → CTA",
        "CONCEITO FORTE → BASTIDORES / VERDADE OCULTA → CONFLITO INTERNO → A VIRADA → DIRETRIZ DE PODER → CTA",
        "MITO COMUM → A REALIDADE NUA E CRUA → O PREÇO DE MANTER O MITO → A NOVA PERSPECTIVA → COMO EXECUTAR → CTA"
    ]

    MECANICAS_RETENCAO = [
        "Loop Aberto: Apresente uma informação incompleta que só será concluída no final.",
        "Escalada: Cada frase aumenta a importância da anterior.",
        "Micro Recompensas: Entregue pequenos insights durante todo o texto para impedir abandono.",
        "Pergunta Interna: Faça o leitor responder mentalmente enquanto lê.",
        "Quebra de Expectativa: Leve o leitor para uma conclusão e entregue outra.",
        "Promessa Progressiva: Mostre que existe algo ainda maior chegando."
    ]

    PADROES_RACIOCINIO = [
        "causa -> efeito", "efeito -> causa", "comparação", "contraste", "paradoxo",
        "dedução", "indução", "história -> princípio", "pergunta -> descoberta",
        "erro -> correção", "mito -> verdade", "falso problema -> verdadeiro problema",
        "analogia", "hipótese", "experimento mental"
    ]

    GATILHOS = [
        "Curiosidade", "Reciprocidade", "Autoridade", "Escassez", "Novidade",
        "Pertencimento", "Validação", "Perda", "Contraste", "Antecipação",
        "Mistério", "Exclusividade", "Progresso", "Identificação", "Surpresa"
    ]

    TIPOS_REVELACAO = [
        "Descoberta", "Confirmação", "Choque", "Alívio", "Mudança de perspectiva",
        "Explicação científica", "Explicação psicológica", "Explicação filosófica",
        "Princípio universal", "Erro invisível"
    ]

    FINAIS = [
        "Plot Twist", "Pergunta aberta", "Desafio", "Reflexão", "Silêncio dramático",
        "Frase memorável", "Contraste", "Resumo poderoso", "Visão futura", "Convite"
    ]

    DNAS_NARRATIVOS = [
        {"nome": "DNA Explosivo", "velocidade": 0.9, "curiosidade": 0.8, "emocao": 0.6, "logica": 0.4, "historia": 0.3, "misterio": 0.7, "autoridade": 0.5, "vulnerabilidade": 0.2, "conflito": 0.8},
        {"nome": "DNA Filosófico", "velocidade": 0.3, "curiosidade": 0.6, "emocao": 0.5, "logica": 0.9, "historia": 0.4, "misterio": 0.4, "autoridade": 0.9, "vulnerabilidade": 0.1, "conflito": 0.3},
        {"nome": "DNA Magnético", "velocidade": 0.6, "curiosidade": 0.9, "emocao": 0.8, "logica": 0.5, "historia": 0.7, "misterio": 0.8, "autoridade": 0.8, "vulnerabilidade": 0.5, "conflito": 0.6},
        {"nome": "DNA Vulnerável", "velocidade": 0.4, "curiosidade": 0.5, "emocao": 0.9, "logica": 0.3, "historia": 0.9, "misterio": 0.2, "autoridade": 0.4, "vulnerabilidade": 0.9, "conflito": 0.7}
    ]
    
    # Sorteios
    intencao_escolhida = random.choice(INTENCOES_NARRATIVAS)
    fluxo_escolhido = random.choice(FLUXOS_NARRATIVOS)
    mecanica_escolhida = random.choice(MECANICAS_RETENCAO)
    padrao_escolhido = random.choice(PADROES_RACIOCINIO)
    gatilhos_escolhidos = random.sample(GATILHOS, 2)
    revelacao_escolhida = random.choice(TIPOS_REVELACAO)
    final_escolhido = random.choice(FINAIS)
    dna_escolhido = random.choice(DNAS_NARRATIVOS)

    INSTRUCAO_BASE_RACIOCINIO = f"""
    ======================================================================
    MÁQUINA DE RACIOCÍNIO (A NOVA ESTRUTURA)
    ======================================================================
    Você não é um gerador de frases soltas ou telegramas ("Você sofre. Você chora."). 
    Você é um escritor magnético. Para isso, ANTES DE ESCREVER OS SLIDES, você DEVE seguir 3 Etapas:

    ► ETAPA 1 — IDEIA CENTRAL (Uma, nunca duas):
    Defina mentalmente qual é a única ideia ou lição que este post quer ensinar. O resto deve ser descartado.

    ► ETAPA 2 — FLUXO LÓGICO ENCADEADO (O Argumento):
    Estruture o raciocínio. A deve levar a B, que leva a C. Como as páginas de um bom livro.
    Você deve seguir este exato Fluxo Narrativo de Emoções:
    [ {fluxo_escolhido} ]

    ► ETAPA 3 — TEXTURA NARRATIVA (OBRIGATÓRIO):
    Ao escrever, você DEVE aplicar as seguintes mecânicas matemáticas sorteadas para esta postagem:
    - Padrão de Raciocínio: {padrao_escolhido.upper()} (A lógica invisível que guia os slides)
    - Mecânica de Retenção: {mecanica_escolhida.upper()} (Use isso para prender a atenção a cada slide)
    - Gatilhos Psicológicos: {gatilhos_escolhidos[0].upper()} e {gatilhos_escolhidos[1].upper()}
    - Tipo de Revelação (Clímax): {revelacao_escolhida.upper()}
    - Estilo de Encerramento: {final_escolhido.upper()} (Não use um CTA padrão, use este estilo de finalização)
    
    ► ETAPA 4 — SÓ DEPOIS DISSO, ESCREVA OS SLIDES:
    Substitua dores genéricas por DESENVOLVIMENTO. Mostre situações concretas.
    Ajuste as suas palavras baseadas neste DNA NARRATIVO ({dna_escolhido['nome']}):
    Velocidade: {dna_escolhido['velocidade']} | Curiosidade: {dna_escolhido['curiosidade']} | Emoção: {dna_escolhido['emocao']} | Lógica: {dna_escolhido['logica']} | História: {dna_escolhido['historia']} | Autoridade: {dna_escolhido['autoridade']} | Conflito: {dna_escolhido['conflito']}
    (Pesos de 0.0 a 1.0. Adapte o seu ritmo e estilo de acordo com esses pesos numéricos).

    REGRA DE OURO (INQUEBRÁVEL):
    "Cada slide deve responder implicitamente à pergunta que o slide anterior deixou em aberto. Nunca escreva um slide que possa ser removido sem prejudicar o entendimento da narrativa. Se um slide puder ser apagado e nada mudar, reescreva a sequência inteira."

    INTENÇÃO NARRATIVA DESTE POST: 
    {intencao_escolhida}
    ======================================================================
    """

    instrucoes = f"""
    {diretriz_sentimento}

    REGRAS GERAIS DE ESCRITA:
    1. APLICAR A ARQUITETURA NARRATIVA DO POST:
    Formato: {arquitetura['nome']}
    Diretriz: {arquitetura['descricao']}

    2. MANTER A PERSONA DE ALTA FREQUÊNCIA:
    NOME DA PERSONA: {nome_persona}
    DIRETRIZ DA PERSONA: {desc_persona}
    Você NÃO é um coach de autoajuda genérico que fala de dor, trauma ou sofrimento. Você é um polo de magnetismo, sabedoria e poder.
    Seu objetivo é incendiar a ambição e elevar a energia do leitor. Fale com a certeza de quem vive no topo.
    EXTENSÃO DOS SLIDES: Use entre 10 e 15 palavras por slide. Esse é o espaço exato para completar uma ideia com sentido narrativo. Evite frases excessivamente curtas.

    3. EXTRAIR A GENIALIDADE DA OBRA E TORNÁ-LA SUA:
    FONTE DE INSPIRAÇÃO DO POST DE HOJE: {nome_fonte}
    ESSÊNCIA DA FONTE: {essencia_fonte}
    PROIBIDO citar o nome do livro, do autor ou dar créditos. Pegue a genialidade da obra e passe como conteúdo original e magnético do nosso perfil.

    {INSTRUCAO_BASE_RACIOCINIO}

    ===== DIRETRIZ OBRIGATÓRIA DE CTA (LEGENDA E FECHAMENTO) =====
    Objetivo do CTA desta postagem: {categoria_cta.upper()}
    Frase de referência de tom (use APENAS como bússola de intenção e sentimento — NÃO copie esta frase no roteiro ou na legenda):
    Referência: "{referencia_cta}"

    REGRAS ABSOLUTAS DO CTA:
    1. PROIBIDO CTA SECO: Nunca coloque um comando solto e abrupto como 'Siga.', 'Comente.', 'Salve.' ou 'Compartilhe.' no final de uma mensagem. Isso quebra o ritmo e soa como publicidade barata.
    2. O CTA deve nascer como extensão natural da última ideia entregue. O leitor não deve sentir que o conteúdo terminou e um aviso começou — deve sentir que a própria mensagem está o convidando para a próxima ação.
    3. Varie a estrutura a cada post: ora use uma pergunta que provoca reflexo, ora uma observação que justifica a ação, ora um desafio, ora um convite. Nunca repita a mesma estrutura de CTA em posts seguidos.
    4. O CTA na legenda deve fluir em continuidade direta com o texto anterior — como se fosse o último parágrafo da mensagem, não um apêndice.
    5. O CTA no slide final do vídeo/carrossel deve ser conciso (1 a 2 frases) e funcionar como uma conclusão provocadora, não como uma chamada para ação clássica de marketing.
    ==============================================================

    ESTRUTURA DE ESCRITA DE SUCESSO (Feedback do Analytics):
    - Estude as métricas de performance recentes no bloco abaixo. Identifique quais estilos e estruturas de copy (ex: diagnóstico cirúrgico, perguntas perturbadoras, alertas de perigo) estão trazendo os maiores scores de engajamento e salvamentos no perfil. Adapte a sua forma de escrever para focar nessa estrutura de sucesso!

    TENDÊNCIAS EM TEMPO REAL (Olhos da Rede):
    - Leia as notícias da semana, os vídeos mais vistos no YouTube deste tema e as buscas no Google Trends descritas no bloco abaixo.
    - FUSÃO OBRIGATÓRIA: Não use a Fonte de forma literal e acadêmica. Junte a lição da obra com o estilo de vida, luxo, poder ou comportamento atual (trazido pelos Olhos da Rede). Use cenários de vitória, negócios, palcos e lifestyle magnético para ilustrar a lição.

    DADOS DE PERFORMANCE E CONTEXTO ATUAL:
    {contexto_analytics}
    """
    return instrucoes, sub_angulo, gancho, descricao_categoria, categoria_gancho, novo_indice, categoria_cta, referencia_cta, novo_indice_cta, arquitetura, novo_indice_arquitetura
