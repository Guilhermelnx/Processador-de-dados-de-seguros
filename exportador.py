
import pandas as pd
import io

def gerar_excel_memoria(df):
    """
    Recebe um DataFrame (tabela) e gera um arquivo Excel em memória 
    pronto para ser baixado pelo Streamlit.
    """
    df_export = df.copy().round(2)
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False)
        
    return buffer.getvalue()