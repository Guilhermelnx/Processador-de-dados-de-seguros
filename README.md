📊 Insurance Commission Analyzer (MVP)
Este projeto é uma ferramenta robusta desenvolvida para automatizar a análise e o processamento de planilhas de comissões de seguros. O sistema transforma dados brutos e desorganizados em um dashboard interativo com indicadores financeiros e visualizações de performance.

🚀 O Problema
No setor de corretagem de seguros, a conciliação de comissões costuma ser feita através de arquivos Excel complexos, com múltiplas abas e formatações inconsistentes. O processo manual de filtrar e somar valores por corretor ou ramo é demorado e propenso a erros.

💡 A Solução
O Insurance Commission Analyzer automatiza esse fluxo:

Limpeza Automática: Formata valores, remove abas desnecessárias e arredonda casas decimais.

Consolidação de Dados: Agrupa milhares de linhas por Ramo, Corretor e Corretora Principal.

Dashboard Executivo: Apresenta KPIs (Total de Prêmios, Comissões e Taxas Médias) em tempo real.

Exportação Dinâmica: Permite baixar a "base limpa" pronta para integração com outros sistemas.

🛠️ Arquitetura e Tecnologias
O projeto foi construído seguindo boas práticas de Programação Orientada a Objetos (POO) e separação de responsabilidades (Backend e Frontend):

Linguagem: Python 3.12+

Interface Web: Streamlit

Processamento de Dados: Pandas

Manipulação de Excel: OpenPyXL

Estrutura: Arquitetura modular com classe de processamento (ProcessadorDados) isolada da camada de visualização.

⚙️ Como Executar
Clone o repositório: git clone https://github.com/Guilhermelnx/Processador-de-dados-de-seguros

Instale as dependências: pip install -r requirements.txt

Execute o dashboard: streamlit run dashboard.py
