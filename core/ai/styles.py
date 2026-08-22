import random

# ==========================================
# ESTILOS DE COPY (abordagem narrativa / tons)
# ==========================================
ESTILOS_COPY = [
    "Fazer uma pergunta: crie curiosidade abrindo uma lacuna na mente do leitor (ex: 'Você acredita que controla sua própria mente?')",
    "Criar um conflito interno: exponha uma contradição de comportamento cotidiana (ex: 'Você quer mudar de vida, mas repete os mesmos hábitos.')",
    "Quebrar uma crença: vá contra o senso comum imediatamente (ex: 'O maior erro é achar que falta tempo.')",
    "Prometer revelar algo: instigue o leitor com um segredo ou mecânica oculta (ex: 'Existe uma mentira silenciosa que está destruindo sua paz.')",
]

# ==========================================
# GANCHOS ORGANIZADOS POR CATEGORIA
# Frases autorais, autocontidas e de alta compartilhabilidade (estilo "indiretas" e "espelhos de vida").
# ==========================================
GANCHOS_POR_CATEGORIA = {

    "curiosidade": [
        "Nunca se esqueça que...",
        "Eu acho que você está esquecendo de uma coisa,",
        "Existe algo que você esconde até de si mesmo.",
        "O que ninguém te conta sobre ficar em silêncio...",
        "Tem algo na sua rotina destruindo sua paz em segredo.",
        "Se você soubesse o que acontece quando aprende a dizer não...",
        "Poucos percebem, mas esta atitude muda tudo.",
        "Existe uma regra não dita sobre a sua mente.",
        "O segredo para se libertar do que te paralisa...",
        "Quando você entender isso, nada mais te abala.",
    ],
    "ironia": [
        "Você flerta com a mudança, mas beija o passado.",
        "É irônico como a gente se desgasta por quem nem se importa.",
        "Você reclama do esgotamento, mas adia o que te salva.",
        "Curioso como você cobra respeito e aceita migalhas.",
        "Engraçado como o medo do erro te faz estagnar.",
        "Você finge que superou, mas suas reações te entregam.",
        "É fácil falar de maturidade sem olhar as próprias atitudes.",
        "Você busca validação de quem nem se importa com você.",
        "Quer paz, mas mantém por perto quem traz o caos.",
        "Incrível como você defende a desculpa que te consome.",
    ],
    "sabedoria": [
        "Quem cresceu na sobrevivência enxerga o mundo diferente de quem cresceu no amor.",
        "Não importa quanto tempo você perdeu: salve o resto da sua vida.",
        "Aquilo que você não pode controlar não devia atormentar sua mente.",
        "A dor de mudar é temporária; a dor de continuar igual é vitalícia.",
        "Seu tempo não sumiu — o medo apenas o escondeu.",
        "O silêncio diante de uma ofensa é o maior teste de poder.",
        "Ficar em paz custa caro, mas viver na bagunça mental custa sua alma.",
        "Eu nunca tirei ninguém da minha vida. As atitudes se encarregaram.",
        "Um lar em paz vale mais do que qualquer conquista no caos.",
        "A lealdade em silêncio vale mais do que mil promessas em público.",
    ],
    "seducao": [
        "Não ignore este aviso. O que vem depois vai mudar seu dia.",
        "Existe uma verdade desconfortável que você precisa ouvir hoje.",
        "Isso não é pra todo mundo — mas quem entende, muda de vida.",
        "A sensação de paz real só chega quando você aceita isso.",
        "Não é sobre trabalhar mais. É sobre parar de se sabotar.",
        "Quando você perceber este padrão, nunca mais vai aceitar o básico.",
        "Tem verdades que doem no início, mas libertam para sempre.",
        "Isso aqui vai te poupar anos de frustração desnecessária.",
        "Existe um divisor de águas entre quem sonha e quem realiza.",
        "Se você chegou até aqui, esta mensagem era pra você.",
    ],
    "intriga": [
        "O maior erro do homem não é errar, é...",
        "Se você se viu cedendo a esse velho padrão...",
        "Existe um veneno sutil roubando sua calma diária.",
        "Aquilo não te destruiu, mas algo em você mudou...",
        "O 'momento perfeito' é apenas sua fuga mais silenciosa.",
        "Seu 'não consigo' na verdade é um convite para...",
        "Quando você parar de culpar os outros, isso acontece...",
        "Sua mente te engana quando te diz que...",
        "A decisão que você mais adia é a que mais te libertaria.",
        "Existe uma armadilha disfarçada de proteção na sua vida.",
    ],
    "pergunta": [
        "Quer um conselho prático que pouca gente te dá?",
        "Você realmente escolhe as batalhas que decide lutar?",
        "E se seu maior obstáculo for a sua própria apressada?",
        "Até quando você vai adiar a vida que merece construir?",
        "Você já se perguntou por que repete o mesmo erro?",
        "O que você faria hoje se não tivesse medo do julgamento?",
        "Sua paz é verdadeira ou você só se acostumou com o incômodo?",
        "Você está construindo seu sonho ou realizando o de outra pessoa?",
        "Vale a pena perder sua saúde mental para provar algo aos outros?",
        "Por que você exige do parceiro a maturidade que você não pratica?",
    ],
    "dilema": [
        "A escolha que separa quem constrói o futuro de quem só assiste a vida passar...",
        "No momento da crise, você busca um culpado ou assume o comando?",
        "O dilema que todo homem enfrenta antes de mudar de patamar...",
        "Você prefere a dor temporária da disciplina ou a dor vitalícia do arrependimento?",
        "Aceitar o conforto medíocre hoje ou pagar o preço da grandeza amanhã?",
        "O divisor de águas entre quem sonha e quem realmente executa...",
        "Sua postura diante da derrota define o tamanho da sua vitória futura.",
        "Você domina suas emoções ou é refém do seu estado de espírito?",
    ],
}

# ─────────────────────────────────────────────────────────────────────
# LISTA SEQUENCIAL MESTRA — todos os ganchos na ordem de cadastro.
# ─────────────────────────────────────────────────────────────────────
LISTA_GANCHOS_SEQUENCIAL = [
    gancho for categoria in GANCHOS_POR_CATEGORIA.values() for gancho in categoria
]


# ==========================================
# GANCHOS CONQUISTADOR — ganchos de fé, superação e autoridade cristã
# ==========================================
LISTA_GANCHOS_CONQUISTADOR = [
    "Nunca se esqueça de quem orou por você quando ninguém estava vendo.",
    "O deserto não é o seu túmulo; é a escola onde Deus forja o seu caráter.",
    "Não absorva o desespero do mundo. A sua paz vem da soberania de Deus.",
    "A comunhão no secreto é a maior fortaleza que um homem pode construir.",
    "Permanecer fiel no silêncio de Deus te prepara para o cumprimento da promessa.",
    "Sem alarde, sem vaidade: na dependência de Deus, sua vitória é certa.",
    "Não confunda a demora de Deus com ausência. Ele trabalha no invisível.",
    "Sua mansidão não é fraqueza — é o domínio próprio concedido pelo Espírito.",
    "Guarde o seu coração das ofensas e deixe a justiça nas mãos do Senhor.",
    "A resposta mais sábia diante da provocação é a oração e a obediência.",
    "Quando você descobre quem você é em Cristo, o aplauso do mundo perde o valor.",
    "Seja íntegro nos pequenos começos, pois é na fidelidade que Deus te confia muito.",
    "Você transforma o seu lar no dia em que decide ser o sacerdote da sua casa.",
    "Não tome decisões guiado pelo medo; posicione-se alicerçado nas promessas da Palavra.",
    "A disciplina espiritual é a ponte entre a oração e a resposta manifestada.",
    "Quem tem um chamado eterno não perde tempo disputando espaço no palco dos homens.",
    "Honre a sua aliança e proteja sua família como sentinela na brecha.",
    "Você não precisa de validação humana — o seu chamado foi selado na cruz.",
    "Deixe que o fruto do Espírito fale por você. Viva o Evangelho em atitudes.",
    "A autoridade espiritual se constrói com oração no secreto, não com palavras vãs.",
    "Coragem cristã não é ausência de tempestade, é confiar Naquele que acalma o mar.",
    "Proteja o seu lar e seus filhos da mentalidade corrompida deste século.",
    "Quem recebe o perdão de Cristo é livre para recomeçar sem o peso da culpa.",
    "A verdadeira força é ser manso com as pessoas e implacável contra o pecado.",
    "Não negocie os princípios de Deus em troca de aplausos passageiros.",
    "A maturidade espiritual chega quando você para de murmurar e começa a interceder.",
    "Edifique o seu altar diário antes de tentar vencer as batalhas do mundo exterior.",
    "A constância na oração e na Palavra vence todas as ciladas do inimigo.",
    "Construa uma herança eterna que o tempo e a traça jamais possam corroer.",
    "A gratidão em meio à prova é o maior ato de confiança que você pode oferecer.",
    "Seja leal aos mandamentos de Deus, mesmo quando a cultura exigir que você se dobre.",
    "Alimente a sua fé diariamente, ou as dúvidas do mundo consumirão sua coragem.",
    "Não gaste energia discutindo com escarnecedores; ore por eles e permaneça firme.",
    "A verdadeira honra diante de Deus começa com a sinceridade do arrependimento.",
    "Cultive hábitos devocionais que sustentarão sua fé nas tempestades que virão.",
    "O temor dos homens é um laço, mas quem confia no Senhor está protegido e seguro.",
    "Nada se compara à paz de deitar a cabeça no travesseiro sabendo que agradou a Deus.",
    "Olhe para as provações como ferramentas de Deus para refinar sua perseverança.",
    "A fé não torna as batalhas fáceis, torna a vitória garantida em Cristo.",
    "Aprenda a valorizar e interceder por quem caminha contigo nas horas escuras.",
    "Consagre o seu tempo e seus talentos a Deus — Ele multiplicará os seus frutos.",
    "Quem vence a si mesmo em oração não é derrotado por gigante algum.",
    "Não confunda paciência com negligência: cumpra o seu dever com excelência para o Senhor.",
    "Seja o modelo de integridade, oração e amor sacrificial para as pessoas que você ama.",
    "A renovação da mente pela Palavra é a única chave para experimentar a boa vontade de Deus.",
    "A verdadeira liberdade é viver como servo de Cristo, livre das amarras do mundo.",
    "Sua família é o seu primeiro ministério; cuide dela com zelo, amor e proteção espiritual.",
    "Valorize a simplicidade da presença de Deus mais do que qualquer glória terrena.",
    "Mantenha a fé inabalável, a armadura vestida e o coração blindado pela graça.",
    "O tempo de Deus é perfeito. Descanse o coração, permaneça firme e confie."
]


# ==========================================
# ARQUITETURAS NARRATIVAS (6 formatos rotativos)
# Garante que o fluxo de entrega da mensagem mude a cada postagem,
# quebrando a mesmice do clássico "Problema-Solução".
# ==========================================
ARQUITETURAS_NARRATIVAS = [
    {
        "nome": "Visão de Grandeza",
        "descricao": "Identifique uma ambição ardente do leitor logo após o gancho, eleve o estado de espírito (mostre o topo) e então entregue o princípio prático para chegar lá."
    },
    {
        "nome": "O Ponto de Virada",
        "descricao": "Fale como se estivesse compartilhando o momento exato em que a sua vida mudou ('O dia em que a chave virou para mim...'). Use a primeira pessoa do plural ('nós') para criar aliança de poder com o ouvinte."
    },
    {
        "nome": "Pergunta & Investigação Magnética",
        "descricao": "Faça uma série de perguntas e vá guiando o leitor passo a passo para desmascarar as próprias desculpas, revelando que ele já tem o poder que procura."
    },
    {
        "nome": "Metáfora de Alta Frequência",
        "descricao": "Use uma analogia de poder e magnitude (como a aerodinâmica de um jato, a precisão de um atirador, a gravidade de um planeta) para explicar a mentalidade vencedora de forma puramente visual e eletrizante."
    },
    {
        "nome": "Confronto de Autoridade",
        "descricao": "Abordagem crua, direta e magnética. Quebre a ilusão da mediocridade e chame o leitor para assumir o controle absoluto da própria vida agora mesmo, com energia de líder."
    },
    {
        "nome": "A Cena do Triunfo",
        "descricao": "Crie uma cena curta INÉDITA com um personagem sem nome em um cenário de sucesso (NÃO copie o exemplo antigo das 23h). Narre o momento da vitória silenciosa e deixe que a lição prática surja da atitude dele."
    }
]


# ─────────────────────────────────────────────────────────────────────
# FUNÇÕES DE CICLO SEQUENCIAL
# ─────────────────────────────────────────────────────────────────────

def proximo_gancho(indice_atual=0):
    """Retorna o próximo gancho da sequência linear, reiniciando após o último.

    Returns:
        gancho (str): Texto do gancho a ser usado.
        novo_indice (int): Próximo índice a ser salvo no estado.
        categoria_gancho (str): Categoria do gancho (usada para orientar a IA).
    """
    indice_atual = indice_atual % len(LISTA_GANCHOS_SEQUENCIAL)
    gancho = LISTA_GANCHOS_SEQUENCIAL[indice_atual]
    novo_indice = (indice_atual + 1) % len(LISTA_GANCHOS_SEQUENCIAL)

    # Identifica a categoria para orientar a IA sobre o formato correto
    categoria_gancho = "afirmacao_que_choca"  # fallback
    for cat, ganchos in GANCHOS_POR_CATEGORIA.items():
        if gancho in ganchos:
            categoria_gancho = cat
            break

    return gancho, novo_indice, categoria_gancho


def proximo_gancho_conquistador(indice_atual=0):
    """Retorna o próximo gancho conquistador na sequência linear.

    Returns:
        gancho (str): Texto do gancho conquistador.
        novo_indice (int): Próximo índice a ser salvo no estado.
    """
    indice_atual = indice_atual % len(LISTA_GANCHOS_CONQUISTADOR)
    gancho = LISTA_GANCHOS_CONQUISTADOR[indice_atual]
    novo_indice = (indice_atual + 1) % len(LISTA_GANCHOS_CONQUISTADOR)
    return gancho, novo_indice


def proxima_arquitetura(indice_atual=0):
    """Retorna a próxima arquitetura narrativa da sequência linear, reiniciando após a última."""
    indice_atual = indice_atual % len(ARQUITETURAS_NARRATIVAS)
    arquitetura = ARQUITETURAS_NARRATIVAS[indice_atual]
    novo_indice = (indice_atual + 1) % len(ARQUITETURAS_NARRATIVAS)
    return arquitetura, novo_indice


# ==========================================
# REGRAS DE COPY (compartilhadas por todos os prompts)
# ==========================================
REGRAS_COPY_BASE = """
REGRAS ABSOLUTAS DE COPY (Nicho Cristão — @valoresdopai):

🎯 CAPAS E TÍTULOS DE IMPACTO (REGRA DA CAPA LIMPA):
- A frase da capa ou primeiro slide DEVE ter no MÁXIMO 5 PALAVRAS. Proibido colocar parágrafos ou frases longas cobrindo a tela do vídeo. Use um gancho curto, provocador e cortante.

🔥 DORES REAIS E CONCRETAS (FÉ & REALIDADE):
- Proibido usar clichês religiosos rasos ("Deus tem uma bênção pra você", "Receba"). Foque em conflitos e dores reais da vida: ansiedade, cansaço mental, liderança no lar, dilemas no trabalho, tentações, falta de constância na oração, medo do futuro.

💬 PALAVRAS-CHAVE DE ENGAJAMENTO (ORACAO / SABEDORIA):
- Para posts de atração, conversão e entrega de guias devocionais, use sempre as palavras-chave "ORACAO" ou "SABEDORIA". Instrua o leitor a comentar para receber o material devocional direto no Direct.

❌ PROIBIDO — NUNCA use estas frases genéricas e vazias:
- "Acredite em você", "Você é o cara", "Foco, força e fé", "O universo conspira"
- "Seja a sua melhor versão", "Saia da zona de conforto"
- "Faça acontecer pelo seu próprio braço", "O poder está dentro de você" (A nossa força e justiça vêm de Deus)
- NUNCA use tom professoral, arrogante ou legalista. Fale com amor fraternal, humildade e autoridade bíblica.

✅ OBRIGATÓRIO — o tom pastoral, firme e maduro:
- O primeiro slide deve ser um gancho de retenção curto e profundo que faça o leitor parar o feed e refletir.
- Use linguagem direta, respeitosa e edificante (português claro e acessível).
- Apresente princípios das Escrituras com aplicações práticas e diretas para a rotina diária.
- Baseie os ensinamentos em traduções fiéis (NAA, NVI, ARC).

🧠 PERCEPÇÃO DE VALOR E EDIFICAÇÃO ESPIRITUAL:
Todo conteúdo deve fazer o seguidor sentir que recebeu sabedoria bíblica e clareza espiritual:
- Mostre a causa espiritual/emocional antes da solução prática.
- Revele os princípios de Provérbios, Salmos e dos Evangelhos aplicados a decisões reais.
- Conduza o leitor da ansiedade para a oração, da fraqueza para a dependência da graça de Deus.

🛡️ AUTORIDADE MORAL E TESTEMUNHO:
A autoridade do perfil decorre da firmeza nas Escrituras e do testemunho sincero de fidelidade a Deus:
- Explique o princípio bíblico com profundidade.
- Aponte sempre para a soberania e o amor de Deus.
- Desafie o leitor a uma postura de integridade, oração e honra.
"""


def sortear_estilo(historico_estilos=None):
    if historico_estilos is None:
        historico_estilos = []
    opcoes = [e for e in ESTILOS_COPY if e not in historico_estilos]
    if not opcoes:
        opcoes = ESTILOS_COPY
    return random.choice(opcoes)



# ==========================================
# CTAs ORGANIZADOS POR CATEGORIA (52 itens)
# Referências de tom e intenção — a IA adapta ao contexto de cada post.
# Estruturas variadas: pergunta, observação, desafio, convite, consequência.
# O CTA deve nascer como extensão natural do conteúdo — nunca como comando seco.
# ==========================================
CTAS_POR_CATEGORIA = {
    "seguir": [
        "Se você reconheceu esse padrão em você, cada post aqui vai aprofundar o que você acabou de entender.",
        "O raciocínio continua — e o próximo post vai mais fundo. Quem acompanha desde o início vê os padrões se conectando.",
        "Isso não é conteúdo isolado. É uma construção diária. Cada post aprofunda o anterior.",
        "Aqui a gente vai mais fundo do que o óbvio — todos os dias. Fique por aqui se quer continuar nesse nível.",
        "Você reconheceu esse padrão. O próximo vai te surpreender mais.",
        "Poucos lugares na internet falam sobre isso com essa profundidade. Esse é um deles.",
        "Se isso abriu uma pergunta que você não consegue parar de pensar, ela será respondida nos próximos posts.",
        "O que você viu aqui é apenas a entrada. Acompanhe para não perder o que vem depois.",
        "Mente que para de questionar para de crescer. Esse perfil é pra quem não para.",
        "Cada post aqui é um tijolo numa construção maior. Quem acompanha desde o início enxerga a obra completa.",
        "Se você quer entender o comportamento humano no nível que poucos chegam, está no lugar certo.",
        "Esse tipo de conteúdo não aparece no feed de quem não procura. Fique por aqui — vale.",
        "Esses padrões mudam a forma como você lê as situações. E isso não tem volta."
    ],
    "comentario": [
        "Agora a pergunta real: onde você já viveu exatamente isso?",
        "Qual das duas escolhas você tomaria? Não tem resposta certa — mas a sua diz muita coisa.",
        "Isso te gerou uma certeza ou abriu uma dúvida nova? Conta aqui embaixo.",
        "Pensa numa situação concreta da sua vida onde esse padrão apareceu. Escreve ela aqui.",
        "Se você pudesse resumir isso em uma palavra, qual seria?",
        "É fácil reconhecer esse mecanismo nos outros. Difícil é ser honesto sobre quando você mesmo esteve nele.",
        "Qual parte disso bateu mais forte em você — e por quê?",
        "Às vezes um conteúdo resolve uma questão e abre três novas. Se foi assim, escreve aqui.",
        "Você já tomou uma decisão diferente depois de entender um princípio parecido com esse?",
        "O que você diria para alguém que está no início desse ciclo agora?",
        "Se você tivesse entendido isso 5 anos atrás, o que teria mudado?",
        "Qual é o maior obstáculo que te impede de aplicar isso hoje?",
        "Você concorda que a maioria das pessoas nunca chega nesse nível de consciência sobre isso?"
    ],
    "compartilhamento": [
        "Você já pensou numa pessoa específica enquanto lia isso. Manda pra ela.",
        "Tem alguém na sua vida que está no meio desse ciclo agora — e que precisa ver isso.",
        "A mensagem certa no momento certo muda uma decisão. Envia para quem precisa dessa mudança.",
        "Esse tipo de conversa precisa acontecer mais. Compartilha com alguém com quem você quer ter ela.",
        "Conhecimento parado em você não multiplica. Espalha.",
        "Quem você conhece que responderia diferente a essa pergunta? Manda pra ela e descobre.",
        "Às vezes a pessoa que está do seu lado não sabe que está nesse padrão. Compartilha silenciosamente.",
        "Se isso foi útil pra você, provavelmente vai ser útil pra alguém do seu círculo também.",
        "Pensa no seu grupo de pessoas mais próximas — quantas precisavam ouvir exatamente isso hoje?",
        "Tem conteúdo que é bom guardar pra si. Esse não é um deles — é melhor dividir.",
        "A diferença entre quem cresce e quem estagna muitas vezes é o conteúdo que eles consomem. Compartilha.",
        "Se você faz parte de um grupo, leva esse raciocínio pra ele. Vale uma conversa.",
        "Você vai querer que a pessoa certa veja isso. Manda agora enquanto ainda está fresco."
    ],
    "salvamento": [
        "Guarda isso. Você vai lembrar desse post num momento específico da sua vida.",
        "Tem conteúdo que faz sentido na primeira leitura. Esse vai fazer mais sentido na segunda — quando você estiver no meio de uma decisão.",
        "Essa ideia cresce com o tempo. Salva e volta aqui em 30 dias.",
        "Você não vai querer buscar isso de novo quando precisar. Salva agora.",
        "Na primeira vez você entende. Na segunda você aplica. Na terceira, você ensina alguém.",
        "Esse princípio não é pra usar só hoje. Guarda para quando o momento chegar.",
        "Salva antes de esquecer. O feed engole tudo — menos o que você decidiu manter.",
        "Esse checklist mental vai ser útil na próxima vez que você enfrentar essa situação.",
        "Quando a mente estiver agitada, você vai querer ter isso à mão. Salva.",
        "Informação que não é revisitada vira ruído. Salva e revisa quando precisar.",
        "Essa é uma daquelas reflexões que amadurecem. Salva para ler de novo depois.",
        "O que parece óbvio hoje pode ser exatamente o que você precisa ouvir amanhã. Guarda.",
        "Salva e compartilha depois — quando você tiver vivido isso e quiser mostrar que entendeu."
    ]
}

# ─────────────────────────────────────────────────────────────────────
# LISTA INTERCALADA DE CTAs — Garante que o objetivo de engajamento
# (seguir, comentar, compartilhar, salvar) mude a cada postagem de forma
# alternada e balanceada, passando por cada uma das 52 referências.
# ─────────────────────────────────────────────────────────────────────
LISTA_CTAS_SEQUENCIAL = []
for i in range(13):
    LISTA_CTAS_SEQUENCIAL.append(("seguir", CTAS_POR_CATEGORIA["seguir"][i]))
    LISTA_CTAS_SEQUENCIAL.append(("comentario", CTAS_POR_CATEGORIA["comentario"][i]))
    LISTA_CTAS_SEQUENCIAL.append(("compartilhamento", CTAS_POR_CATEGORIA["compartilhamento"][i]))
    LISTA_CTAS_SEQUENCIAL.append(("salvamento", CTAS_POR_CATEGORIA["salvamento"][i]))

def proximo_cta(indice_atual=0):
    """Retorna o próximo CTA da sequência intercalada, reiniciando após o último.

    Returns:
        categoria (str): O objetivo do CTA (seguir, comentario, compartilhamento, salvamento)
        referencia (str): Frase base a ser adaptada pela IA.
        novo_indice (int): Próximo índice para salvar no estado.
    """
    indice_atual = indice_atual % len(LISTA_CTAS_SEQUENCIAL)
    categoria, referencia = LISTA_CTAS_SEQUENCIAL[indice_atual]
    novo_indice = (indice_atual + 1) % len(LISTA_CTAS_SEQUENCIAL)
    return categoria, referencia, novo_indice


# =====================================================================
# CAIXA DE SENTIMENTOS (15 emoções)
# Mapeia cada sentimento para diretrizes de copy, termos de busca de imagem,
# e subpasta de áudio para criar sinestesia pura.
# =====================================================================
SENTIMENTOS_CONFIG = {
    # ── Família 1: Fé, Soberania & Firmeza (Devocional e Guerra Espiritual)
    "poder": {
        "tom": "Transmita a soberania inabalável de Deus, a autoridade espiritual pela oração e a firmeza diante das tempestades.",
        "busca_imagem": ["ancient mountains golden sunrise dramatic sky biblical", "praying hands light shining through clouds cinematic", "resilient man standing in storm dramatic lighting", "powerful sunrise biblical landscape high resolution"],
        "pasta_audio": "desejo_poder"
    },
    "ousadia": {
        "tom": "Desperte a coragem santa de enfrentar gigantes e desertos com a certeza de que Deus é contigo.",
        "busca_imagem": ["person standing on mountain edge looking at dramatic sunrise", "warrior shield and light in darkness biblical cinematic", "stormy sea with beam of light shining from above", "walking through desert with sunrise on horizon"],
        "pasta_audio": "tensao_acao"
    },
    "plenitude": {
        "tom": "Conecte com a paz que excede o entendimento. O alívio de descansar nos braços do Pai.",
        "busca_imagem": ["peaceful sunrise over calm lake mist 35mm", "morning light streaming through ancient forest trees", "quiet library ancient bible glowing light", "serene valley bathed in warm morning sun"],
        "pasta_audio": "conexao_lealdade"
    },
    "escassez": {
        "tom": "Gere senso de vigília e vigilância espiritual. O tempo presente é precioso para edificar sua família e sua fé.",
        "busca_imagem": ["ancient hourglass with golden sand in darkness", "lantern glowing in dark forest path at night", "clock tower historic sunset dramatic sky", "candlelight in darkness soft glow"],
        "pasta_audio": "tensao_acao"
    },
    "desafio": {
        "tom": "Exorte o seguidor à autoavaliação sincera, ao abandono do pecado e à busca pela santidade e retidão.",
        "busca_imagem": ["man deep in prayer contemplative face dramatic shadow", "ancient stones path leading to light fog", "intense thoughtful look reflection mirror chiaroscuro", "solitary cross on mountain hill dramatic sky"],
        "pasta_audio": "tensao_acao"
    },
    "curiosidade": {
        "tom": "Abra reflexões profundas sobre as verdades ocultas e a sabedoria eterna de Provérbios e das Escrituras.",
        "busca_imagem": ["ancient sacred scripture glowing light dust particles", "candle on wooden desk with open vintage bible", "old scrolls library warm atmosphere", "magnificent historic cathedral interior light rays"],
        "pasta_audio": "tensao_acao"
    },
    "amor": {
        "tom": "Manifeste o amor sacrificial de Cristo, a graça que perdoa e a aliança inquebrável no seio da família.",
        "busca_imagem": ["father embracing family warm golden hour field", "hands holding together light from above", "joyful family walking sunrise meadow cinematic", "open arms silhouette sunrise horizon"],
        "pasta_audio": "conexao_lealdade"
    },
    "carinho": {
        "tom": "Fale como um pastor que cuida das ovelhas com zelo, consolo e paciência.",
        "busca_imagem": ["shepherd walking with sheep peaceful green pasture", "warm tea by window morning sun cozy room", "gentle embrace in soft natural light", "hands resting on open book serene morning"],
        "pasta_audio": "conexao_lealdade"
    },
    "esperanca": {
        "tom": "Mostre que o choro pode durar uma noite, mas a alegria vem pela manhã. Uma visão gloriosa do agir de Deus.",
        "busca_imagem": ["spectacular sunrise breaking through storm clouds", "person looking up at starry night sky with hope", "blooming flower in cracked desert earth sunlight", "sunbeams penetrating dark clouds over ocean"],
        "pasta_audio": "conexao_lealdade"
    }
}


