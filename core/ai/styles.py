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
}

# ─────────────────────────────────────────────────────────────────────
# LISTA SEQUENCIAL MESTRA — todos os ganchos na ordem de cadastro.
# ─────────────────────────────────────────────────────────────────────
LISTA_GANCHOS_SEQUENCIAL = [
    gancho for categoria in GANCHOS_POR_CATEGORIA.values() for gancho in categoria
]


# ==========================================
# GANCHOS CONQUISTADOR — ganchos diretos de altíssimo impacto visual e emocional
# ==========================================
LISTA_GANCHOS_CONQUISTADOR = [
    "Nunca se esqueça de quem esteve lá nos seus piores dias.",
    "O homem que passou pelo inferno não se assusta com fumaça.",
    "Não absorva a pressa do mundo. Viva no seu próprio ritmo.",
    "A paz de espírito é a maior riqueza que você pode construir.",
    "Ficar sozinho quando você precisa de apoio te transforma para sempre.",
    "Sem fazer barulho, sem se gabar: no silêncio, a vida flui melhor.",
    "Não prolongue ciclos falidos por causa de boas memórias passadas.",
    "Sua paciência não é fraqueza — é controle absoluto da sua mente.",
    "Busque sua paz e deixe os outros ficarem com a razão.",
    "A resposta mais elegante para quem te desrespeita é a sua ausência.",
    "Quando você aprende a ficar em paz sozinho, o básico já não te atrai.",
    "Se você não é o 'sim' de alguém, jamais se submeta a ser o 'talvez'.",
    "Você muda o mundo ao seu redor no dia em que muda sua mente.",
    "Não prometa nada na empolgação e não tome decisões na raiva.",
    "A disciplina é a ponte entre quem você é hoje e quem quer se tornar.",
    "Quem tem propósito forte não perde tempo tentando provar nada.",
    "Honre a sua palavra e cuide de quem corre ao seu lado no escuro.",
    "Você não precisa de mais tempo — precisa de mais foco e menos distrações.",
    "Deixe que os resultados falem por você. Trabalhe em silêncio.",
    "O respeito se constrói com atitudes constantes, não com discursos bonitos.",
    "Coragem não é ausência de medo, é agir mesmo com o coração acelerado.",
    "Proteja seu lar, sua família e sua mente de influências tóxicas.",
    "Quem se perdoa pelo passado consegue finalmente construir o futuro.",
    "A verdadeira força é sereno por fora e inabalável por dentro.",
    "Não venda sua liberdade por uma ilusão de conforto temporário.",
    "A maturidade chega quando você para de reagir a tudo que te irrita.",
    "Pare de tentar salvar quem não quer ser salvo. Salve a si mesmo.",
    "A constância diária vence o talento sem disciplina todas as vezes.",
    "Construa uma vida da qual você não precise tirar férias para escapar.",
    "A gratidão em dias difíceis é o maior ato de fé que existe.",
    "Seja leal aos seus princípios, mesmo quando ninguém estiver olhando.",
    "Sua mente é seu maior aliado ou seu pior algoz: você escolhe o que alimenta.",
    "Não perca energia discutindo com quem só quer vencer o argumento.",
    "A verdadeira coragem é ser honesto consigo mesmo sobre suas falhas.",
    "Crie hábitos que sua versão do futuro vai te agradecer por ter mantido.",
    "O medo do julgamento alheio é a gaiola de quem vive para impressionar.",
    "Nada substitui o valor de deitar na cama com a consciência limpa.",
    "Crie o hábito de focar na solução enquanto os fracos reclamam do problema.",
    "A vida não fica mais fácil, é você que se torna mais forte e sábio.",
    "Aprenda a valorizar quem te apoia no anonimato e nos momentos difíceis.",
    "Trate sua atenção como o recurso mais caro da sua vida — porque ele é.",
    "Quem domina a própria raiva domina qualquer situação no caos.",
    "Não confunda paciência com acomodação: saiba a hora exata de agir.",
    "Seja a referência de serenidade e firmeza para as pessoas que você ama.",
    "O segredo da mudança é focar toda a energia na construção do novo.",
    "A verdadeira liberdade é poder dizer 'não' sem sentir culpa.",
    "Sua história só começa a mudar quando você assume 100% da responsabilidade.",
    "Valorize a simplicidade das coisas reais em um mundo cheio de aparências.",
    "Mantenha os pés no chão, a mente afiada e o coração em paz.",
    "O tempo revela quem é de verdade. Confie no processo e siga firme."
]


# ==========================================
# ARQUITETURAS NARRATIVAS (6 formatos rotativos)
# Garante que o fluxo de entrega da mensagem mude a cada postagem,
# quebrando a mesmice do clássico "Problema-Solução".
# ==========================================
ARQUITETURAS_NARRATIVAS = [
    {
        "nome": "Problema-Solução Clássico",
        "descricao": "Identifique a dor cotidiana do leitor logo após o gancho, aprofunde o incômodo (bata na ferida) e então entregue o insight/passo prático como recompensa."
    },
    {
        "nome": "Confissão Pessoal / Storytelling",
        "descricao": "Fale como se estivesse compartilhando um erro ou aprendizado pessoal do próprio palestrante ('Eu já estive exatamente onde você está agora...'). Use a primeira pessoa do plural ('nós') para criar aliança com o ouvinte."
    },
    {
        "nome": "Pergunta & Investigação Cirúrgica",
        "descricao": "Faça uma série de perguntas e vá guiando o leitor passo a passo para desmascarar as próprias desculpas ou mentiras mentais, revelando a raiz real do problema."
    },
    {
        "nome": "Metáfora / Analogia do Cotidiano",
        "descricao": "Use uma analogia física rica (como o funcionamento de uma represa, uma xícara transbordando, uma árvore sem raízes) para explicar um padrão de comportamento de forma extremamente visual."
    },
    {
        "nome": "Confronto e Alerta de Tempo",
        "descricao": "Abordagem crua e direta. Alerte o leitor de que o tempo está passando, destrua a falsa ilusão de conforto e chame-o para agir imediatamente com firmeza e autoridade."
    },
    {
        "nome": "Micro-Fábula de Personagem",
        "descricao": "Apresente uma cena curta com um personagem sem nome ('Às 23h, ele olhou para as telas...'). Narre a dor dele e deixe que a lição prática surja do desfecho natural da cena."
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
REGRAS ABSOLUTAS DE COPY (violá-las é inaceitável):

❌ PROIBIDO — NUNCA use estas frases de autoajuda vazia:
- "Acredite em você", "Você é capaz", "Nunca desista", "Foco e determinação"
- "Seja a melhor versão de si mesmo", "Saia da zona de conforto"
- "O sucesso é para quem corre atrás", "A vida é uma jornada"
- "Faça acontecer", "Você tem o poder", "Hoje é o dia"
- NUNCA use tom professoral, arrogante ou palavras artificiais de auto-promoção (ex: "Poucos sabem disso..."). Fale de igual para igual.
- Você tem total liberdade para citar livros, filósofos, teorias e autores para dar peso de autoridade à mensagem.

✅ OBRIGATÓRIO — o tom cirúrgico e atraente:
- O primeiro slide deve ser um gancho cliffhanger curto e cortante. Ele DEVE quebrar o padrão e parar o scroll.
- Use linguagem direta, falada e visceral (coloquial do Brasil).
- Use sentenças curtas e parágrafos de uma linha. Textos longos matam a retenção.

🧠 PERCEPÇÃO DE VALOR (DO INÍCIO AO FIM DA MENSAGEM):
Todo conteúdo deve fazer o leitor sentir que acabou de receber um insight difícil de encontrar.
- Evite frases motivacionais genéricas, conselhos óbvios, listas superficiais e clichês.
- Prefira: revelar o mecanismo psicológico por trás do comportamento, explicar o motivo invisível que gera o problema, apresentar uma mudança de perspectiva que aumente a clareza do leitor, entregar um princípio aplicável imediatamente.

🛡️ AUTORIDADE MORAL:
Nunca tente convencer o leitor de que você tem autoridade. Faça com que ele conclua isso sozinho pela qualidade da explicação:
- Explique causas antes de soluções.
- Revele mecanismos antes de recomendações.
- Mostre princípios antes de técnicas.

🎯 O CONCEITO CENTRAL (Filtro de Qualidade):
Toda postagem gerada deve aumentar ativamente uma destas três percepções no leitor:
1. "Nunca tinha pensado por esse ângulo."
2. "Agora entendi por que isso acontece."
3. "Isso vale muito mais do que o tempo que levei para consumir."
Se nenhuma dessas sensações estiver presente do início ao fim, a postagem está superficial e deve ser reescrita.
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
    # ── Família 1: Desejo & Aspiração (Ideal para inspirar e gerar conexão de alta qualidade)
    "poder": {
        "tom": "Transmita autoridade incansável e domínio das emoções. Use frases firmes e seguras. Fale de auto-maestria.",
        "busca_imagem": ["determined male leader portrait night city golden lights 35mm", "strong artistic portrait person night cityscape deep shadows", "powerful stance person night city golden bokeh cinematic", "intense portrait night city lights Kodak Portra 800"],
        "pasta_audio": "desejo_poder"
    },
    "luxuria": {
        "tom": "Desperte o desejo pelo extraordinário e pelo conhecimento restrito aos 1%. Fale sobre segredos ocultos e exclusividade.",
        "busca_imagem": ["artistic couple night city lights warm amber glow 35mm", "stylish person night city reflections golden neon mood", "glamour artistic portrait night warm shadows cinematic", "intimate couple night city lighting Kodak Portra 800"],
        "pasta_audio": "desejo_poder"
    },
    "sensualidade": {
        "tom": "Trabalhe com o magnetismo do mistério e o poder do silêncio atraente. Fale com classe, sem vulgaridade.",
        "busca_imagem": ["artistic portrait person night warm shadow amber light 35mm", "intimate atmosphere couple night city warm lighting", "moody silhouette portrait night golden glow cinematic", "artistic romance night city street lighting 35mm"],
        "pasta_audio": "desejo_poder"
    },
    "prazer": {
        "tom": "Conecte com a satisfação genuína de colher frutos do esforço e viver sob seus próprios termos. Sensação de conquista.",
        "busca_imagem": ["joyful person night city rooftop celebrating warm golden light 35mm", "artistic portrait person smiling night city lights warm glow", "happy couple laughing night city street bokeh cinematic", "peaceful contentment person night warm lighting 35mm"],
        "pasta_audio": "desejo_poder"
    },
    "plenitude": {
        "tom": "Foque no alívio de se sentir completo e em paz consigo mesmo. Acabe com a sensação de estar correndo em vão.",
        "busca_imagem": ["tranquil person contemplating night city skyline golden glow 35mm", "peaceful artistic portrait person night warm ambient light", "serene person looking at night city lights deep shadows", "calm moment person night cityscape Kodak Portra 800"],
        "pasta_audio": "conexao_lealdade"
    },

    # ── Família 2: Tensão & Ação (Excelente para engajamento frio, ganchos rápidos de 2s e comentários)
    "escassez": {
        "tom": "Gere senso de urgência e perda de tempo. Chame a atenção para a velocidade com que os anos passam enquanto o leitor hesita.",
        "busca_imagem": ["person walking alone night city rain golden neon reflections 35mm", "moody portrait person looking at time night cityscape shadows", "thoughtful person night city street rain reflections cinematic", "dramatic portrait night city lights deep shadows 35mm"],
        "pasta_audio": "tensao_acao"
    },
    "raiva": {
        "tom": "Manifeste indignação fria contra a mediocridade, a distração fácil e a hipocrisia social do mundo atual.",
        "busca_imagem": ["intense determined portrait person night city rain 35mm", "dramatic lighting person night city street deep shadows", "strong emotional portrait person night neon reflections", "intense glare person night cityscape Kodak Portra 800"],
        "pasta_audio": "tensao_acao"
    },
    "medo": {
        "tom": "Toque na dor inconsciente e no perigo de continuar na mesma situação de estagnação por covardia de mudar.",
        "busca_imagem": ["moody portrait person looking back night city street rain 35mm", "vulnerable artistic portrait person night city shadows glow", "person walking alone night city street fog golden light", "dramatic atmosphere person night city bokeh 35mm"],
        "pasta_audio": "tensao_acao"
    },
    "duvida": {
        "tom": "Faça perguntas perturbadoras. Desafie as verdades que o leitor julga inabaláveis. Crie incerteza intelectual.",
        "busca_imagem": ["thoughtful person looking at rainy window night city lights 35mm", "contemplative portrait person night city golden shadows", "puzzled artistic portrait person night ambient lighting", "person questioning thoughts night city reflection Kodak Portra"],
        "pasta_audio": "tensao_acao"
    },
    "curiosidade": {
        "tom": "Abra loops mentais com promessas de revelação sobre o comportamento humano. O leitor precisa virar a tela.",
        "busca_imagem": ["artistic portrait person reading book under warm night lamp 35mm", "curious person looking at night city lights golden glow", "thoughtful person discovering something night warm lighting", "intimate artistic reading moment night cityscape bokeh"],
        "pasta_audio": "tensao_acao"
    },

    # ── Família 3: Conexão & Lealdade (Ideal para Stories e aquecimento de base de seguidores)
    "amor": {
        "tom": "Aborde com altruísmo puro, empatia real e proteção aos valores familiares. O valor do sacrifício por quem se ama.",
        "busca_imagem": ["warm genuine affectionate hug couple night city lights 35mm", "tender moment couple night golden ambient lighting cinematic", "artistic affection couple night city street Kodak Portra 800", "intimate embrace couple night warm golden bokeh"],
        "pasta_audio": "conexao_lealdade"
    },
    "carinho": {
        "tom": "Fale com tom de proximidade e cuidado de um verdadeiro mentor. Acolha e ofereça suporte prático com calma.",
        "busca_imagem": ["gentle caring moment couple night warm ambient light 35mm", "affectionate portrait person night city warm golden glow", "tender embrace couple night city lights soft bokeh", "caring mentor comforting person night warm lighting"],
        "pasta_audio": "conexao_lealdade"
    },
    "afeto": {
        "tom": "Mostre a importância das alianças verdadeiras e amizades de aço. Construa pontes emocionais seguras.",
        "busca_imagem": ["two genuine friends laughing together night city street 35mm", "warm friendship hug night city lights golden bokeh", "intimate human connection night city warm ambient light", "loyal friends talking night city street Kodak Portra"],
        "pasta_audio": "conexao_lealdade"
    },
    "alegria": {
        "tom": "Celebre vitórias reais, a beleza da natureza e a felicidade sincera de viver com propósito.",
        "busca_imagem": ["joyful person laughing night city street golden lights 35mm", "happy group friends celebrating night city rooftop glow", "radiant smile person night city bokeh cinematic", "cheerful moment person night cityscape warm lighting"],
        "pasta_audio": "conexao_lealdade"
    },
    "esperanca": {
        "tom": "Mostre que mesmo na noite mais escura, a alvorada virá. Dê perspectivas positivas de crescimento real.",
        "busca_imagem": ["hopeful person looking up night city golden lights 35mm", "inspiring portrait young person night city light reflection", "optimistic look person night cityscape warm amber glow", "bright hope person night city street Kodak Portra 800"],
        "pasta_audio": "conexao_lealdade"
    }
}


