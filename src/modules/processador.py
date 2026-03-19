import pandas as pd

class ProcessadorDados:
    def __init__(self, arquivo_upload, aba_selecionada, leitor):
        self.df_bruto = pd.read_excel(arquivo_upload, sheet_name=aba_selecionada)
        self.df_bruto = leitor.padronizar_dados(self.df_bruto)

    def base_valida(self):
        colunas_essenciais = ['RAMO', 'CORRETORA PRINCIPAL', 'CORRETOR', 'R$ PRÊMIO LÍQUIDO', 'R$ COMISSÃO']
        for col in colunas_essenciais:
            if col not in self.df_bruto.columns:
                return False
        return True

    @staticmethod
    def listar_abas(arquivo):
        return pd.ExcelFile(arquivo).sheet_names

    def obter_listas_filtros(self):
        ramos = ["Todos"] + sorted(self.df_bruto['RAMO'].dropna().unique().tolist())
        corretores = ["Todos"] + sorted(self.df_bruto['CORRETOR'].dropna().unique().tolist())
        principais = ["Todos"] + sorted(self.df_bruto['CORRETORA PRINCIPAL'].dropna().unique().tolist())
        return ramos, corretores, principais

    def processar_tabela(self, ramo, corretor, principal):
        df_filtrado = self.df_bruto.copy()
        
        if ramo != "Todos":
            df_filtrado = df_filtrado[df_filtrado['RAMO'] == ramo]
        if corretor != "Todos":
            df_filtrado = df_filtrado[df_filtrado['CORRETOR'] == corretor]
        if principal != "Todos":
            df_filtrado = df_filtrado[df_filtrado['CORRETORA PRINCIPAL'] == principal]
            
        if df_filtrado.empty:
            return df_filtrado
            
        # 🚨 A SALVAÇÃO ESTÁ AQUI: Ensinando o Agrupador a não apagar o PreCalc!
        colunas_soma = ['R$ PRÊMIO LÍQUIDO', 'R$ COMISSÃO']
        if 'Repasse SOL_PreCalc' in df_filtrado.columns:
            colunas_soma.extend(['Repasse SOL_PreCalc', 'Repasse A12_PreCalc', 'Base Corretora_PreCalc'])
            
        resultado = df_filtrado.groupby(['RAMO', 'CORRETORA PRINCIPAL', 'CORRETOR'], as_index=False)[colunas_soma].sum()
        
        from src.core.calculador import calcular_repasses_corretagem
        return calcular_repasses_corretagem(resultado)