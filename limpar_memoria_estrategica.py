"""
Script de limpeza da Memória Estratégica no Firebase.
Zera os documentos 'hipoteses' e 'recomendacoes' da coleção 'memoria_estrategica'.
NÃO apaga posts, métricas, leads ou qualquer outro dado.
"""
import sys
import os

# Garante que o projeto está no path (caminho de busca do Python)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loguru import logger

def limpar_memoria_firebase():
    try:
        from core.analytics.db import get_db
        db = get_db()
        if not db:
            logger.error("❌ Não foi possível conectar ao Firebase. Verifique as credenciais.")
            return

        # Estrutura zerada para hipóteses
        memoria_zerada = {
            "hipoteses": [],
            "conhecimento_consolidado": []
        }

        # Zera o documento de hipóteses
        db.collection("memoria_estrategica").document("hipoteses").set(memoria_zerada)
        logger.success("✅ Firebase: 'memoria_estrategica/hipoteses' zerado com sucesso.")

        # Zera o documento de recomendações
        recomendacoes_zeradas = {
            "ranking_temas": [],
            "ranking_ganchos": [],
            "ranking_ctas": [],
            "contexto_para_gemini": "",
            "zerado_em": "Memória zerada para reformulação com nova estrutura de comunicação (ganchos psicológicos)."
        }
        db.collection("memoria_estrategica").document("recomendacoes").set(recomendacoes_zeradas)
        logger.success("✅ Firebase: 'memoria_estrategica/recomendacoes' zerado com sucesso.")

        logger.success("\n🧹 Limpeza concluída! O Cientista de Dados começará do zero na próxima semana.")
        logger.info("📌 Dados de posts, métricas e leads: INTACTOS.")

    except Exception as e:
        logger.error(f"❌ Erro ao limpar Firebase: {e}")

if __name__ == "__main__":
    limpar_memoria_firebase()
