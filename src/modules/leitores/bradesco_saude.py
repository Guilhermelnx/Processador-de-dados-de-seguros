import pandas as pd
from .base import LeitorSeguradora

class LeitorBradescoSaude(LeitorSeguradora):
    def padronizar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        
        df.columns = df.columns.str.strip() 
        df_padronizado = pd.DataFrame()
        
        df_padronizado['CORRETORA PRINCIPAL'] = df['Corretora Principal'].astype(str).str.strip().str.upper()
        df_padronizado['CORRETOR'] = df['Corretora'].astype(str).str.strip().str.upper()
        df_padronizado['RAMO'] = 'SAÚDE'
        
      
        df_padronizado['R$ PRÊMIO LÍQUIDO'] = pd.to_numeric(df['Valor Prêmio'], errors='coerce').fillna(0)
        
        df_padronizado['R$ COMISSÃO'] = pd.to_numeric(df['Montante pagamento em moeda do contrato'], errors='coerce').fillna(0)
        
        return df_padronizado