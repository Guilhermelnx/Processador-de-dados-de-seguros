import pandas as pd
import numpy as np

def calcular_repasses_corretagem(df_entrada):
    df = df_entrada.copy()

    comissao_real = df['R$ COMISSÃO']
    
    # ==========================================
    # 1. REGRA PADRÃO (Para 99% das corretoras)
    # ==========================================
    df['Repasse SOL'] = (comissao_real * 0.20) / 3
    df['Repasse A12'] = comissao_real * 0.20
    df['Base Corretora'] = comissao_real * 0.80
    
    # ==========================================
    # 2. IDENTIFICAÇÃO DOS "DIFERENTÕES"
    # ==========================================
    eh_grupo_m2 = (
        df['CORRETOR'].str.contains('M2', case=False, na=False) | 
        df['CORRETORA PRINCIPAL'].str.contains('M2', case=False, na=False)
    )
    
    # MELHORIA: Agora pega qualquer variação (A12+, A12 CORPORATE, PARTNER A12+)
    eh_partner_a12 = (
        df['CORRETOR'].str.contains('A12\+|A12 CORPORATE', case=False, regex=True, na=False) | 
        df['CORRETORA PRINCIPAL'].str.contains('A12\+|A12 CORPORATE', case=False, regex=True, na=False)
    )

    # ==========================================
    # 3. APLICAÇÃO DAS EXCEÇÕES
    # ==========================================
    # Exceção A: Grupo M2
    df.loc[eh_grupo_m2, 'Repasse A12'] = comissao_real * 0.70
    df.loc[eh_grupo_m2, 'Base Corretora'] = comissao_real * 0.30
    
    # Exceção B: Família A12
    df.loc[eh_partner_a12, 'Repasse SOL'] = comissao_real / 12
    df.loc[eh_partner_a12, 'Repasse A12'] = comissao_real - df.loc[eh_partner_a12, 'Repasse SOL']
    df.loc[eh_partner_a12, 'Base Corretora'] = 0

    # ==========================================
    # 4. CÁLCULO FINAL DE IMPOSTOS E LUCRO
    # ==========================================
    df['Valor p/ Corretora'] = df['Base Corretora'] - df['Repasse SOL']
    
    # REMOVIDO: A trava .clip(lower=0) foi retirada! 
    # Agora valores negativos compensam os positivos corretamente na soma final.
    
    df['Impostos Retidos'] = df['Valor p/ Corretora'] * 0.19
    df['Lucro Líquido Pago'] = df['Valor p/ Corretora'] - df['Impostos Retidos']

    df = df.drop(columns=['Base Corretora', 'Valor p/ Corretora'])

    return df.fillna(0)