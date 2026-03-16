import pandas as pd
from .base import LeitorSeguradora

class LeitorYelum(LeitorSeguradora):
    def padronizar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        
        # 🧹 Vacina Anti-Espaços
        df.columns = df.columns.str.strip()
        
        df_padronizado = pd.DataFrame()
        
        # 1. Textos
        df_padronizado['CORRETORA PRINCIPAL'] = df['Corretora Principal'].astype(str).str.strip().str.upper()
        df_padronizado['CORRETOR'] = df['Corretora'].astype(str).str.strip().str.upper()
        df_padronizado['RAMO'] = 'YELUM - NÃO INFORMADO' 
        
        # 2. Lendo o Prêmio (do arquivo original da Yelum)
        # Atenção: Se os valores vierem multiplicados por 100, é só avisar que a gente ajusta a leitura aqui!
        df_padronizado['R$ PRÊMIO LÍQUIDO'] = pd.to_numeric(df['Prêmio Emitido (R$)'], errors='coerce').fillna(0)
        
        # 3. A MÁGICA: Criando a comissão baseada na regra de 1%
        df_padronizado['R$ COMISSÃO'] = df_padronizado['R$ PRÊMIO LÍQUIDO'] * 0.01
        
        return df_padronizado