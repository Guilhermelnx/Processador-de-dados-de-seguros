import pandas as pd
from .base import LeitorSeguradora

class LeitorAllianz(LeitorSeguradora):
    def padronizar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        
     
        df.columns = df.columns.str.strip()
        
        df_padronizado = pd.DataFrame()
        
    
        df_padronizado['CORRETORA PRINCIPAL'] = df['Corretora Principal'].astype(str).str.strip().str.upper()
        df_padronizado['CORRETOR'] = df['Corretor'].astype(str).str.strip().str.upper()
        df_padronizado['RAMO'] = df['Ramo'].astype(str).str.strip().str.upper()
        

        df_padronizado['R$ PRÊMIO LÍQUIDO'] = pd.to_numeric(
            df['Prêmio'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce'
        ).fillna(0)
        
        df_padronizado['R$ COMISSÃO'] = pd.to_numeric(
            df['Montante pagamento em moeda do contrato'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce'
        ).fillna(0)
        
        return df_padronizado