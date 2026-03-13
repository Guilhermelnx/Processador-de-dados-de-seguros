import pandas as pd
from calculador import calcular_repasses_corretagem
from leitores import LeitorSeguradora

class ProcessadorDados:
    def __init__(self, arquivo_upload, nome_aba, leitor_estrategia: LeitorSeguradora):
        self.arquivo = arquivo_upload
        self.aba = nome_aba
        
        df_temporario = pd.read_excel(arquivo_upload, sheet_name=nome_aba)
        
       
        self.df_bruto = leitor_estrategia.padronizar_dados(df_temporario)
        
        self.colunas_necessarias = ['RAMO', 'CORRETORA PRINCIPAL', 'CORRETOR', 'R$ PRÊMIO LÍQUIDO', 'R$ COMISSÃO']

    @staticmethod
    def listar_abas(arquivo_upload):
        xls = pd.ExcelFile(arquivo_upload)
        return xls.sheet_names

    def base_valida(self):
        return all(coluna in self.df_bruto.columns for coluna in self.colunas_necessarias)

    def obter_listas_filtros(self):
        df_base = self.df_bruto[self.colunas_necessarias]
        ramos = ["Todos"] + list(df_base['RAMO'].dropna().unique())
        corretores = ["Todos"] + list(df_base['CORRETOR'].dropna().unique())
        principais = ["Todos"] + list(df_base['CORRETORA PRINCIPAL'].dropna().unique())
        return ramos, corretores, principais

    def processar_tabela(self, ramo, corretor, principal):
        df_filtrado = self.df_bruto[self.colunas_necessarias].copy()
        
        df_filtrado['R$ PRÊMIO LÍQUIDO'] = pd.to_numeric(df_filtrado['R$ PRÊMIO LÍQUIDO'], errors='coerce').fillna(0)
        df_filtrado['R$ COMISSÃO'] = pd.to_numeric(df_filtrado['R$ COMISSÃO'], errors='coerce').fillna(0)
        
        if ramo != "Todos":
            df_filtrado = df_filtrado[df_filtrado['RAMO'] == ramo]
        if corretor != "Todos":
            df_filtrado = df_filtrado[df_filtrado['CORRETOR'] == corretor]
        if principal != "Todos":
            df_filtrado = df_filtrado[df_filtrado['CORRETORA PRINCIPAL'] == principal]
            
        df_agrupado = df_filtrado.groupby(['RAMO', 'CORRETORA PRINCIPAL', 'CORRETOR']).sum().reset_index()
        return calcular_repasses_corretagem(df_agrupado)