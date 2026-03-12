import pandas as pd
import io
from calculador import calcular_repasses_corretagem


class ProcessadorDados:
    def __init__(self, arquivo_upload, nome_aba):
        """Construtor: Inicializa lendo a aba selecionada do Excel e padroniza os dados"""
        self.arquivo = arquivo_upload
        self.aba = nome_aba
        self.df_bruto = pd.read_excel(arquivo_upload, sheet_name=nome_aba)
        
        # 1. O DICIONÁRIO DE SINÔNIMOS (O "Cérebro" do tradutor)
        # Chave: O nome que o nosso sistema usa | Lista: Os nomes que vêm nas planilhas
        self.mapeamento_sinonimos = {
            'R$ COMISSÃO': ['R$ COMISSÃO', 'Comissão', 'Adicional', 'Valor Comissao', 'COMISSAO', 'Valor Comissao Retida'],
            'R$ PRÊMIO LÍQUIDO': ['R$ PRÊMIO LÍQUIDO', 'Prêmio', 'Prêmio Líquido', 'PREMIO', 'Premio Liquido', 'Valor Prêmio'],
            'CORRETOR': ['CORRETOR', 'Corretor', 'Corretora', 'Nome Corretor', 'Produtor'],
            'CORRETORA PRINCIPAL': ['CORRETORA PRINCIPAL', 'Corretora principal', 'Agência', 'Filial', 'Líder'],
            'RAMO': ['RAMO', 'Ramo', 'Produto', 'Carteira', 'Grupo']
        }

        # 2. Chama a função que traduz as colunas logo na leitura
        self._padronizar_colunas()
        
        self.colunas_necessarias = ['RAMO', 'CORRETOR', 'CORRETORA PRINCIPAL', 'R$ PRÊMIO LÍQUIDO', 'R$ COMISSÃO']

    def _padronizar_colunas(self):
        """Método interno (invisível pro Dashboard) que traduz os nomes das colunas"""
        colunas_planilha = self.df_bruto.columns.tolist()
        novos_nomes = {}

        # Varre o nosso dicionário
        for nome_padrao, lista_sinonimos in self.mapeamento_sinonimos.items():
            for coluna_encontrada in colunas_planilha:
                # Compara ignorando letras maiúsculas/minúsculas e espaços extras
                if str(coluna_encontrada).strip().lower() in [s.strip().lower() for s in lista_sinonimos]:
                    novos_nomes[coluna_encontrada] = nome_padrao
                    break # Achou o correspondente, pula pro próximo

        # Executa a renomeação no Pandas
        self.df_bruto.rename(columns=novos_nomes, inplace=True)

        # 3. TRATAMENTO DE EXCEÇÃO: E se a planilha não tiver a coluna Ramo?
        # (Exatamente como aconteceu no print que você enviou)
        if 'RAMO' not in self.df_bruto.columns:
            self.df_bruto['RAMO'] = 'Não Informado'
            
        if 'CORRETORA PRINCIPAL' not in self.df_bruto.columns:
            self.df_bruto['CORRETORA PRINCIPAL'] = 'Não Informado'

    @staticmethod
    def listar_abas(arquivo_upload):
        xls = pd.ExcelFile(arquivo_upload)
        return xls.sheet_names

    def base_valida(self):
        return all(coluna in self.df_bruto.columns for coluna in self.colunas_necessarias)

    def obter_listas_filtros(self):
        df_base = self.df_bruto[self.colunas_necessarias]
        ramos = ["Todos"] + list(df_base['RAMO'].dropna().unique())
        corretores = ["Todos"] + list(df_base['CORRETOR'].dropna().unique())
        principais = ["Todos"] + list(df_base['CORRETORA PRINCIPAL'].dropna().unique())
        return ramos, corretores, principais

    def processar_tabela(self, ramo, corretor, principal):
        df_filtrado = self.df_bruto[self.colunas_necessarias].copy()
        
        # Garante que números fiquem no formato correto e remove textos perdidos nas colunas de valor
        df_filtrado['R$ PRÊMIO LÍQUIDO'] = pd.to_numeric(df_filtrado['R$ PRÊMIO LÍQUIDO'], errors='coerce').fillna(0)
        df_filtrado['R$ COMISSÃO'] = pd.to_numeric(df_filtrado['R$ COMISSÃO'], errors='coerce').fillna(0)
        
        if ramo != "Todos":
            df_filtrado = df_filtrado[df_filtrado['RAMO'] == ramo]
        if corretor != "Todos":
            df_filtrado = df_filtrado[df_filtrado['CORRETOR'] == corretor]
        if principal != "Todos":
            df_filtrado = df_filtrado[df_filtrado['CORRETORA PRINCIPAL'] == principal]
            
        # 1. Fazemos o agrupamento e guardamos numa variável
        df_agrupado = df_filtrado.groupby(['RAMO', 'CORRETOR', 'CORRETORA PRINCIPAL']).sum().reset_index()
        
        # 2. A MÁGICA: Passamos os dados limpos para a nossa calculadora externa
        df_calculado = calcular_repasses_corretagem(df_agrupado)
        
        # 3. Retornamos o resultado final pro Dashboard
        return df_calculado

    # Veja que a exportar_base_limpa fica logo abaixo, intacta!
    def exportar_base_limpa(self):
        df_limpo = self.df_bruto.copy().round(2)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_limpo.to_excel(writer, index=False)
        return buffer.getvalue()