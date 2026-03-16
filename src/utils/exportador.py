import pandas as pd
import io

# A FUNÇÃO ANTIGA (Que devolvemos pra vida)
def gerar_excel_memoria(df: pd.DataFrame) -> bytes:
    """Gera um arquivo Excel simples na memória para a Base Limpa."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Base')
    return output.getvalue()

# A FUNÇÃO NOVA (Estilo Tabela Dinâmica com formatação)
def gerar_excel_pagamentos(df_exibicao: pd.DataFrame) -> bytes:
    """Gera um relatório de pagamentos agrupado estilo Tabela Dinâmica."""
    output = io.BytesIO()
    
    # Recriando a Tabela Dinâmica
    tabela_dinamica = pd.pivot_table(
        df_exibicao,
        index=['CORRETORA PRINCIPAL', 'CORRETOR'],
        values=['Comissão Bruta', 'Comissão Líquida'],
        aggfunc='sum',
        margins=True, 
        margins_name='Total Geral'
    )
    
    # Ordena as colunas
    tabela_dinamica = tabela_dinamica[['Comissão Bruta', 'Comissão Líquida']]
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        tabela_dinamica.to_excel(writer, sheet_name='Resumo Pagamentos')
        df_exibicao.to_excel(writer, sheet_name='Base de Dados', index=False)
        
        # Perfumaria de tamanho e dinheiro
        workbook = writer.book
        worksheet_resumo = writer.sheets['Resumo Pagamentos']
        formato_moeda = workbook.add_format({'num_format': 'R$ #,##0.00'})
        
        worksheet_resumo.set_column('A:A', 30) 
        worksheet_resumo.set_column('B:B', 50) 
        worksheet_resumo.set_column('C:D', 20, formato_moeda) 
        
    return output.getvalue()