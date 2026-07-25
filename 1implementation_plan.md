# Plano de Implementação: Máquina de Leads & Modo Lançamento Automático

Transformar o bot em uma **máquina diária de captação de leads** através do encurtamento do `reels_leads`, implementação da chamada de **Palavra-Chave nos Comentários**, entrega de PDF 100% programática pelo Direct (sem dependência do ManyChat) e criação do **Modo Lançamento em 3 Fases (PPL -> PL -> Vendas)**.

## User Review Required

> [!IMPORTANT]
> **Entrega Programática pelo Direct (Sem ManyChat)**
> Em vez de usar o ManyChat (que possui limites de contatos e mensalidade), utilizaremos uma **solução 100% programática em Python**:
> 1. **Webhook Oficial Meta Graph API**: O próprio bot recebe notificações em tempo real quando alguém comenta a palavra-chave no seu post e envia o link do PDF no Direct usando o `IG_ACCESS_TOKEN`.
> 2. **Fallback Autônomo**: Script interno que verifica periodicamente os novos comentários das postagens recentes e envia o Direct para quem comentou a palavra-chave.

> [!TIP]
> **Encurtamento do Reels Leads (Retenção 5x Maior)**
> O `reels_leads` passará de **35 slides (3 minutos)** para **8 a 12 slides (45 a 60 segundos)**. Isso garantirá que mais de 80% do público assista ao vídeo até o final e veja a chamada para comentar a palavra-chave.

---

## Open Questions

> [!NOTE]
> 1. **Qual palavra-chave principal prefere usar nos comentários?** (Exemplos: `SABEDORIA`, `LIVRO`, `PDF`, `QUERO`, `MENTE`).
> 2. **Duração preferida do Ciclo de Lançamento**: Recomendamos o ciclo padrão de 14 dias (5 dias PPL + 5 dias PL + 4 dias Vendas). Deseja ajustar os dias de cada fase?

---

## Proposed Changes

### Core Engine (Funil de Leads & Roteiros)

#### [MODIFY] [gemini.py](file:///c:/Users/kali/Desktop/my-bot-instagram-main/core/ai/gemini.py)
- Reduzir a estrutura do `reels_leads` de 35 slides para **8 a 12 slides dinâmicos** (45 a 60 segundos).
- Reformular a Fase 10 do `reels_leads` para exigir o gatilho da palavra-chave nos comentários (ex: *"Comente 'SABEDORIA' que te envio o PDF no Direct"*).

---

### Automação de Direct & Captação Programática (Sem ManyChat)

#### [NEW] [gerenciador_direct.py](file:///c:/Users/kali/Desktop/my-bot-instagram-main/core/leads/gerenciador_direct.py)
- Criar o sistema programático que monitora comentários de posts de leads.
- Ao detectar a palavra-chave (ex: `SABEDORIA`), envia automaticamente a mensagem no Direct da pessoa com o link do PDF recém-gerado.
- Registra os leads capturados (username, data, post, PDF enviado) no banco de dados Firebase/local.

---

### Módulo do Modo Lançamento (PPL -> PL -> Vendas)

#### [NEW] [modo_lancamento.py](file:///c:/Users/kali/Desktop/my-bot-instagram-main/core/config/modo_lancamento.py)
- Controlar as 3 fases do lançamento:
  - **Fase 1 (PPL - 5 dias)**: Reels Conquistador e Pexels Story despertam a curiosidade e antecipação sem vender nada.
  - **Fase 2 (PL - 5 dias)**: Ativação massiva do `reels_leads` + Gerador de PDF + Chamada da Palavra-Chave.
  - **Fase 3 (Lançamento / Carrinho Aberto - 4 dias)**: Postagens de alta urgência e escassez direcionando para a oferta principal (comunidade/curso).

#### [MODIFY] [main.py](file:///c:/Users/kali/Desktop/my-bot-instagram-main/main.py)
- Adicionar o argumento `--modo-lancamento` para alternar os cronogramas de postagem de acordo com a fase atual do lançamento.

---

## Verification Plan

### Automated Tests
- Executar compilação de sintaxe Python: `python -m py_compile core/ai/gemini.py core/leads/gerenciador_direct.py core/config/modo_lancamento.py main.py`.
- Simular a geração de um `reels_leads` encurtado para verificar a contagem de slides (entre 8 e 12 slides).
- Testar a verificação de comentários programática via Graph API.

### Manual Verification
- Testar o envio de um comentário de teste no Instagram com a palavra-chave escolhida e verificar se o Direct com o PDF é recebido instantaneamente.
