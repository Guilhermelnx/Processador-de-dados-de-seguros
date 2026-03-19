import pandas as pd
import numpy as np
from .base import LeitorSeguradora

class LeitorBradescoAuto(LeitorSeguradora):
    def padronizar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        
        # 🧹 Limpando os espaços invisíveis
        df.columns = df.columns.str.strip()
        df_padronizado = pd.DataFrame()
        
        # 1. Textos
        df_padronizado['CORRETORA PRINCIPAL'] = df['Corretora Principal'].astype(str).str.strip().str.upper()
        df_padronizado['CORRETOR'] = df['Nome do Corretor'].astype(str).str.strip().str.upper()
        
        # 🎯 RAMO DINÂMICO
        df_padronizado['RAMO'] = df['Ctg.objeto negócio'].apply(
            lambda x: 'BRADESCO - AUTO' if str(x).strip().upper() == 'AUT' else 'BRADESCO - RE'
        )
        
        # 2. Valores Financeiros (Lendo da planilha bruta)
        nome_coluna_premio = [c for c in df.columns if 'Valor de Produ' in c][0]
        df_padronizado['R$ PRÊMIO LÍQUIDO'] = pd.to_numeric(df[nome_coluna_premio], errors='coerce').fillna(0)
        
        # A comissão global base é sempre 5% da produção
        df_padronizado['R$ COMISSÃO'] = df_padronizado['R$ PRÊMIO LÍQUIDO'] * 0.05
        
        # ==========================================
        # 🧠 3. O DICIONÁRIO DE TAXAS ("ATUAL")
        # ==========================================
        taxas_atual = {
            'BRASICOR': 0.05,
            'LIGA VITORIA': 0.05,
            'PERSPECTIVA': 0.05,
            'ALMANZA': 0.03,
            'SEGNA': 0.03,
            'SELTSEG': 0.03
        }
        
        # Função para varrer o nome da corretora e achar a taxa (se não achar, é 0)
        def buscar_taxa(nome_corretora):
            for chave, taxa in taxas_atual.items():
                if chave in nome_corretora:
                    return taxa
            return 0.0
            
        df_padronizado['Taxa Atual'] = df_padronizado['CORRETORA PRINCIPAL'].apply(buscar_taxa)
        
        # ==========================================
        # ⚙️ 4. ENGENHARIA REVERSA (O Motor de Cálculo)
        # ==========================================
        eh_auto = df_padronizado['RAMO'] == 'BRADESCO - AUTO'
        
        # A. O Ganho Intocável (Só aplica se for AUTO, no RE é zero)
        ganho_intocavel = np.where(eh_auto, df_padronizado['R$ PRÊMIO LÍQUIDO'] * df_padronizado['Taxa Atual'], 0)
        
        # B. A Base que vai para o moedor da A12 (80/20)
        # Se for AUTO, subtrai a taxa atual dos 5%. Se for RE, usa os 5% cheios.
        base_divisao = np.where(eh_auto, 
                                df_padronizado['R$ PRÊMIO LÍQUIDO'] * (0.05 - df_padronizado['Taxa Atual']), 
                                df_padronizado['R$ PRÊMIO LÍQUIDO'] * 0.05)
        
        # C. Calculando as Retenções e guardando no PreCalc
        df_padronizado['Repasse A12_PreCalc'] = base_divisao * 0.20
        df_padronizado['Repasse SOL_PreCalc'] = df_padronizado['Repasse A12_PreCalc'] / 3
        df_padronizado['Base Corretora_PreCalc'] = (base_divisao * 0.80) + ganho_intocavel
        
        # 🧹 5. LIMPEZA FINAL
        df_padronizado = df_padronizado.drop(columns=['Taxa Atual'])
        df_padronizado = df_padronizado[df_padronizado['R$ PRÊMIO LÍQUIDO'] > 0]
        
        return df_padronizado