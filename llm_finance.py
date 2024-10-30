import ofxparse
import pandas as pd
import os
from datetime import datetime

df = pd.DataFrame()
for extrato in os.listdir("extrato"):
    with open(f'extrato/{extrato}') as ofx_file:
        ofx = ofxparse.OfxParser.parse(ofx_file)
    transactions_data = []

    for account in ofx.accounts:
        for transaction in account.statement.transactions:
            transactions_data.append({
                "Data": transaction.date,
                "Valor": transaction.amount,
                "Descrição": transaction.payee,
                "ID": transaction.id,
            })


    df_temp = pd.DataFrame(transactions_data)
    df_temp["Valor"] = df_temp["Valor"].astype(float)
    df_temp["Data"] = df_temp["Data"].apply(lambda x: x.date())
    df = pd.concat([df, df_temp])
df = df.set_index("ID")
# df["Valor"] = 1

# print(dir(transaction))
# print(df.head())


# ================
# LLM

import time
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from langchain_groq import ChatGroq
from dotenv import load_dotenv, find_dotenv
import datetime

_ = load_dotenv(find_dotenv())

# Template da prompt de categorização
template = """
Você é um analista de dados, trabalhando em um projeto de limpeza de dados.
Seu trabalho é escolher uma categoria adequada para cada lançamento financeiro
que vou te enviar.

Escolha uma dentre as seguintes categorias:
- Alimentação
- Receitas
- Saúde
- Mercado
- Educação
- Compras
- Transporte
- Investimento
- Transferências para terceiros
- Telefone
- Moradia

Escolha a categoria deste item:
{text}

Responda apenas com a categoria.
"""

# Configurar modelo Groq
prompt = PromptTemplate.from_template(template=template)
chat = ChatGroq(model="llama-3.1-8b-instant", max_tokens=30)
chain = prompt | chat | StrOutputParser()

# Função para categorizar descrições com gerenciamento de requisições
def categorize_descriptions(descriptions, batch_size=5):
    categories = []
    
    # Convertendo as descrições para uma lista simples
    descriptions_list = [desc for desc in descriptions if isinstance(desc, str)]
    
    for i in range(0, len(descriptions_list), batch_size):
        batch = descriptions_list[i:i + batch_size]
        try:
            # Categorização em lote
            batch_categories = chain.batch(batch)
            categories.extend(batch_categories)
            time.sleep(1)  # Atraso de 1 segundo entre os lotes para evitar limite de requisições
        except Exception as e:
            print(f"Erro ao processar lote: {e}")
            time.sleep(5)  # Atraso de 5 segundos em caso de erro
            continue  # Isso continua para a próxima iteração
    
    return categories

# Captura de descrições únicas
unique_descriptions = df["Descrição"].unique()

# Categorização das descrições
unique_categorias = categorize_descriptions(unique_descriptions, batch_size=5)
categories_map = dict(zip(unique_descriptions, unique_categorias))

# Mapeando as categorias para todas as linhas originais
df["Categoria"] = df["Descrição"].map(categories_map)

# Filtrando para datas específicas
df = df[df["Data"] >= datetime.date(2024, 3, 1)]

# Resetando o índice para preservar a coluna 'ID'
df.reset_index(inplace=True)

# Salvando o DataFrame no arquivo CSV
df.to_csv("finances2.csv", index=False)

print("Categorização concluída e arquivo salvo.")