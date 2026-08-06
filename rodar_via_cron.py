import sys
import time
import datetime
import subprocess
import io

# Forçar UTF-8 no Windows para suportar emojis no print
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def rodar_agora():
    # Calcula a hora no Brasil (UTC-3)
    utc_now = datetime.datetime.utcnow()
    brt_now = utc_now - datetime.timedelta(hours=3)
    hora = brt_now.hour
    dia_semana = brt_now.weekday()  # 0 = Segunda-feira

    print(f"🕒 Hora atual no Brasil: {brt_now.strftime('%Y-%m-%d %H:%M:%S')} (Dia da semana: {dia_semana})")

    if hora == 4:
        dia_mes = brt_now.day
        mes = brt_now.month

        # --- INGESTÃO DIÁRIA (todo dia) ---
        # Coleta métricas do Instagram e salva no Firebase. Não altera recomendações.
        print("📥 Executando: Ingestão Diária de Métricas (coleta pura)")
        subprocess.run(["python", "core/analytics/rodar_analytics.py", "--only-collect"])

        # Fechamento semanal (relatório) continua no Domingo
        if dia_semana == 6:  # Domingo
            print("🚀 [DOMINGO] Executando: Fechamento Semanal, Relatório")
            subprocess.run(["python", "-c", "import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); from core.analytics.analisador_semanal import analisar_semana; analisar_semana()"])
            subprocess.run(["python", "core/reports/weekly.py"])
            print("🔬 [DOMINGO] Executando: Cientista de Dados + Formulador de Hipóteses")
            subprocess.run(["python", "core/analytics/rodar_analytics.py", "--ciclo", "semanal"])


    elif hora == 5:
        if dia_semana == 6:  # Domingo
            print("🚀 [DOMINGO] Executando: Geração do PDF da Semana")
            # Roda o gerador de PDF
            subprocess.run(["python", "gerador_pdf/gerador.py"])

    elif hora == 6:
        if dia_semana == 6:  # Domingo
            print("🚀 [DOMINGO] Executando: Reels Leads (Captura de Leads com base no PDF gerado às 4h)")
            subprocess.run(["python", "main.py", "--type", "reels_leads"])
        else:
            print("🚀 Executando: Reels e Story da Manhã")
            subprocess.run(["python", "main.py", "--type", "reels"])
            time.sleep(10)
            subprocess.run(["python", "main.py", "--type", "story_manha"])

    elif hora == 7:
        print("🚀 Executando: Pexels Story")
        subprocess.run(["python", "main.py", "--type", "pexels_story"])

    elif hora == 8:
        if dia_semana == 0:  # Segunda-feira
            minuto = brt_now.minute
            if minuto < 20:  # ~08:00
                print("🚀 [SEGUNDA] Executando: Olhos da Rede Semanal")
                subprocess.run(["python", "-c", "import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); from core.ai.olhos_da_rede import coletar_e_salvar_semanal; coletar_e_salvar_semanal()"])
            elif minuto >= 20:  # ~08:30
                print("🧠 [SEGUNDA] Executando: Analisador Semanal + IA Estrategista")
                subprocess.run(["python", "core/analytics/rodar_analytics.py", "--ciclo", "semanal"])
        else:
            print("💤 Nenhuma tarefa específica agendada para as 8:00 BRT nos outros dias.")

    elif hora == 9:
        print("🚀 Executando: Carousel")
        subprocess.run(["python", "main.py", "--type", "carousel"])

    elif hora == 12:
        print("🚀 Executando: Reels do almoço")
        subprocess.run(["python", "main.py", "--type", "reels"])

    elif hora == 17:
        print("🚀 Executando: Story da Tarde")
        subprocess.run(["python", "main.py", "--type", "story_tarde"])

    elif hora == 18:
        print("🚀 Executando: Reels da noite (narrativo)")
        subprocess.run(["python", "main.py", "--type", "reels_noite"])

    elif hora == 19:
        print("🚀 Executando: Pexels Story da noite (cinematógrafico)")
        subprocess.run(["python", "main.py", "--type", "pexels_story_noite"])

    elif hora == 22:
        print("🚀 Executando: Reels Conquistador (Atração de Público)")
        subprocess.run(["python", "main.py", "--type", "reels_conquistador"])

    # Sempre verifica e processa pedidos pendentes do Studio de Criação (Dashboard)
    # Roda a cada hora para não deixar nenhuma solicitação esperando
    try:
        print("📥 Verificando solicitações pendentes do Studio de Criação (Dashboard)...")
        subprocess.run(["python", "core/publisher/executor_usuario.py"])
    except Exception as e_req:
        print(f"⚠️ Aviso no processador do Studio de Criação: {e_req}")

    # Sempre executa o monitor de comentários ao final de qualquer ciclo agendado
    try:
        print("💬 Executando verificação e resposta automática de comentários...")
        subprocess.run(["python", "core/publisher/gerenciador_comentarios.py"])
    except Exception as e_comm:
        print(f"⚠️ Aviso no monitor de comentários: {e_comm}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        tipo = sys.argv[2] if len(sys.argv) > 2 else None
        if tipo == "comentarios":
            print("🚀 Executando manualmente: Monitor de Comentários")
            subprocess.run(["python", "core/publisher/gerenciador_comentarios.py"])
        elif tipo == "analytics":
            print("🚀 Executando manualmente: Analytics Diário")
            subprocess.run(["python", "core/analytics/rodar_analytics.py"])
        elif tipo == "weekly_report":
            print("Executando manualmente: Relatorio Semanal")
            subprocess.run(["python", "core/analytics/rodar_analytics.py", "--ciclo", "semanal"])
            subprocess.run(["python", "-c", "import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); from core.analytics.analisador_semanal import analisar_semana; analisar_semana()"])
            subprocess.run(["python", "core/reports/weekly.py"])
        elif tipo in ("mensal", "trimestral", "semestral", "anual"):
            print(f"Executando manualmente: Relatorio {tipo.upper()}")
            subprocess.run(["python", "core/reports/periodic.py", tipo])
        elif tipo == "gerador_pdf":
            print("🚀 Executando manualmente: Gerador de PDF Semanal")
            subprocess.run(["python", "gerador_pdf/gerador.py"])
        elif tipo == "user_requests":
            print("🚀 Executando manualmente: Processador do Studio de Criação")
            subprocess.run(["python", "core/publisher/executor_usuario.py"])
        elif tipo:
            print(f"Executando manualmente: {tipo}")
            subprocess.run(["python", "main.py", "--type", tipo])
        else:
            print("Tipo de post nao especificado para execucao manual.")
    else:
        rodar_agora()
