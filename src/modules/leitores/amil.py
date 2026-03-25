import pandas as pd
import re
from .base import LeitorSeguradora

class LeitorAmil(LeitorSeguradora):
    def padronizar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        
        # ==========================================
        # 🕵️‍♂️ 1. RADAR DE PRECISÃO PROFUNDO
        # ==========================================
        colunas_str = ' '.join(df.columns.astype(str).str.lower())
        
        tem_identificador = 'corretora' in colunas_str or 'vendedor' in colunas_str
        tem_dinheiro = any(p in colunas_str for p in ['comissão', 'comissao', 'adicional', 'base'])
        
        if not (tem_identificador and tem_dinheiro):
            for i in range(min(50, len(df))):
                linha_str = ' '.join(df.iloc[i].astype(str).str.lower().tolist())
                id_ok = 'corretora' in linha_str or 'vendedor' in linha_str
                din_ok = any(p in linha_str for p in ['comissão', 'comissao', 'adicional', 'base'])
                
                if id_ok and din_ok:
                    df.columns = df.iloc[i].astype(str).str.strip()
                    df = df.iloc[i+1:].reset_index(drop=True)
                    break
        
        df = df.loc[:, ~df.columns.duplicated(keep='first')]
        df.columns = df.columns.astype(str).str.strip()
        
        df_padronizado = pd.DataFrame()

        # ==========================================
        # 🧲 2. BUSCADOR INTELIGENTE COM "PLANO B"
        # ==========================================
        def buscar_coluna_flex(lista_de_opcoes, evitar=None):
            for palavras_chave in lista_de_opcoes:
                for col in df.columns:
                    col_str = str(col).lower()
                    if evitar and any(e in col_str for e in evitar):
                        continue
                    if all(p in col_str for p in palavras_chave):
                        return df[col]
            return pd.Series(0, index=df.index)

        # ==========================================
        # 🧹 3. O SUPER TRADUTOR DE NÚMEROS (À Prova de Balas)
        # ==========================================
        def limpar_numero_br(serie):
            def converte_valor(val):
                if pd.isna(val) or str(val).strip() == '' or str(val).strip() == '-': 
                    return 0.0
                if isinstance(val, (int, float)): 
                    return float(val)
                
                s = str(val).upper().replace('R$', '').strip()
                
                if ',' in s and '.' in s:
                    if s.rfind('.') < s.rfind(','):
                        s = s.replace('.', '').replace(',', '.')
                    else:
                        s = s.replace(',', '')
                elif ',' in s:
                    s = s.replace(',', '.')
                
                s = re.sub(r'[^\d\.-]', '', s) 
                
                try:
                    return float(s)
                except ValueError:
                    return 0.0
                    
            return serie.apply(converte_valor)
# ==========================================
        # 🏗️ 4. MONTAGEM FINAL
        # ==========================================
        df_padronizado['CORRETORA PRINCIPAL'] = buscar_coluna_flex([['corretora'], ['empresa']], evitar=['cnpj']).astype(str).str.strip().str.upper()
        df_padronizado['CORRETOR'] = buscar_coluna_flex([['vendedor'], ['produtor'], ['corretor']], evitar=['cnpj']).astype(str).str.strip().str.upper()
        df_padronizado['RAMO'] = 'AMIL'
        
        df_padronizado['R$ PRÊMIO LÍQUIDO'] = limpar_numero_br(buscar_coluna_flex([['base de'], ['prêmio'], ['premio'], ['base']]))
        
        # 🎯 Apenas o Spread!
        df_padronizado['R$ COMISSÃO'] = limpar_numero_br(buscar_coluna_flex([['valor comissão'], ['valor comissao'], ['adicional'], ['comissão'], ['comiss']]))
        
        # 🧹 O Exterminador de Totais SEGURO
        # Remove APENAS a linha fantasma de "Grand Total" do rodapé (onde não há corretora)
        lixo = ['0.0', '0', 'NAN', 'NONE', '']
        df_padronizado = df_padronizado[~df_padronizado['CORRETORA PRINCIPAL'].isin(lixo)]
        
        # Só deleta se a corretora se chamar EXATAMENTE 'TOTAL' (assim não matamos os ajustes!)
        df_padronizado = df_padronizado[~df_padronizado['CORRETORA PRINCIPAL'].eq('TOTAL')]
        
        # 🛡️ O Salva-Vidas da Base de Cálculo (Agora aceita estornos negativos!)
        # Guarda a linha se ela tiver Comissão (positiva ou negativa) OU se tiver Base de Cálculo! 
        df_padronizado = df_padronizado[(df_padronizado['R$ COMISSÃO'] != 0) | (df_padronizado['R$ PRÊMIO LÍQUIDO'] != 0)]
        
        return df_padronizado