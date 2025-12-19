"""
Extrai itens e impostos de XMLs de NF-e para um DataFrame unificado.
Percorre pastas específicas, concatena resultados e exibe um resumo final.

Author: Gustavo F. Lima
License: MIT
Created: 2025
"""

import os
import glob
import xml.etree.ElementTree as ET
import pandas as pd


def extrair_dados_xml_pandas(caminho_arquivo):
    """
    Extrai dados de um XML de NF-e e retorna um DataFrame Pandas
    (uma linha por item da nota).
    """
    tree = ET.parse(caminho_arquivo)
    root = tree.getroot()
    ns = {'ns': 'http://www.portalfiscal.inf.br/nfe'}

    infNFe = root.find('.//ns:infNFe', ns)
    if infNFe is None:
        return pd.DataFrame()

    base_data = {
        "chave_acesso": infNFe.attrib.get('Id', '').replace('NFe', ''),
        "dhEmi": infNFe.findtext('.//ns:dhEmi', default='', namespaces=ns),
        "natOp": infNFe.findtext('.//ns:natOp', default='', namespaces=ns),
        "mod": infNFe.findtext('.//ns:mod', default='', namespaces=ns),
        "serie": infNFe.findtext('.//ns:serie', default='', namespaces=ns),
        "nNF": infNFe.findtext('.//ns:nNF', default='', namespaces=ns),
        "vNF": infNFe.findtext('.//ns:vNF', default='', namespaces=ns),
    }

    emit = infNFe.find('.//ns:emit', ns)
    if emit is not None:
        base_data.update({
            "CNPJ_emit": emit.findtext('ns:CNPJ', default='', namespaces=ns),
            "xNome_emit": emit.findtext('ns:xNome', default='', namespaces=ns),
            "UF_emit": emit.findtext('ns:enderEmit/ns:UF', default='', namespaces=ns),
            "cMun_emit": emit.findtext('ns:enderEmit/ns:cMun', default='', namespaces=ns),
        })

    dest = infNFe.find('.//ns:dest', ns)
    if dest is not None:
        base_data.update({
            "CNPJ_dest": dest.findtext('ns:CNPJ', default='', namespaces=ns),
            "xNome_dest": dest.findtext('ns:xNome', default='', namespaces=ns),
            "UF_dest": dest.findtext('ns:enderDest/ns:UF', default='', namespaces=ns),
            "cMun_dest": dest.findtext('ns:enderDest/ns:cMun', default='', namespaces=ns),
        })

    det_list = []
    for det in infNFe.findall('ns:det', ns):
        item_data = base_data.copy()
        item_data.update({
            "nItem": det.attrib.get('nItem', ''),
            "cProd": det.findtext('ns:prod/ns:cProd', default='', namespaces=ns),
            "cEAN": det.findtext('ns:prod/ns:cEAN', default='', namespaces=ns),
            "xProd": det.findtext('ns:prod/ns:xProd', default='', namespaces=ns),
            "NCM": det.findtext('ns:prod/ns:NCM', default='', namespaces=ns),
            "CEST": det.findtext('ns:prod/ns:CEST', default='', namespaces=ns),
            "cBenef": det.findtext('ns:prod/ns:cBenef', default='', namespaces=ns),
            "CFOP": det.findtext('ns:prod/ns:CFOP', default='', namespaces=ns),
            "uCom": det.findtext('ns:prod/ns:uCom', default='', namespaces=ns),
            "qCom": det.findtext('ns:prod/ns:qCom', default='', namespaces=ns),
            "vUnCom": det.findtext('ns:prod/ns:vUnCom', default='', namespaces=ns),
            "vProd": det.findtext('ns:prod/ns:vProd', default='', namespaces=ns),

            "ICMS_CST": det.findtext('.//ns:ICMS//ns:CST', default='', namespaces=ns),
            "ICMS_vBC": det.findtext('.//ns:ICMS//ns:vBC', default='', namespaces=ns),
            "ICMS_pICMS": det.findtext('.//ns:ICMS//ns:pICMS', default='', namespaces=ns),
            "ICMS_vICMS": det.findtext('.//ns:ICMS//ns:vICMS', default='', namespaces=ns),

            "vBCSTRet": det.findtext('.//ns:ICMS//ns:vBCSTRet', default='', namespaces=ns),
            "pST": det.findtext('.//ns:ICMS//ns:pST', default='', namespaces=ns),
            "vICMSSubstituto": det.findtext('.//ns:ICMS//ns:vICMSSubstituto', default='', namespaces=ns),
            "vICMSSTRet": det.findtext('.//ns:ICMS//ns:vICMSSTRet', default='', namespaces=ns),

            "pRedBCEfet": det.findtext('.//ns:ICMS//ns:pRedBCEfet', default='', namespaces=ns),
            "vBCEfet": det.findtext('.//ns:ICMS//ns:vBCEfet', default='', namespaces=ns),
            "pICMSEfet": det.findtext('.//ns:ICMS//ns:pICMSEfet', default='', namespaces=ns),
            "vICMSEfet": det.findtext('.//ns:ICMS//ns:vICMSEfet', default='', namespaces=ns),

            "IPI_CST": det.findtext('.//ns:IPI//ns:CST', default='', namespaces=ns),
            "IPI_vBC": det.findtext('.//ns:IPI//ns:vBC', default='', namespaces=ns),
            "IPI_pIPI": det.findtext('.//ns:IPI//ns:pIPI', default='', namespaces=ns),
            "IPI_vIPI": det.findtext('.//ns:IPI//ns:vIPI', default='', namespaces=ns),

            "PIS_CST": det.findtext('.//ns:PIS//ns:CST', default='', namespaces=ns),
            "PIS_vBC": det.findtext('.//ns:PIS//ns:vBC', default='', namespaces=ns),
            "PIS_vPIS": det.findtext('.//ns:PIS//ns:vPIS', default='', namespaces=ns),

            "COFINS_vBC": det.findtext('.//ns:COFINS//ns:vBC', default='', namespaces=ns),
            "COFINS_pCOFINS": det.findtext('.//ns:COFINS//ns:pCOFINS', default='', namespaces=ns),
            "COFINS_vCOFINS": det.findtext('.//ns:COFINS//ns:vCOFINS', default='', namespaces=ns),
        })
        det_list.append(item_data)

    return pd.DataFrame(det_list)


def main():
    pastas = [
        r"C:\Users\nome_usuario\Teste\pasta_xml_1",
        r"C:\Users\nome_usuario\Teste\pasta_xml_2",
    ]

    dfs_pandas = []
    total_arquivos = 0

    for pasta in pastas:
        arquivos_xml = glob.glob(os.path.join(pasta, "*.xml"))
        total_arquivos += len(arquivos_xml)

        for caminho_xml in arquivos_xml:
            try:
                df_xml = extrair_dados_xml_pandas(caminho_xml)
                if not df_xml.empty:
                    dfs_pandas.append(df_xml)
            except Exception as e:
                print(f"Erro no arquivo: {caminho_xml} -> {e}")

    df_final_pandas = (
        pd.concat(dfs_pandas, ignore_index=True)
        if dfs_pandas else pd.DataFrame()
    )

    print("Processamento finalizado com sucesso.")
    print(f"Total de arquivos XML encontrados: {total_arquivos}")
    print(f"Total de linhas geradas (itens de NF-e): {len(df_final_pandas)}")

    if not df_final_pandas.empty:
        print("\nAmostra dos dados:")
        print(df_final_pandas.head(5))
    else:
        print("Nenhum dado válido foi extraído.")


if __name__ == "__main__":
    main()
