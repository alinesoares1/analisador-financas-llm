import os
import random
import datetime

# Função para criar a pasta "extrato" caso ela não exista
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Função para gerar arquivos .ofx com estrutura XML
def generate_ofx_files(num_files=1):
    # Cria a pasta extrato
    create_directory("extrato")
    
    # Listas de MCCs, nomes de estabelecimentos simulados e tipos de transação
    establishments = [
        ("Compra com Cartão", "MP*KAKABENTO", "enviado"),
        ("Compra com Cartão", "IFOOD*RESTAURANTE", "enviado"),
        ("Compra com Cartão", "UBER *VIAGEM", "enviado"),
        ("Compra com Cartão", "SHEIN *ROUPAS", "enviado"),
        ("Compra com Cartão", "SAMSCLUB", "enviado"),
        ("Compra com Cartão", "NETFLIX.COM", "enviado"),
        ("Compra com Cartão", "POSTO*GASOLINA", "enviado"),
        ("Pix - Recebido", "Transferência Fulano", "recebido"),
        ("TED Transf.Eletr.Disponiv", "João Silva", "recebido"),
        ("Pagto cartão crédito", "Banco XPTO", "enviado"),
        ("Pagamento de Boleto", "Celesc - Energia", "enviado"),
        ("Compra com Cartão", "AMAZON MKTPLACE", "enviado")
    ]
    
    for i in range(num_files):
        # Gera dados simulados
        transactions = []
        for _ in range(30):  # 100 transações por arquivo, pode ajustar conforme necessário
            transaction_id = f"2024{random.randint(1000000000000, 9999999999999)}"
            date = datetime.datetime(2024, random.randint(8, 10), random.randint(1, 28)).strftime("%Y%m%d")
            mcc_code = random.randint(1000, 9999)  # MCC fictício
            description_base, establishment_name, transaction_type = random.choice(establishments)
            value = round(random.uniform(100, 10000), 2)  # Valor absoluto
            
            # Ajusta o valor conforme o tipo de transação
            if transaction_type == "enviado":
                value = -value  # Valor negativo para envios/compras
            
            # Formata a descrição incluindo data, MCC e nome do estabelecimento
            description = f"{description_base} - {mcc_code} {establishment_name}"

            # Monta a estrutura XML da transação
            transaction_xml = f"""
                <STMTTRN>
                    <TRNTYPE>{'DEBIT' if value < 0 else 'CREDIT'}</TRNTYPE>
                    <DTPOSTED>{date}</DTPOSTED>
                    <TRNAMT>{value}</TRNAMT>
                    <FITID>{transaction_id}</FITID>
                    <NAME>{description}</NAME>
                </STMTTRN>
            """
            transactions.append(transaction_xml)
        
        # Monta o conteúdo XML completo do arquivo .ofx
        ofx_content = f"""
            OFXHEADER:100
            DATA:OFXSGML
            VERSION:102
            SECURITY:NONE
            ENCODING:USASCII
            CHARSET:1252
            COMPRESSION:NONE
            OLDFILEUID:NONE
            NEWFILEUID:NONE

            <OFX>
                <BANKMSGSRSV1>
                    <STMTTRNRS>
                        <TRNUID>1</TRNUID>
                        <STATUS>
                            <CODE>0</CODE>
                            <SEVERITY>INFO</SEVERITY>
                        </STATUS>
                        <STMTRS>
                            <CURDEF>BRL</CURDEF>
                            <BANKTRANLIST>
                                {''.join(transactions)}
                            </BANKTRANLIST>
                        </STMTRS>
                    </STMTTRNRS>
                </BANKMSGSRSV1>
            </OFX>
        """
        
        # Salva o conteúdo no arquivo .ofx na pasta extrato
        file_name = f"extrato/extrato_{i + 1}.ofx"
        with open(file_name, 'w') as f:
            f.write(ofx_content.strip())
        
    print("Arquivos OFX estruturados gerados e salvos na pasta 'extrato/'.")

# Gera os arquivos simulados
generate_ofx_files()