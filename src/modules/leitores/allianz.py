import pandas as pd
from .base import LeitorSeguradora

class LeitorAllianz(LeitorSeguradora):
    def padronizar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        
        # 🧹 Vacina contra espaços
        df.columns = df.columns.str.strip()
        
        df_padronizado = pd.DataFrame()
        
        # 1. Textos (Agora buscando exatamente como o Raio-X mostrou: TUDO MAIÚSCULO)
        df_padronizado['CORRETORA PRINCIPAL'] = df['CORRETORA PRINCIPAL'].astype(str).str.strip().str.upper()
        df_padronizado['CORRETOR'] = df['CORRETOR'].astype(str).str.strip().str.upper()
        df_padronizado['RAMO'] = df['RAMO'].astype(str).str.strip().str.upper()
        
        # 2. Valores Financeiros (O Excel da Allianz já tem o 'R$ ' no nome da coluna original!)
        # Usamos a mesma lógica simples que consertou a Bradesco
        df_padronizado['R$ PRÊMIO LÍQUIDO'] = pd.to_numeric(df['R$ PRÊMIO LÍQUIDO'], errors='coerce').fillna(0)
        
        df_padronizado['R$ COMISSÃO'] = pd.to_numeric(df['R$ COMISSÃO'], errors='coerce').fillna(0)
        
        return df_padronizado