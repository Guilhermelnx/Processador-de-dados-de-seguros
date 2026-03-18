import pandas as pd
from .base import LeitorSeguradora

class LeitorChubb(LeitorSeguradora):
    def padronizar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        
        # 🧹 Limpando os espaços invisíveis
        df.columns = df.columns.str.strip()
        
        df_padronizado = pd.DataFrame()
        
        # 1. Textos
        df_padronizado['CORRETORA PRINCIPAL'] = df['Corretora Principal'].astype(str).str.strip().str.upper()
        df_padronizado['CORRETOR'] = df['Broker'].astype(str).str.strip().str.upper()
        df_padronizado['RAMO'] = 'CHUBB' 
        
        # 2. Valores Financeiros
        df_padronizado['R$ PRÊMIO LÍQUIDO'] = pd.to_numeric(df['GWP BRL'], errors='coerce').fillna(0)
        
        # 🚨 A REGRA DE NEGÓCIO AQUI: Ignoramos a comissão da Chubb e forçamos 5%
        df_padronizado['R$ COMISSÃO'] = df_padronizado['R$ PRÊMIO LÍQUIDO'] * 0.05
        
        return df_padronizado