import pandas as pd
import re
from .base import LeitorSeguradora

class LeitorAurana(LeitorSeguradora):
    def padronizar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        
        df_padronizado = pd.DataFrame()
        if df.empty:
            return df_padronizado
            
        # 1. Limpa os nomes das colunas da base para facilitar a busca
        df.columns = df.columns.astype(str).str.strip().str.lower()
        
        # 2. Buscador Simples
        def buscar_coluna(palavras_chave):
            for col in df.columns:
                if all(p in col for p in palavras_chave):
                    return df[col]
            return pd.Series(0, index=df.index)

        # 3. Limpador de Números
        def limpar_numero_br(serie):
            def converte_valor(val):
                if pd.isna(val) or str(val).strip() in ['', '-']: return 0.0
                if isinstance(val, (int, float)): return float(val)
                s = str(val).upper().replace('R$', '').strip()
                if ',' in s and '.' in s:
                    if s.rfind('.') < s.rfind(','):
                        s = s.replace('.', '').replace(',', '.')
                    else:
                        s = s.replace(',', '')
                elif ',' in s:
                    s = s.replace(',', '.')
                s = re.sub(r'[^\d\.-]', '', s) 
                try: return float(s)
                except ValueError: return 0.0
            return serie.apply(converte_valor)

# ==========================================
        # 🏗️ MONTAGEM FINAL
        # ==========================================
        df_padronizado['CORRETORA PRINCIPAL'] = buscar_coluna(['corretora principal']).astype(str).str.strip().str.upper()
        df_padronizado['CORRETOR'] = buscar_coluna(['corretor']).astype(str).str.strip().str.upper()
        df_padronizado['RAMO'] = 'ARUANA'
        
        df_padronizado['R$ PRÊMIO LÍQUIDO'] = limpar_numero_br(buscar_coluna(['prêmio']))
        df_padronizado['R$ COMISSÃO'] = limpar_numero_br(buscar_coluna(['adicional']))
        
        # 🧹 Faxina: Remove valores zerados e os "Corretores Fantasmas" (Totais/NAN)
        df_padronizado = df_padronizado[(df_padronizado['R$ COMISSÃO'] != 0) | (df_padronizado['R$ PRÊMIO LÍQUIDO'] != 0)]
        
        lixo = ['NAN', 'NONE', '', '0.0', '0']
        df_padronizado = df_padronizado[~df_padronizado['CORRETORA PRINCIPAL'].isin(lixo)]
        df_padronizado = df_padronizado[~df_padronizado['CORRETORA PRINCIPAL'].str.contains('TOTAL', case=False, na=False)]
        df_padronizado = df_padronizado[~df_padronizado['CORRETOR'].str.contains('TOTAL', case=False, na=False)]
        
        return df_padronizado