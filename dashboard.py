import streamlit as st
from decimal import Decimal, ROUND_HALF_UP
from src.modules.processador import ProcessadorDados
from src.modules.leitores import LeitorAllianz, LeitorBradescoSaude
from src.modules.leitores.yelum import LeitorYelum
from src.modules.leitores.suhai import LeitorSuhai
from src.utils.exportador import gerar_excel_memoria, gerar_excel_pagamentos

st.set_page_config(layout="wide", page_title="App A12 - Comissões")
st.title("Análise de Comissões e Prêmios 📊")

# ==========================================
# MAPEAMENTO DE LEITORES (A MÁGICA DA LIMPEZA)
# ==========================================
# Adicionar uma nova seguradora agora é só colocar ela neste dicionário!
LEITORES_DISPONIVEIS = {
    "Allianz": LeitorAllianz,
    "Bradesco Saúde": LeitorBradescoSaude,
    "Yelum": LeitorYelum,
    "Suhai": LeitorSuhai,
}

# ==========================================
# BARRA LATERAL (SIDEBAR)
# ==========================================
st.sidebar.title("1. Importar Dados 📁")

arquivo_upload = st.sidebar.file_uploader("Suba a planilha de apuração", type=["xlsx", "xls"])

# O Streamlit lê as chaves do dicionário automaticamente para criar a caixinha
seguradora_escolhida = st.sidebar.selectbox("Selecione a Seguradora", list(LEITORES_DISPONIVEIS.keys()))

# Instancia o leitor escolhido sem precisar de NENHUM "if" ou "elif"!
leitor = LEITORES_DISPONIVEIS[seguradora_escolhida]()

# ==========================================
# FLUXO PRINCIPAL
# ==========================================
if arquivo_upload is not None:
    # A leitura das abas geralmente não dá erro, podemos deixar fora
    abas = ProcessadorDados.listar_abas(arquivo_upload)
    aba_selecionada = st.sidebar.selectbox("Selecione a aba correta:", abas)
    
    # 🛡️ REDE DE PROTEÇÃO ATIVADA AQUI!
    try:
        processador = ProcessadorDados(arquivo_upload, aba_selecionada, leitor)
        
        if not processador.base_valida():
            st.error("⚠️ As colunas não batem. Tem certeza que você selecionou a seguradora certa ali do lado?")
        else:
            st.sidebar.download_button(
                label="📥 Baixar Base Limpa (Excel)",
                data=gerar_excel_memoria(processador.df_bruto), 
                file_name="base_padronizada.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # 2. ÁREA DE FILTROS
            st.sidebar.divider()
            st.sidebar.header("2. Filtros de Pesquisa 🔍")
            
            ramos, corretores, principais = processador.obter_listas_filtros()
            
            filtro_ramo = st.sidebar.selectbox("Ramo", ramos)
            filtro_corretor = st.sidebar.selectbox("Corretor", corretores)
            filtro_principal = st.sidebar.selectbox("Corretora Principal", principais)

            # 3. PROCESSAMENTO DOS DADOS
            df_final = processador.processar_tabela(filtro_ramo, filtro_corretor, filtro_principal)

            if df_final.empty:
                st.warning("📭 Nenhum dado encontrado com esses filtros!")
            else:
                # ---------------------------------------------------------
                # CARDS DE KPIs (Indicadores)
                # ---------------------------------------------------------
                def formatar_moeda(valor):
                    valor_exato = Decimal(str(valor)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    return f"R$ {valor_exato:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                st.write("### 💰 Resumo Financeiro")

                total_premio = df_final['R$ PRÊMIO LÍQUIDO'].sum()
                total_comissao = df_final['R$ COMISSÃO'].sum()
                total_lucro = df_final['Lucro Líquido Pago'].sum()
                total_imposto = df_final['Impostos Retidos'].sum()
                total_a12 = df_final['Repasse A12'].sum()
                total_sol = df_final['Repasse SOL'].sum()

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Prêmio Líquido", formatar_moeda(total_premio))
                col2.metric("Total Comissão Bruta", formatar_moeda(total_comissao))
                col3.metric("Lucro Líquido Pago", formatar_moeda(total_lucro))

                col4, col5, col6 = st.columns(3)
                col4.metric("Total de Impostos Retidos", formatar_moeda(total_imposto))
                col5.metric("Repasse A12", formatar_moeda(total_a12))
                col6.metric("Repasse SOL", formatar_moeda(total_sol))

                st.markdown("---")
                
                # ---------------------------------------------------------
                # GRÁFICO E TABELA
                # ---------------------------------------------------------
                col_grafico, col_tabela = st.columns([1, 2]) 

                with col_grafico:
                    st.subheader("🏆 Top 5 Corretores")
                    st.caption("Por valor de comissão gerada")
                    df_grafico = df_final.groupby('CORRETOR')['R$ COMISSÃO'].sum().sort_values(ascending=False).head(5)
                    st.bar_chart(df_grafico)

                with col_tabela:
                    st.subheader("📥 Exportação de Dados")
                    st.write("Baixe a lista completa de comissões líquidas processadas e prontas para o pagamento.")
                    
                    colunas_para_exibir = ['CORRETORA PRINCIPAL', 'CORRETOR', 'R$ COMISSÃO', 'Lucro Líquido Pago']
                    df_exibicao = df_final[colunas_para_exibir].copy()

                    df_exibicao = df_exibicao.rename(columns={
                        'R$ COMISSÃO': 'Comissão Bruta',
                        'Lucro Líquido Pago': 'Comissão Líquida'
                    })

                    # O BOTÃO NOVO AQUI:
                    st.download_button(
                        label="Baixar Relatório de Pagamentos (Excel)",
                        data=gerar_excel_pagamentos(df_exibicao), # <--- Mudamos a função aqui!
                        file_name="relatorio_pagamentos_brasicor.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True 
                    )

    # 🛑 CASO DÊ ALGO ERRADO, ELE CAI AQUI EM VEZ DE DAR TELA VERMELHA!
    except KeyError as erro_coluna:
        st.error(f"🚨 Ops! A planilha parece estar diferente do esperado. Não encontrei a coluna: {erro_coluna}")
        st.info("💡 Dica: Verifique se você selecionou a Seguradora correta na barra lateral e se é a aba certa da planilha.")
    except Exception as erro_geral:
        st.error("🚨 Ocorreu um erro inesperado ao processar a planilha.")
        st.warning(f"Detalhe técnico para o suporte: {erro_geral}")

else:
    st.info("👆 Bem-vindo! Para começar, faça o upload da planilha de apuração no menu lateral.")