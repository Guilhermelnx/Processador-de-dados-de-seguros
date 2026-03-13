import pandas as pd
from abc import ABC, abstractmethod

# ==========================================
# 1. A NOSSA "INTERFACE" (O Contrato Base)
# ==========================================
class LeitorSeguradora(ABC):
    @abstractmethod
    def padronizar_dados(self, df_bruto):
        pass

# ==========================================
# 2. OS ESPECIALISTAS (Implementações)
# ==========================================
class LeitorAllianz(LeitorSeguradora):
    def padronizar_dados(self, df_bruto):
        mapeamento_sinonimos = {
            'R$ COMISSÃO': ['R$ COMISSÃO', 'Comissão', 'Adicional', 'Valor Comissao', 'COMISSAO', 'Valor Comissao Retida'],
            'R$ PRÊMIO LÍQUIDO': ['R$ PRÊMIO LÍQUIDO', 'Prêmio', 'Prêmio Líquido', 'PREMIO', 'Premio Liquido', 'Valor Prêmio', 'PRÊMIO LIQUIDO EMITIDO'],
            'CORRETOR': ['CORRETOR', 'Corretor', 'Corretora', 'Nome Corretor', 'Produtor'],
            'CORRETORA PRINCIPAL': ['CORRETORA PRINCIPAL', 'Corretora principal', 'Agência', 'Filial', 'Líder'],
            'RAMO': ['RAMO', 'Ramo', 'Produto', 'Carteira', 'Grupo']
        }
        
        colunas_planilha = df_bruto.columns.tolist()
        novos_nomes = {}

        for nome_padrao, lista_sinonimos in mapeamento_sinonimos.items():
            for coluna_encontrada in colunas_planilha:
                if str(coluna_encontrada).strip().lower() in [s.strip().lower() for s in lista_sinonimos]:
                    novos_nomes[coluna_encontrada] = nome_padrao
                    break
        
        df_bruto.rename(columns=novos_nomes, inplace=True)
        
        if 'RAMO' not in df_bruto.columns:
            df_bruto['RAMO'] = 'Não Informado'
        if 'CORRETORA PRINCIPAL' not in df_bruto.columns:
            df_bruto['CORRETORA PRINCIPAL'] = 'Não Informado'
            
        return df_bruto

class LeitorSeguradoraNova(LeitorSeguradora):
    def padronizar_dados(self, df_bruto):
        # O de-para manual daquela planilha diferentona
        df_bruto.rename(columns={
            'Adicional': 'R$ COMISSÃO',
            'PREMIO LIQUIDO EMITIDO': 'R$ PRÊMIO LÍQUIDO'
        }, inplace=True)
        
        if 'RAMO' not in df_bruto.columns:
            df_bruto['RAMO'] = 'Não Informado'
        if 'CORRETORA PRINCIPAL' not in df_bruto.columns:
            df_bruto['CORRETORA PRINCIPAL'] = 'Não Informado'
            
        return df_bruto