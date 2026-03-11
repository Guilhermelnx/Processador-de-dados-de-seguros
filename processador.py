import pandas as pd
import io

class ProcessadorDados:
    def __init__(self, arquivo_upload, nome_aba):
        """Construtor: Inicializa lendo a aba selecionada do Excel"""
        self.arquivo = arquivo_upload
        self.aba = nome_aba
        self.df_bruto = pd.read_excel(arquivo_upload, sheet_name=nome_aba)
        self.colunas_necessarias = ['RAMO', 'CORRETOR', 'CORRETORA PRINCIPAL', 'R$ PRÊMIO LÍQUIDO', 'R$ COMISSÃO']

    @staticmethod
    def listar_abas(arquivo_upload):
        """Método estático para ler os nomes das abas"""
        xls = pd.ExcelFile(arquivo_upload)
        return xls.sheet_names

    def base_valida(self):
        """Verifica se a aba tem as colunas certas"""
        return all(coluna in self.df_bruto.columns for coluna in self.colunas_necessarias)

    def obter_listas_filtros(self):
        """Devolve as listas únicas para os filtros"""
        df_base = self.df_bruto[self.colunas_necessarias]
        ramos = ["Todos"] + list(df_base['RAMO'].dropna().unique())
        corretores = ["Todos"] + list(df_base['CORRETOR'].dropna().unique())
        principais = ["Todos"] + list(df_base['CORRETORA PRINCIPAL'].dropna().unique())
        return ramos, corretores, principais

    def processar_tabela(self, ramo, corretor, principal):
        """Aplica filtros e faz o agrupamento (sum)"""
        df_filtrado = self.df_bruto[self.colunas_necessarias].copy()
        
        if ramo != "Todos":
            df_filtrado = df_filtrado[df_filtrado['RAMO'] == ramo]
        if corretor != "Todos":
            df_filtrado = df_filtrado[df_filtrado['CORRETOR'] == corretor]
        if principal != "Todos":
            df_filtrado = df_filtrado[df_filtrado['CORRETORA PRINCIPAL'] == principal]
            
        return df_filtrado.groupby(['RAMO', 'CORRETOR', 'CORRETORA PRINCIPAL']).sum().reset_index()

    def exportar_base_limpa(self):
        """Gera o Excel limpo na memória"""
        df_limpo = self.df_bruto.copy().round(2)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_limpo.to_excel(writer, index=False)
        return buffer.getvalue()