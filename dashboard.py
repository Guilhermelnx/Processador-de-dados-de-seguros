import streamlit as st
from decimal import Decimal, ROUND_HALF_UP

# Importações dos Módulos Base
from src.modules.processador import ProcessadorDados
from src.utils.exportador import gerar_excel_memoria, gerar_excel_pagamentos

# Importações dos Leitores (Dicionário Mágico)
from src.modules.leitores import LeitorAllianz, LeitorBradescoSaude
from src.modules.leitores.yelum import LeitorYelum
from src.modules.leitores.bradesco_vida import LeitorBradescoVida
from src.modules.leitores.bradesco_auto import LeitorBradescoAuto
from src.modules.leitores.suhai import LeitorSuhai
from src.modules.leitores.chubb import LeitorChubb
from src.modules.leitores.amil import LeitorAmil
from src.modules.leitores.aruana import LeitorAurana
from src.modules.leitores.darwin import LeitorDarwin
from src.modules.leitores.hdi import LeitorHDI

st.set_page_config(layout="wide", page_title="App A12 - Comissões")

# ==========================================
# 1. MAPEAMENTO DE LEITORES
# ==========================================
LEITORES_DISPONIVEIS = {
    "Allianz": LeitorAllianz,
    "Bradesco Saúde": LeitorBradescoSaude,
    "Bradesco Vida": LeitorBradescoVida,
    "Bradesco Auto": LeitorBradescoAuto,
    "Yelum": LeitorYelum,
    "Suhai": LeitorSuhai,
    "Chubb": LeitorChubb,
    "Amil": LeitorAmil,
    "Aruana": LeitorAurana,
    "Darwin": LeitorDarwin,
    "HDI": LeitorHDI,
}

# ==========================================
# 2. FUNÇÕES DE INTERFACE (COMPONENTES)
# ==========================================
def formatar_moeda(valor):
    """Formata números para o padrão de moeda brasileiro (R$ 0.000,00)"""
    valor_exato = Decimal(str(valor)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return f"R$ {valor_exato:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def renderizar_kpis_financeiros(df_final, seguradora_escolhida):
    """Renderiza a seção de Resumo Financeiro (Cards)"""
    st.write("### 💰 Resumo Financeiro")

    total_premio = df_final['R$ PRÊMIO LÍQUIDO'].sum()
    total_comissao = df_final['R$ COMISSÃO'].sum()
    total_lucro = df_final['Lucro Líquido Pago'].sum()
    total_imposto = df_final['Impostos Retidos'].sum()
    total_a12 = df_final['Repasse A12'].sum()
    total_sol = df_final['Repasse SOL'].sum()

    if seguradora_escolhida == "Bradesco Auto":
        premio_auto = df_final[df_final['RAMO'] == 'BRADESCO - AUTO']['R$ PRÊMIO LÍQUIDO'].sum()
        premio_re = df_final[df_final['RAMO'] == 'BRADESCO - RE']['R$ PRÊMIO LÍQUIDO'].sum()
        
        col1a, col1b, col2, col3 = st.columns(4)
        col1a.metric("Prêmio AUTO 🚗", formatar_moeda(premio_auto))
        col1b.metric("Prêmio RE 🏢", formatar_moeda(premio_re))
        col2.metric("Total Comissão Bruta", formatar_moeda(total_comissao))
        col3.metric("Lucro Líquido Pago", formatar_moeda(total_lucro))
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Prêmio Líquido", formatar_moeda(total_premio))
        col2.metric("Total Comissão Bruta", formatar_moeda(total_comissao))
        col3.metric("Lucro Líquido Pago", formatar_moeda(total_lucro))

    col4, col5, col6 = st.columns(3)
    col4.metric("Total de Impostos Retidos", formatar_moeda(total_imposto))
    col5.metric("Repasse A12", formatar_moeda(total_a12))
    col6.metric("Repasse SOL", formatar_moeda(total_sol))

def renderizar_graficos_e_exportacao(df_final):
    """Renderiza a seção de Gráficos, Download e Raio-X"""
    col_grafico, col_tabela = st.columns([1, 2]) 

    with col_grafico:
        st.subheader("🏆 Top 5 Corretores")
        st.caption("Por valor de comissão gerada")
        df_grafico = df_final.groupby('CORRETOR')['R$ COMISSÃO'].sum().sort_values(ascending=False).head(5)
        st.bar_chart(df_grafico)

    with col_tabela:
        st.subheader("📥 Exportação de Dados")
        st.write("Baixe a lista completa de comissões líquidas processadas e prontas para o pagamento.")
        
        colunas_exibicao = ['CORRETORA PRINCIPAL', 'CORRETOR', 'R$ COMISSÃO', 'Repasse A12', 'Repasse SOL', 'Impostos Retidos', 'Lucro Líquido Pago']
        df_exibicao = df_final[colunas_exibicao].copy()

        df_exibicao = df_exibicao.rename(columns={
            'R$ COMISSÃO': 'Comissão Bruta',
            'Impostos Retidos': 'Impostos',
            'Lucro Líquido Pago': 'Comissão Líquida'
        })

        colunas_dinheiro = ['Comissão Bruta', 'Repasse A12', 'Repasse SOL', 'Impostos', 'Comissão Líquida']
        for col in colunas_dinheiro:
            df_exibicao[col] = df_exibicao[col].round(2)

        st.download_button(
            label="Baixar Relatório de Pagamentos (Excel)",
            data=gerar_excel_pagamentos(df_exibicao),
            file_name="relatorio_pagamentos_brasicor.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True 
        )

    # Raio-X de Auditoria
    st.markdown("---")
    st.markdown("### 🕵️‍♂️ Auditoria Detalhada (Raio-X)")
    st.dataframe(df_final, use_container_width=True, hide_index=True)


# ==========================================
# 3. CONSTRUÇÃO DA TELA (FLUXO PRINCIPAL)
# ==========================================
st.title("Análise de Comissões e Prêmios 📊")

st.sidebar.title("1. Importar Dados 📁")
arquivo_upload = st.sidebar.file_uploader("Drag and drop file here", type=["xlsx", "xls", "xlsm", "xlsb", "csv"])
seguradora_escolhida = st.sidebar.selectbox("Selecione a Seguradora", list(LEITORES_DISPONIVEIS.keys()))

leitor = LEITORES_DISPONIVEIS[seguradora_escolhida]()

if arquivo_upload is not None:
    abas = ProcessadorDados.listar_abas(arquivo_upload)
    aba_selecionada = st.sidebar.selectbox("Selecione a aba correta:", abas)
    
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
        
        st.sidebar.divider()
        st.sidebar.header("2. Filtros de Pesquisa 🔍")
        ramos, corretores, principais = processador.obter_listas_filtros()
        filtro_ramo = st.sidebar.selectbox("Ramo", ramos)
        filtro_corretor = st.sidebar.selectbox("Corretor", corretores)
        filtro_principal = st.sidebar.selectbox("Corretora Principal", principais)

        df_final = processador.processar_tabela(filtro_ramo, filtro_corretor, filtro_principal)

        if df_final.empty:
            st.warning("📭 Nenhum dado encontrado com esses filtros!")
        else:
            renderizar_kpis_financeiros(df_final, seguradora_escolhida)
            st.markdown("---")
            renderizar_graficos_e_exportacao(df_final)

else:
    st.info("👆 Bem-vindo! Para começar, faça o upload da planilha de apuração no menu lateral.")