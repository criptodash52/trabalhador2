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

    "curiosidade": [
        "O medo que te paralisa não é o de perder, mas o de...",
        "Eu descobri algo que mudou tudo. E não foi motivação. Foi...",
        "Quando parei de buscar motivação e comecei a buscar...",
        "A maioria treina habilidades. Os raros treinam...",
        "Existe uma diferença entre quem constrói e quem aparenta. Ela é...",
        "Estudaram décadas o comportamento humano e descobriram que o problema é...",
        "Não é o que você não sabe que te paralisa. É...",
        "E se o que você chama de preguiça for, na verdade,...",
        "Há uma pergunta que você evita fazer a si mesmo. Ela é...",
    ],
    "medo": [
        "Você acha que está buscando sucesso, mas está fugindo do...",
        "O que você mais evita pensar é exatamente o que...",
        "Existe um custo que a maioria não percebe até ser tarde. Ele é...",
        "Você não tem medo de falhar. Você tem medo de...",
        "O silêncio que você foge toda noite está escondendo...",
        "Tem exatamente 3 meses antes que o custo seja...",
        "O que você chama de prudência, seu futuro chama de...",
        "Você repete um erro sem perceber. Esse erro é...",
        "A distancia entre você e seus sonhos tem um nome, e é...",
    ],
    "identidade": [
        "Você julga ter coragem? Então me mostre o que faz no...",
        "Engraçado como a maioria se esforça para polir a vitrine, mas esquece que o...",
        "Há dois tipos de pessoas ao deitar: as que reviram o dia e as que...",
        "A prova real do seu caráter não é o que você faz quando aplaudem, mas...",
        "O que você constrói quando ninguém está olhando define...",
        "A diferença entre quem persiste e quem desiste está em um único hábito, que é...",
        "Você odeia no outro o que mais te incomoda em si, especificamente...",
        "Existe um tipo de pessoa que nunca precisa de motivação. Ela...",
        "Sua família não vai lembrar do seu salário. Vai lembrar do que...",
    ],
    "pertencimento": [
        "Você não está sozinho nisso. A maioria das pessoas que conheço também...",
        "Se você já sentiu que trabalha muito mas avança pouco, então você entende...",
        "Tem uma sensação que ninguém admite em voz alta. Quase todo mundo sente. Ela é...",
        "Às vezes a gente deita e a mente acende. Se você conhece isso, então...",
        "A resposta que você busca mora numa pergunta que você evita. No silêncio, ela...",
        "Se você acordou hoje com mais perguntas do que respostas, isso significa...",
        "Corremos atrás de sombras enquanto a luz essencial...",
        "Existe uma guerra silenciosa que a maioria trava todos os dias. Ela é...",
        "Você busca paz fora e ignora a guerra interna. Um erro que quase todos cometem porque...",
    ],
    "contradicao": [
        "Quanto mais você corre, mais parado se sente. O motivo disso é...",
        "Sua ânsia por controle está te destruindo por dentro porque...",
        "Existe uma mentira neural que te paralisa. Quanto mais você acredita, mais...",
        "A maioria busca motivação. Os raros buscam o que ela esconde, que é...",
        "O que parece força às vezes é apenas o medo de parecer fraco. Isso acontece quando...",
        "Estudaram a vida de milhares por vinte anos e descobriram um abismo chamado...",
        "Ao deitar, o dia se despede. Há dois tipos de pessoas, e a diferença é...",
        "Muitos perdem o fio de si num labirinto de aparências e pressa porque...",
        "A distracão rouba sua própria alma sem você notar, porque age através de...",
    ],
    "autoridade": [
        "Estudaram o comportamento humano por 20 anos. A conclusão foi...",
        "A neurociência já mapeou o que acontece no cérebro de quem desiste. É...",
        "Filósofos estudaram a natureza humana por séculos e chegaram a uma conclusão. Ela é...",
        "Depois de analisar centenas de histórias de reconstrução, um padrão ficou claro. Ele é...",
        "A ciência do comportamento explica por que a maioria sabota os próprios sonhos. A causa é...",
        "Existe uma mentira neural que a neurociência já provou, e ela é...",
        "Há um princípio que os grandes líderes dominam e raramente ensinam. Ele é...",
        "O que separa quem constrói de quem apenas planeja é um único princípio, que é...",
        "Pesquisas sobre hábitos de alta performance revelaram algo incômodo, que é...",
    ],
    "esperanca": [
        "Você é a prova viva de que dá para navegar no caos e ainda manter o...",
        "Não importa quantas vezes você recomeçou. O que importa é que você ainda...",
        "Existe um momento em que tudo muda. Para muitos, ele começa quando...",
        "A mentira que sua mente conta sobre o que te assusta é que não dá. Mas...",
        "O próximo nível não começa com mais esforço. Começa quando você entende que...",
        "Para quem sente que travou: há uma saída. Ela começa por...",
        "A transformação real não começa com motivação. Começa quando você...",
        "Há uma diferença entre quem espera a vida melhorar e quem decide mudar porque...",
        "O que a maioria chama de sorte, os que chegaram lá chamam de...",
    ],
    "escassez": [
        "Tem exatamente 3 meses antes que o custo seja irreversível. Esse custo é...",
        "Cada dia sem essa decisão acumula um preço que poucos percebem. Ele é...",
        "Existe uma janela que fecha devagar. Quando fecha, o que fica é...",
        "O que você não decide hoje, a vida decide por você amanhã. E geralmente é...",
        "Enquanto você espera o momento certo, ele passa. O que sobra depois é...",
        "Em 5 anos, você vai olhar para hoje como o dia que escolheu ou o dia que...",
        "Existe um prazo silencioso que a maioria ignora. Quando vence, o custo é...",
        "O hábito de adiar transforma oportunidade em...",
        "A maioria só descobre que o tempo é o único recurso irrecuperável quando...",
    ],
    "narrativa": [
        "Eu fazia isso assim quando descobri que o problema não era o esforço, mas...",
        "Houve um momento em que percebi que estava correndo na direção errada. Esse momento foi...",
        "Tinha uma crença que eu carregava há anos sem perceber. Quando a vi, entendi que...",
        "Às 23h, ele olhou para as telas. Não era trabalho. Era fuga. O motivo era...",
        "A primeira vez que decidi parar de me justificar, algo mudou. Esse algo foi...",
        "Tinha uma conversa que eu evitava comigo mesmo. Quando finalmente a tive, descobri...",
        "Ele trabalhou 12 horas por dia por 5 anos. No final, o que ele tinha era...",
        "Por anos construí do jeito errado. Quando olhei para o que havia construído, vi...",
        "Quando parei de buscar a resposta certa e comecei a fazer a pergunta certa, tudo mudou porque...",
    ],
    "culpa": [
        "Você sabe o que deveria estar fazendo agora. E não está. Isso se chama...",
        "A versão de você que prometeu mudar ainda está esperando porque...",
        "Existe uma voz dentro de você que você cala toda vez. Essa voz diz...",
        "O que você justifica hoje vai custar algo amanhã. Esse algo é...",
        "Cada dia sem mudança, você vai aceitando uma versão menor de si mesmo porque...",
        "Tem uma promessa que você fez a si mesmo e quebrou. Ela foi...",
        "O que você evita fazer hoje é exatamente o que te mantém preso porque...",
        "Você conhece a resposta. A questão não é o que fazer, mas por que você ainda não...",
        "Ninguém vai te cobrar. Só você sabe o que está deixando para depois, e isso é...",
    ],
}

# ─────────────────────────────────────────────────────────────────────
# LISTA SEQUENCIAL MESTRA — todos os 90 ganchos na ordem de cadastro.
# O bot cicla por esta lista: post 1 usa índice 0, post 2 usa índice 1,
# e quando chega ao último (90), reinicia do zero.
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


