import streamlit as st
from decimal import Decimal, ROUND_HALF_UP
from src.modules.processador import ProcessadorDados
from src.modules.leitores import LeitorAllianz, LeitorBradescoSaude
from src.utils.exportador import gerar_excel_memoria


st.set_page_config(layout="wide", page_title="App A12 - Comissões")
st.title("Análise de Comissões e Prêmios 📊")

# ==========================================
# BARRA LATERAL (SIDEBAR)
# ==========================================
st.sidebar.title("1. Importar Dados 📁")

# 1. Botão de Upload
arquivo_upload = st.sidebar.file_uploader("Suba a planilha de apuração", type=["xlsx", "xls"])


seguradora_escolhida = st.sidebar.selectbox(
    "Selecione a Seguradora",
    ["Allianz", "Bradesco Saúde"] 
)

# A regra de qual classe usar
if seguradora_escolhida == "Allianz":
    leitor = LeitorAllianz()
elif seguradora_escolhida == "Bradesco Saúde":
    leitor = LeitorBradescoSaude()
# 4. A barreira de proteção: Só tenta ler abas e processar SE tiver arquivo
if arquivo_upload is not None:
    # Pega as abas do arquivo
    abas = ProcessadorDados.listar_abas(arquivo_upload)
    aba_selecionada = st.sidebar.selectbox("Selecione a aba correta:", abas)
    
    # 5. O PROCESSADOR NASCE AQUI (com os 3 argumentos!)
    processador = ProcessadorDados(arquivo_upload, aba_selecionada, leitor)
    #if processador.df_bruto is not None and not processador.df_bruto.empty:
    
        # 🚨 ADICIONE ESTAS DUAS LINHAS DE RAIO-X AQUI 🚨
       # st.warning("🧐 RAIO-X DOS DADOS (APENAS BRASICOR):")
        #st.dataframe(processador.df_bruto[processador.df_bruto['CORRETORA PRINCIPAL'] == 'BRASICOR'])
        
    if not processador.base_valida():
        st.error("⚠️ As colunas necessárias não foram encontradas nesta aba.")
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
            st.write("### 💰 Resumo Financeiro")

            # Função Sênior para arredondar dinheiro igual ao Excel e já formatar para o padrão BR
            def formatar_moeda(valor):
                # Converte para Decimal e força o arredondamento comercial (0.005 vira 0.01)
                valor_exato = Decimal(str(valor)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                return f"R$ {valor_exato:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            # Pegamos as somas brutas que vieram do processador
            total_premio = df_final['R$ PRÊMIO LÍQUIDO'].sum()
            total_comissao = df_final['R$ COMISSÃO'].sum()
            total_lucro = df_final['Lucro Líquido Pago'].sum()
            total_imposto = df_final['Imposto'].sum()
            total_a12 = df_final['A12'].sum()
            total_sol = df_final['SOL'].sum()

            # Desenhamos os Cards passando os valores pela nossa nova função blindada
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

                # 1. Filtramos apenas as colunas que o financeiro pediu, na ordem certa
                colunas_para_exibir = ['CORRETORA PRINCIPAL', 'CORRETOR', 'R$ COMISSÃO', 'Lucro Líquido Pago']
                df_exibicao = df_final[colunas_para_exibir].copy()

    with col_tabela:
        st.subheader("📥 Exportação de Dados")
        st.write("Baixe a lista completa de comissões líquidas processadas e prontas para o pagamento.")
        
        # 1. Preparamos os dados nos bastidores (Oculto do usuário)
        colunas_para_exibir = ['CORRETORA PRINCIPAL', 'CORRETOR', 'R$ COMISSÃO', 'Lucro Líquido Pago']
        df_exibicao = df_final[colunas_para_exibir].copy()

        df_exibicao = df_exibicao.rename(columns={
            'R$ COMISSÃO': 'Comissão Bruta',
            'Lucro Líquido Pago': 'Comissão Líquida'
        })

        df_exibicao['Comissão Bruta'] = df_exibicao['Comissão Bruta'].round(2)
        df_exibicao['Comissão Líquida'] = df_exibicao['Comissão Líquida'].round(2)

        # 2. Deixamos apenas o botão brilhando na tela!
        st.download_button(
            label="Baixar Relatório de Pagamentos (Excel)",
            data=gerar_excel_memoria(df_exibicao),
            file_name="relatorio_pagamentos_brasicor.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True # Isso faz o botão esticar e ficar com um visual bem moderno
        )


else:
    st.info("👆 Bem-vindo! Para começar, faça o upload da planilha de apuração no menu lateral.")