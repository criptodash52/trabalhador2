import random

# ==========================================
# ESTILOS DE COPY (abordagem narrativa / tons)
# ==========================================
ESTILOS_COPY = [
    "Tom de maturidade serena e autoral: fale com quietude e sabedoria, sem gritos ou palestras (ex: 'O dia que parei de explicar minha vida foi o dia que comecei a vivê-la.')",
    "Tom de observação humana e postura: linguagem direta e elegante sobre impor limites em silêncio (ex: 'A temporada de dar satisfação pra quem não merece já passou.')",
    "Tom de acolhimento e paz mental: reconheça a luta silenciosa do leitor sem vitimismo (ex: 'Teve dias em que sua única opção era aguentar. E você aguentou. Lembre-se disso.')",
    "Tom de ironia leve e verdade cotidiana: exponha contradições humanas com leveza e um toque de humor sutil (ex: 'Fofocam sobre mim, mas continuam assistindo cada passo. Engraçado como a inveja é silenciosa.')",
    "Tom de conselho sereno como ordem: instrução curta e inegociável para a vida (ex: 'Delete os contatos de quem só te procura quando precisa. Pousa esse peso.')",
    "Tom de lealdade e princípios: exaltar a honra, o respeito e o valor de quem permanece de verdade (ex: 'Valiosas são as pessoas que te dão coisas caras: tempo, lealdade e respeito.')",
]

# ==========================================
# GANCHOS ORGANIZADOS POR CATEGORIA
# Frases autorais, autocontidas e de alta compartilhabilidade (estilo "indiretas" e "espelhos de vida").
# ==========================================
GANCHOS_POR_CATEGORIA = {

    "postura_e_limites": [
        "A temporada de 'não merece minha energia' está oficialmente inaugurada.",
        "Não force rivalidade comigo. Eu nem estou pensando em você.",
        "A pessoa que mais sabe do seu passado deveria ser a primeira a ficar longe do seu presente.",
        "Quando você aprende a se retirar em silêncio, não precisa provar mais nada a ninguém.",
        "Não dê a ninguém o poder de adoecer a sua vida. Lembre-se disso.",
        "Sei exatamente quem esteve lá quando o mar estava agitado. Não me venha com abraço agora.",
        "Ficar em silêncio não significa que não vi. Significa que não vale meu tempo.",
        "A maturidade te ensina: você decepciona pessoas quando começa a impor limites.",
    ],
    "reflexao_de_maturidade": [
        "Uma pessoa criada no amor e outra criada na sobrevivência nunca verão o mundo igual.",
        "Saúde mental é escolher conviver com pessoas que não te deixam doente.",
        "Normalizem ficar com uma pessoa só. Isso é higiene emocional e espiritual.",
        "Eu virei um nadador tão bom que ninguém mais percebe quando tô me afogando.",
        "O dia que parei de tentar agradar todo mundo foi o dia que recuperei minha paz.",
        "Imagina quantas vezes eles se perdoaram em silêncio para chegar até aqui?",
        "Valiosas são as pessoas que te dão coisas raras: tempo, lealdade e respeito.",
        "Teve dias em que a sua única opção era ser forte. E você foi. Continue.",
    ],
    "verdades_curtas": [
        "A inveja nem sempre é sobre querer o que você tem; é sobre não aguentar te ver tendo.",
        "Preste muita atenção ao que as pessoas dizem com raiva — elas estavam doidas para dizer isso.",
        "Por falta de postura, até a pessoa mais bonita deixa de ser atraente.",
        "Quem te conhece de verdade sabe a dor que existiu por trás da sua calma de hoje.",
        "Nunca se canse de pedir discernimento a Deus antes de abrir sua casa para qualquer um.",
        "Você é a prova viva de que dá para passar pelo caos e continuar tendo o coração limpo.",
        "Depois que você aprende o valor da sua paz, qualquer barulho desnecessário irrita.",
        "Você não precisa de vingança. O próprio tempo se encarrega de colocar cada um no seu lugar.",
    ],
    "postura_urbana": [
        "Delete da sua vida quem só lembra de você quando a fonte dos outros seca.",
        "Não confunda minha paz com fraqueza. Eu só escolhi não me sujar.",
        "Meu lado ruim é apenas me afastar sem dizer uma palavra após ver o que não me agrada.",
        "Se eu não caí com tudo o que me aconteceu, não é agora que você vai me derrubar.",
        "Estou na fase de sair de casa e nem tirar foto. Minha vida não é espetáculo.",
        "Quer saber quem é de verdade? Repare em como a pessoa te trata quando você não tem nada a oferecer.",
        "Menos desculpas e mais consideração. O resto é conversa fiada.",
        "Tem coisas que a gente não conta nem pra quem mora com a gente. É sobre Deus e você.",
    ],
    "amor_e_relacionamento": [
        "Quando você encontrar a pessoa certa, você vai saber. Não será apenas sobre atração ou química.",
        "Está no jeito como a presença dela parece um lar, trazendo paz ao seu caos e luz aos dias nublados.",
        "O verdadeiro amor não está na busca pela perfeição, mas em abraçar as imperfeições juntos.",
        "Conversas que fluem sem esforço e um silêncio compartilhado onde ninguém precisa fingir nada.",
        "Alguém que te aceite por completo, não alguém que tente te transformar no que convém a ele.",
        "Cuidar de quem cuida de você: a única regra de ouro que nunca falha num relacionamento.",
    ],
}

# ─────────────────────────────────────────────────────────────────────
# LISTA SEQUENCIAL MESTRA — todos os ganchos na ordem de cadastro.
# O bot cicla por esta lista: post 1 usa índice 0, post 2 usa índice 1,
# e quando chega ao último, reinicia do zero.
# ─────────────────────────────────────────────────────────────────────
LISTA_GANCHOS_SEQUENCIAL = [
    gancho for categoria in GANCHOS_POR_CATEGORIA.values() for gancho in categoria
]


# ==========================================
# GANCHOS CONQUISTADOR — ciclo sequencial próprio (50 ganchos de alto impacto)
# ==========================================
LISTA_GANCHOS_CONQUISTADOR = [
    "A sabedoria radiante de quem aprendeu a contemplar o belo em cada detalhe da jornada.",
    "A verdadeira liberdade é o espírito corajoso que explora a vida sem medo de ser autêntico.",
    "A força extraordinária de quem escolhe a paz, a coragem e a alegria de viver com propósito.",
    "O valor inestimável de alianças leais e amizades sinceras que caminham ao nosso lado.",
    "Como cultivar uma mente curiosa e destemida em um mundo cheio de distrações.",
    "A beleza inspiradora das escolhas feitas por amor, integridade e princípios inegociáveis.",
    "O verdadeiro espírito aventureiro se revela na coragem de encarar novos horizontes com entusiasmo.",
    "A estabilidade real não está no que acumulamos, mas na nobreza da nossa postura diante da vida.",
    "Uma mente serena e motivada enxerga a oportunidade de crescer onde outros veem obstáculos.",
    "A sabedoria milenar de semear o bem com alegria e confiar que o tempo trará os melhores frutos.",
    "Quem governa seus pensamentos com sabedoria descobre que a maior aventura começa por dentro.",
    "A verdadeira riqueza é a liberdade de viver com paixão, desapegado do materialismo superficial.",
    "O valor do caráter reside nos valores sagrados da família, da verdade e da lealdade.",
    "A construção de um legado grandioso começa com a coragem das escolhas simples de hoje.",
    "A paz de espírito e a alegria de viver são os maiores escudos contra a arrogância do mundo.",
    "A lealdade e o amor verdadeiro não são moedas de troca: são o reflexo da nossa essência.",
    "Como manter o entusiasmo e o foco afiado, vivendo cada dia como uma nova oportunidade.",
    "A verdadeira força é serena, valente e inspiradora: não precisa fazer barulho para ser notada.",
    "O princípio atemporal que nos ensina a celebrar cada pequena vitória com gratidão profunda.",
    "Cultivar o amor no lar e proteger quem amamos é a maior conquista de um homem de verdade.",
    "O silêncio sábio e o olhar atento observam a beleza do mundo onde a pressa nada enxerga.",
    "A liberdade começa quando deixamos de ser escravos da aprovação alheia e abraçamos nossos ideais.",
    "A importância de proteger nossa energia e nossa paz para viver com vitalidade e entusiasmo.",
    "Como cultivar a consistência corajosa e a alegria de agir nos dias mais desafiadores.",
    "O valor sagrado de honrar a palavra dada com integridade, firmeza e entusiasmo.",
    "A sabedoria de focar naquilo que constrói a nossa caminhada com leveza e propósito.",
    "Uma conversa sincera entre corações leais tem o poder de transformar qualquer desafio em união.",
    "A verdadeira jornada de crescimento é uma caminhada linda, inspiradora e cheia de aprendizados.",
    "Como blindar o nosso foco para contemplar o que é belo, puro e transformador.",
    "O alívio e a alegria genuína de viver uma vida pautada na verdade, na família e na simplicidade.",
    "A sabedoria milenar que nos lembra: a paciência entusiasta constrói destinos inabaláveis.",
    "Caminhar ao lado de quem compartilha dos mesmos ideais transforma a jornada em uma grande celebração.",
    "A diferença entre viver na ansiedade do futuro e viver com a coragem vibrante do presente.",
    "A beleza das alianças verdadeiras que se fortalecem com o tempo e superam qualquer tempestade.",
    "Como a auto-maestria e o autoconhecimento abrem as portas para uma vida livre e plena.",
    "O poder transformador de celebrar a vida com gratidão por tudo que já foi conquistado.",
    "A sabedoria de olhar para a vida com curiosidade e encanto, como um eterno aprendiz.",
    "A verdadeira liberdade é deitar a cabeça no travesseiro com a consciência limpa e o coração leve.",
    "A força silenciosa e valente de proteger e honrar o seu círculo de família e amigos leais.",
    "Como a maturidade nos ensina a valorizar as conexões profundas e viver sem distrações inúteis.",
    "O poder de uma mente serena e alegre que responde ao mundo com sabedoria e amor.",
    "A sabedoria de abraçar as mudanças com espírito de aventura e recomeçar com entusiasmo.",
    "O caráter sólido se reflete no brilho nos olhos de quem vive com propósito e integridade.",
    "A beleza de viver sem comparações, celebrando a própria história com orgulho e humildade.",
    "A importância de honrar nossas raízes, a sabedoria dos nossos antepassados e nossos valores.",
    "Como a paz interna e a clareza de espírito iluminam cada uma das nossas decisões.",
    "O verdadeiro valor de estar de corpo e alma presente para as pessoas que amamos.",
    "A sabedoria de aprender com cada experiência com leveza, sem carregar o peso do passado.",
    "A força de quem se mantém fiel aos princípios do bem, do amor e da verdade em qualquer cenário.",
    "O maior ato de nobreza é viver de forma autêntica, esbanjando alegria e inspirando quem nos cerca."
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
- NUNCA use tom professoral, arrogante ou com palavras difíceis. Fale de igual para igual.
- Você tem total liberdade para citar livros, filósofos, teorias e autores para dar peso de autoridade à mensagem.

✅ OBRIGATÓRIO — o tom agressivo e atraente:
- O primeiro slide deve ser um gancho forte, curto e cortante. Ele DEVE quebrar o padrão e parar o scroll.
- Use linguagem direta, falada e visceral (coloquial do Brasil).
- Crie contradição imediata: o leitor deve querer discordar nos primeiros 3 segundos, mas concordar ao ler a explicação.
- Use sentenças curtas e parágrafos de uma linha. Textos longos matam a retenção.
- Direcionamento prático: no final de posts de valor, mostre um passo prático curto para resolver a dor.
- Tom: direto, instigante, misterioso e pragmático. Como alguém que enxerga o sistema por trás do comportamento.

🧠 PROCESSOS DE PERSUASÃO:
- INTERRUPÇÃO DE ESTADO: Mude o estado mental do usuário com um fato inesperado ou estudo chocante no início.
- EFEITO ZEIGARNIK: Abra um ciclo de curiosidade no slide 1 e só feche no final.
- DOPAMINA: Entregue um 'segredo' ou atalho prático que o leitor sinta que valeria dinheiro.
- IDENTIDADE: Trate quem lê até o fim como alguém acima da média (ex: 'Quem chega até aqui já entendeu o que a massa ignora').
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
# Fornecidos pelo usuário para alternar objetivos estrategicamente
# ==========================================
CTAS_POR_CATEGORIA = {
    "seguir": [
        "Se isso fez sentido para você, talvez este perfil seja para você.",
        "Aqui a gente faz perguntas que quase ninguém faz.",
        "Se você gosta de pensar diferente, acompanhe este perfil.",
        "Se esse assunto te interessa, ainda tem muito conteúdo por aqui.",
        "Se você procura respostas diferentes, fique por aqui.",
        "Se você gosta de entender o comportamento humano, siga.",
        "Se você acredita que sempre existe outra perspectiva, acompanhe.",
        "Talvez essa seja apenas uma das perguntas que você precisava fazer.",
        "Quem entende o valor do silêncio encontra espaço aqui. Siga.",
        "Acompanhe nossa jornada se você busca profundidade diária.",
        "Se você quer blindar sua mente contra o ruído moderno, siga o perfil.",
        "A evolução pessoal exige constância. Una-se à nossa jornada diária.",
        "Siga se você prefere a verdade que incomoda à mentira que conforta."
    ],
    "comentario": [
        "Quero saber sua resposta.",
        "O que você faria?",
        "Concorda ou discorda?",
        "Qual foi sua primeira reação?",
        "Resuma sua opinião em uma palavra.",
        "Você já viveu isso?",
        "O que você pensa sobre isso?",
        "Existe outra forma de enxergar isso?",
        "Qual dessas verdades bateu mais forte em você?",
        "Você já esteve do outro lado dessa situação?",
        "Comente qual o seu maior obstáculo ao aplicar isso hoje.",
        "Deixe sua percepção sincera aqui embaixo.",
        "Se você pudesse mudar apenas uma atitude hoje, qual seria?"
    ],
    "compartilhamento": [
        "Envie para alguém que precisa ouvir isso.",
        "Compartilhe com quem pensa diferente.",
        "Mostre isso para um amigo.",
        "Essa conversa merece continuar.",
        "Quem você conhece que responderia diferente?",
        "Compartilhe e compare as respostas.",
        "Quero saber o que outra pessoa responderia.",
        "Vale a pena ouvir uma segunda opinião.",
        "Envie isso para a pessoa que compartilha dos seus princípios.",
        "Espalhe essa reflexão com quem valoriza a sabedoria prática.",
        "Compartilhe silenciosamente com quem precisa acordar hoje.",
        "Leve essa mensagem para quem faz parte do seu círculo de ferro.",
        "Envie para alguém com quem você quer crescer junto."
    ],
    "salvamento": [
        "Salve para refletir depois.",
        "Guarde isso.",
        "Você pode querer lembrar disso amanhã.",
        "Vale a pena voltar aqui.",
        "Salve antes de esquecer.",
        "Essa reflexão merece ser revisitada.",
        "Nem toda resposta aparece na primeira leitura.",
        "Guarde essa ideia.",
        "Salve este post para ler quando a mente estiver agitada.",
        "Guarde este checklist mental para a sua próxima decisão difícil.",
        "Salve para reler nos dias em que o foco parecer distante.",
        "Guarde essa chave de sabedoria na sua coleção.",
        "Salve para garantir que esse princípio se torne um hábito."
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


