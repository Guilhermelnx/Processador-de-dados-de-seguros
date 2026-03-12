# calculador.py
import pandas as pd

def calcular_repasses_corretagem(df_entrada):
    """
    Recebe um DataFrame limpo e aplica as regras de comissionamento da corretora.
    """
    # Cria uma cópia para não alterar os dados originais do filtro
    df = df_entrada.copy()

    # Constantes
    TAXA_ADICIONAL = 0.03    
    TAXA_A12 = 0.006         
    ALIQUOTA_IMPOSTO = 0.19  

    # Cálculos
    df['Adicional Bruto'] = df['R$ PRÊMIO LÍQUIDO'] * TAXA_ADICIONAL
    df['80% do Adicional'] = df['Adicional Bruto'] * 0.80
    df['A12'] = df['R$ PRÊMIO LÍQUIDO'] * TAXA_A12
    df['SOL'] = df['A12'] / 3
    df['Valor p/ Corretora'] = df['80% do Adicional'] - df['SOL']
    df['Imposto'] = df['Valor p/ Corretora'] * ALIQUOTA_IMPOSTO
    df['Lucro Líquido Pago'] = df['Valor p/ Corretora'] - df['Imposto']

    # Arredondamento
    #colunas_financeiras = [
        #'R$ PRÊMIO LÍQUIDO', 'R$ COMISSÃO', 'Adicional Bruto', '80% do Adicional', 
        #'A12', 'SOL', 'Valor p/ Corretora', 'Imposto', 'Lucro Líquido Pago'
    #]
    
    # Garante que só vai arredondar as colunas que realmente existem no df
    #colunas_presentes = [col for col in colunas_financeiras if col in df.columns]
    #df[colunas_presentes] = df[colunas_presentes].round(2)

   
    return df.fillna('')    