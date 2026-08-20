# Plano de Implementação: Correção do Studio de Criação + Novos Módulos de Analytics + Guardião de Qualidade

Este plano detalha as correções urgentes da fila de postagem do **Studio de Criação** e a adição dos novos módulos de **Analytics (Olhos da Rede e Mapa de Horários)**, juntamente com a inteligência autônoma do robô.

---

## 🎯 1. Correção Urgente: Studio de Criação Não Publicava
### Diagnóstico Encontrado
Ao enviar uma postagem pelo Studio de Criação do Dashboard, o sistema salva o pedido no Firebase e aciona a nuvem (GitHub Actions) enviando o parâmetro `user_requests`. No entanto, o script central `rodar_via_cron.py` **não possuía um gatilho configurado** para o comando `--manual user_requests`. Por isso, o robô iniciava a nuvem mas encerrava sem executar o arquivo `executor_usuario.py`.

### Solução
#### [MODIFY] [rodar_via_cron.py](file:///c:/Users/kali/Desktop/my_ecosystem/trabalhador1-main/rodar_via_cron.py)
* Adicionar a condição `elif tipo == "user_requests":` no bloco `--manual`.
* Acionar diretamente a execução de `core/publisher/executor_usuario.py` quando a requisição vier do Studio de Criação.

#### [MODIFY] [executor_usuario.py](file:///c:/Users/kali/Desktop/my_ecosystem/trabalhador1-main/core/publisher/executor_usuario.py)
* Garantir que as credenciais do Firebase e os comandos repassados para o `main.py` (--custom-tema e --custom-mensagem) sejam processados e que o status do post no Firebase passe de `pendente` para `publicado`.

---

## 📊 2. Adição dos Novos Módulos de Analytics no Dashboard

#### [MODIFY] [index.html](file:///c:/Users/kali/Desktop/my_ecosystem/trabalhador1-main/dashboard/index.html)
* **📰 Radar "Olhos da Rede" (Tendências da Semana):** Adicionar um card visual na aba *Cientista de Dados* exibindo em tempo real as manchetes e buscas do Google Trends que o robô leu e usou de contexto.
* **⏰ Mapa de Melhores Horários e Dias (Heatmap Temporal):** Adicionar um gráfico comparativo indicando quais dias da semana e horários geram maior alcance e salvamentos.

#### [MODIFY] [app.js](file:///c:/Users/kali/Desktop/my_ecosystem/trabalhador1-main/dashboard/app.js)
* Buscar os dados salvos em `analytics/dados/recomendacoes.json` e renderizar as manchetes do *Olhos da Rede* e a matriz de horários no Dashboard.

---

## 🧠 3. Cérebro Autônomo e Guardião de Qualidade

#### [NEW] [guardiao.py](file:///c:/Users/kali/Desktop/my_ecosystem/trabalhador1-main/core/ai/guardiao.py)
* Módulo de auto-crítica que avalia o roteiro gerado (Nota de 0 a 10). Se a nota for < 8.0, o robô descarta e reescreve automaticamente antes de gerar a mídia/postar.

#### [MODIFY] [analisador.py](file:///c:/Users/kali/Desktop/my_ecosystem/trabalhador1-main/core/analytics/analisador.py)
* Cruzamento de mídias/vídeos e músicas de fundo campeãs em retenção.

---

## Verification Plan

### Automated Tests
- Simular uma chamada manual ao `rodar_via_cron.py --manual user_requests` em ambiente de teste para validar a leitura da fila.
- Executar os scripts de analytics para garantir que o *Olhos da Rede* gera os dados estruturados para o Dashboard.

### Manual Verification
- Enviar um post de teste via Studio de Criação no Dashboard e verificar a publicação.
- Conferir a renderização do Radar de Tendências e do Mapa de Horários na interface.
