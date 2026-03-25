import pandas as pd
import numpy as np

def calcular_repasses_corretagem(df_entrada):
    df = df_entrada.copy()
    comissao_real = df['R$ COMISSÃO']

    # ==========================================
    # 1. REGRA PADRÃO vs PRÉ-CÁLCULO
    # ==========================================
    if 'Repasse SOL_PreCalc' in df.columns:
        df['Repasse SOL'] = df['Repasse SOL_PreCalc']
        df['Repasse A12'] = df['Repasse A12_PreCalc']
        df['Base Corretora'] = df['Base Corretora_PreCalc']
    else:
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
    
    eh_partner_a12 = (
        df['CORRETOR'].str.contains('A12\+|A12 CORPORATE|A12 MAIS', case=False, regex=True, na=False) | 
        df['CORRETORA PRINCIPAL'].str.contains('A12\+|A12 CORPORATE|A12 MAIS', case=False, regex=True, na=False)
    )

    # ==========================================
    # 3. APLICAÇÃO DAS EXCEÇÕES (Protegido contra o Bradesco)
    # ==========================================
    if 'Repasse SOL_PreCalc' not in df.columns:
        df.loc[eh_grupo_m2, 'Repasse A12'] = comissao_real * 0.70
        df.loc[eh_grupo_m2, 'Base Corretora'] = comissao_real * 0.30
        
        df.loc[eh_partner_a12, 'Repasse SOL'] = comissao_real / 12
        df.loc[eh_partner_a12, 'Repasse A12'] = comissao_real - df.loc[eh_partner_a12, 'Repasse SOL']
        df.loc[eh_partner_a12, 'Base Corretora'] = 0

   # ==========================================
    # 4. CÁLCULO FINAL DE IMPOSTOS E LUCRO
    # ==========================================
    df['Valor p/ Corretora'] = df['Base Corretora'] - df['Repasse SOL']
    
    # 🛡️ TRAVA DE SEGURANÇA: Ninguém tem lucro ou imposto negativo. 
    # Se a corretora repassou 100% da comissão (ex: A12+), a base dela zera.
    df['Valor p/ Corretora'] = df['Valor p/ Corretora'].clip(lower=0)

    df['Impostos Retidos'] = df['Valor p/ Corretora'] * 0.19
    df['Lucro Líquido Pago'] = df['Valor p/ Corretora'] - df['Impostos Retidos']

    df = df.drop(columns=['Base Corretora', 'Valor p/ Corretora'])
    
    # Faxina no fim da festa para as colunas de "PreCalc" não sujarem o Excel
    cols_to_drop = ['Repasse SOL_PreCalc', 'Repasse A12_PreCalc', 'Base Corretora_PreCalc']
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

    return df.fillna(0)