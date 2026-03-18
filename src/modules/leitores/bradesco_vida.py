import pandas as pd
from .base import LeitorSeguradora

class LeitorBradescoVida(LeitorSeguradora):
    def padronizar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        
        # 🧹 Limpar os espaços invisíveis nas colunas
        df.columns = df.columns.str.strip()
        
        df_padronizado = pd.DataFrame()
        
        # 1. Textos
        df_padronizado['CORRETORA PRINCIPAL'] = df['Corretora Principal'].astype(str).str.strip().str.upper()
        df_padronizado['CORRETOR'] = df['Nome do Corretor'].astype(str).str.strip().str.upper()
        df_padronizado['RAMO'] = 'BRADESCO - VIDA E PREVIDÊNCIA' 
        
        # 2. Valores Financeiros
        # Se por acaso a coluna estiver mesmo cortada no ficheiro original, 
        # podes alterar 'Valor de Produção' para 'Valor de Produ'
        nome_coluna_premio = 'Valor de Produção' if 'Valor de Produção' in df.columns else [c for c in df.columns if 'Valor de Produ' in c][0]
        
        df_padronizado['R$ PRÊMIO LÍQUIDO'] = pd.to_numeric(df[nome_coluna_premio], errors='coerce').fillna(0)
        df_padronizado['R$ COMISSÃO'] = pd.to_numeric(df['Valor Adicional'], errors='coerce').fillna(0)
        
        return df_padronizado