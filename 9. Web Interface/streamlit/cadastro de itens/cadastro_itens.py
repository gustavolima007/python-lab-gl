"""
Fornece interface Streamlit para cadastro manual de itens com validações.
Mantém a lista na sessão, mostra totais e permite exportar em Excel.

Author: Gustavo F. Lima
License: MIT
Created: 2025
"""

# -*- coding: utf-8 -*-
"""
Cadastro de Itens — Versão Inicial
---------------------------------
- Interface simples e estável
- Cadastro manual de itens
- Validação de campos
- Exportação para Excel
- Compatível com Streamlit ≥ 1.30 e Python 3.12
"""

from __future__ import annotations
from io import BytesIO
import pandas as pd
import streamlit as st


# =========================
# Constantes e Session Keys
# =========================

ITEM_COLUMNS = [
    "CATEGORIA",
    "RESPONSAVEL",
    "CODIGO",
    "ITEM",
    "DESCRICAO",
    "QTDE",
    "PRECO_UNITARIO",
    "TOTAL",
]

SESSION_KEY = "items_cadastro"

K_CATEGORY = "item_category"
K_OWNER = "item_owner"


# =========================
# Helpers
# =========================

def _empty_items_df() -> pd.DataFrame:
    return pd.DataFrame(columns=ITEM_COLUMNS)


def _ensure_items_frame() -> pd.DataFrame:
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = _empty_items_df()
    return st.session_state[SESSION_KEY]


def _build_excel(items_df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        items_df.to_excel(writer, index=False, sheet_name="Itens")
    return output.getvalue()


# =========================
# Interface Principal
# =========================

def _render_items_interface() -> None:
    st.subheader("📋 Informações Gerais")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Categoria", key=K_CATEGORY)
    with col2:
        st.text_input("Responsável", key=K_OWNER)

    st.markdown("---")
    st.subheader("➕ Cadastro de Item")

    with st.form("form_item"):
        col1, col2 = st.columns(2)
        with col1:
            codigo = st.text_input("Código do Item *")
            item = st.text_input("Nome do Item *")
        with col2:
            descricao = st.text_input("Descrição")

        col3 = st.columns(3)
        qtde = col3[0].number_input("Quantidade *", min_value=0, value=0)
        preco_unit = col3[1].number_input("Preço Unitário *", min_value=0.0, value=0.0)
        total = qtde * preco_unit
        col3[2].metric("Total", f"R$ {total:,.2f}")

        submitted = st.form_submit_button("Adicionar Item")

        if submitted:
            erros = []
            if not codigo.strip():
                erros.append("Código do item é obrigatório.")
            if not item.strip():
                erros.append("Nome do item é obrigatório.")
            if qtde <= 0:
                erros.append("Quantidade deve ser maior que zero.")
            if preco_unit <= 0:
                erros.append("Preço unitário deve ser maior que zero.")

            if erros:
                st.error("⚠️ Corrija os erros:\n- " + "\n- ".join(erros))
            else:
                df = _ensure_items_frame()
                novo_item = pd.DataFrame([{
                    "CATEGORIA": st.session_state.get(K_CATEGORY, ""),
                    "RESPONSAVEL": st.session_state.get(K_OWNER, ""),
                    "CODIGO": codigo,
                    "ITEM": item,
                    "DESCRICAO": descricao,
                    "QTDE": qtde,
                    "PRECO_UNITARIO": preco_unit,
                    "TOTAL": total,
                }])

                st.session_state[SESSION_KEY] = pd.concat(
                    [df, novo_item], ignore_index=True
                )
                st.success("✅ Item cadastrado com sucesso!")

    # =========================
    # Lista de Itens
    # =========================

    st.markdown("---")
    st.subheader("📦 Itens Cadastrados")

    df_itens = _ensure_items_frame()

    if not df_itens.empty:
        st.dataframe(df_itens, use_container_width=True)

        col_btn = st.columns(3)
        if col_btn[0].button("❌ Remover último item"):
            st.session_state[SESSION_KEY] = df_itens.iloc[:-1].reset_index(drop=True)
            st.rerun()

        col_btn[2].metric(
            "💰 Total Geral",
            f"R$ {df_itens['TOTAL'].sum():,.2f}"
        )
    else:
        st.info("Nenhum item cadastrado ainda.")

    # =========================
    # Ações Finais
    # =========================

    st.markdown("---")
    col_final = st.columns(3)

    with col_final[1]:
        excel_bytes = _build_excel(df_itens)
        st.download_button(
            "📥 Baixar Excel",
            data=excel_bytes,
            file_name="cadastro_itens.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    with col_final[2]:
        if st.button("🗑️ Limpar Tudo"):
            st.session_state[SESSION_KEY] = _empty_items_df()
            st.rerun()


def run() -> None:
    st.title("Cadastro de Itens")
    st.caption("Sistema simples para cadastro e exportação de itens.")
    _render_items_interface()


if __name__ == "__main__":
    run()
