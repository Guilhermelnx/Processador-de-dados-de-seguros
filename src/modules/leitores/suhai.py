import pandas as pd
from .base import LeitorSeguradora

class LeitorSuhai(LeitorSeguradora):
    def padronizar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        
        # 🧹 Vacina Anti-Espaços
        df.columns = df.columns.str.strip()
        
        df_padronizado = pd.DataFrame()
        
        # 1. Textos
        df_padronizado['CORRETORA PRINCIPAL'] = df['Corretora Principal'].astype(str).str.strip().str.upper()
        df_padronizado['CORRETOR'] = df['nm_corretor'].astype(str).str.strip().str.upper()
        df_padronizado['RAMO'] = 'SUHAI - AUTO/MOTO' 
        
        # 2. Valores Financeiros (Agora com os nomes inteiros!)
        df_padronizado['R$ PRÊMIO LÍQUIDO'] = pd.to_numeric(df['vl_premio_tarifario'], errors='coerce').fillna(0)
        df_padronizado['R$ COMISSÃO'] = pd.to_numeric(df['vl_comissao'], errors='coerce').fillna(0)
        
        return df_padronizado