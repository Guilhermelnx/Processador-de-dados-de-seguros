import streamlit as st
from processador import ProcessadorDados

st.set_page_config(layout="wide", page_title="App A12 - Comissões")
st.title("Análise de Comissões e Prêmios 📊")

# 1. ÁREA DE UPLOAD
st.sidebar.header("1. Importar Dados 📁")
arquivo_upload = st.sidebar.file_uploader("Suba a planilha de apuração", type=["xlsx"])

if arquivo_upload:
    abas = ProcessadorDados.listar_abas(arquivo_upload)
    aba_selecionada = st.sidebar.selectbox("Selecione a aba correta:", abas)
    
    processador = ProcessadorDados(arquivo_upload, aba_selecionada)
    
    if not processador.base_valida():
        st.error("⚠️ As colunas necessárias não foram encontradas nesta aba.")
    else:
        st.sidebar.download_button(
            label="📥 Baixar Base Limpa (Excel)",
            data=processador.exportar_base_limpa(),
            file_name=f"Base_Limpa_{aba_selecionada}.xlsx",
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
            st.warning("Nenhum dado encontrado com esses filtros!")
        else:
            # ---------------------------------------------------------
            # CARDS DE KPIs (Indicadores)
            # ---------------------------------------------------------
            # Calculamos os totais da tabela filtrada
            total_premio = df_final['R$ PRÊMIO LÍQUIDO'].sum()
            total_comissao = df_final['R$ COMISSÃO'].sum()
            taxa_media = (total_comissao / total_premio * 100) if total_premio > 0 else 0

            # Função rápida para formatar número no padrão Brasileiro (R$ 1.000,00)
            def formata_br(valor):
                return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            st.subheader("Resumo Financeiro")
            # Divide a tela em 3 colunas
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Total Prêmio Líquido", f"R$ {formata_br(total_premio)}")
            col2.metric("💸 Total Comissão", f"R$ {formata_br(total_comissao)}")
            col3.metric("🎯 % Média de Comissão", f"{formata_br(taxa_media)}%")

            st.divider() # Linha divisória para ficar elegante

            # ---------------------------------------------------------
            # NOVIDADE 2: GRÁFICO E TABELA LADO A LADO
            # ---------------------------------------------------------
            # Divide a tela ao meio (Esquerda pro Gráfico, Direita pra Tabela)
            col_grafico, col_tabela = st.columns([1, 2]) # A tabela fica 2x mais larga que o gráfico

            with col_grafico:
                st.subheader("🏆 Top 5 Corretores")
                st.caption("Por valor de comissão gerada")
                # Agrupa por corretor, soma a comissão, ordena do maior pro menor e pega os 5 primeiros
                df_grafico = df_final.groupby('CORRETOR')['R$ COMISSÃO'].sum().sort_values(ascending=False).head(5)
                # O Streamlit desenha o gráfico de barras automático!
                st.bar_chart(df_grafico)

            with col_tabela:
                st.subheader("Tabela Consolidada")
                st.dataframe(
                    df_final, 
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "R$ PRÊMIO LÍQUIDO": st.column_config.NumberColumn("Prêmio Líquido", format="R$ %.2f"),
                        "R$ COMISSÃO": st.column_config.NumberColumn("Comissão", format="R$ %.2f")
                    }
                )

else:
    st.info("👈 Bem-vindo! Para começar, faça o upload da planilha de apuração no menu lateral.")