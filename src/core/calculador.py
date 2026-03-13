import pandas as pd
import numpy as np

def calcular_repasses_corretagem(df_entrada):
    df = df_entrada.copy()

    # 1. Cálculo Base
    df['Adicional Bruto'] = df['R$ PRÊMIO LÍQUIDO'] * 0.03
    
    # Identifica quem é M2
    # Procura 'M2' na coluna CORRETOR ou (|) na coluna CORRETORA PRINCIPAL
    eh_grupo_m2 = (
        df['CORRETOR'].str.contains('M2', case=False, na=False) | 
        df['CORRETORA PRINCIPAL'].str.contains('M2', case=False, na=False)
    )

    # Se for M2, a A12 ganha 70% (0.70). Se for Padrão, ganha 20% (0.20)
    taxa_a12 = np.where(eh_grupo_m2, 0.70, 0.20)
    
    # Se for M2, a Corretora fica com a base de 30% (0.30). Se for Padrão, 80% (0.80)
    taxa_corretora = np.where(eh_grupo_m2, 0.30, 0.80)
    
    # 3. Aplica as fatias
    df['A12'] = df['Adicional Bruto'] * taxa_a12
    df['Base Corretora'] = df['Adicional Bruto'] * taxa_corretora
    
    # O SOL é sempre fixo: 1/3 da taxa padrão de 20% da A12
    df['SOL'] = (df['Adicional Bruto'] * 0.20) / 3
    
    # 4. Descontos e Impostos
    # A Corretora paga o SOL saindo da fatia dela
    df['Valor p/ Corretora'] = df['Base Corretora'] - df['SOL']
    
   # ... (todo o cálculo de taxas continua igualzinho) ...
    
    df['Imposto'] = df['Valor p/ Corretora'] * 0.19
    df['Lucro Líquido Pago'] = df['Valor p/ Corretora'] - df['Imposto']

    # Removemos colunas intermediárias para o Dashboard ficar limpo
    df = df.drop(columns=['Base Corretora'])

    return df.fillna('')