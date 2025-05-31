import base64
from fpdf import FPDF
import streamlit as st
from datetime import datetime

# ===== Configurações =====
st.set_page_config(page_title="Quitério Severo - Emissão de notas de pedidos", layout="centered")

# ===== Logotipo =====
logo_path = "logo.png"
def get_image_base64(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_image_base64("logo.png")
st.markdown(
    f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="data:image/png;base64,{logo_base64}" width="200"/>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "<h1 style='text-align: center;'>Emissão de Notas de Pedidos</h1>",
    unsafe_allow_html=True
)
st.markdown("---")

col_cliente, col_produtos = st.columns([5, 5])

# ==== Coluna Dados do Cliente ====
with col_cliente:
    st.subheader("📇 Dados do Cliente")
    cliente_nome = st.text_input("Nome do Cliente")
    cliente_telefone = st.text_input("Telefone")
    cliente_endereco = st.text_input("Endereço")

# ==== Coluna Produtos ====
with col_produtos:
    st.subheader("🛍️ Adicionar Produtos")

    if "produtos" not in st.session_state:
        st.session_state.produtos = []

    with st.form("form_produto", clear_on_submit=True):
        nome_produto = st.text_input("Nome do Produto")
        quantidade = st.number_input("Quantidade", min_value=1, step=1, value=1)
        valor_unitario = st.number_input("Valor Unitário (R$)", min_value=0.0, format="%.2f")

        adicionar = st.form_submit_button("Adicionar Produto")

        if adicionar:
            if nome_produto and valor_unitario > 0:
                subtotal = quantidade * valor_unitario
                st.session_state.produtos.append({
                    "nome": nome_produto,
                    "quantidade": quantidade,
                    "valor_unitario": valor_unitario,
                    "subtotal": subtotal
                })
                st.success(f"Produto '{nome_produto}' adicionado com sucesso!")
            else:
                st.warning("Preencha pelo menos o nome do produto e valor.")

st.markdown("---")

# ===== Produtos Adicionados =====
st.subheader("📦 Produtos Adicionados")

if st.session_state.produtos:
    total_geral = 0

    for idx, item in enumerate(st.session_state.produtos):
        total_geral += item['subtotal']

        with st.container():
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(
                    f"""
                    <div style="padding:10px;border-radius:8px;border: 1px solid #ccc;">
                    <strong>🛒 {item['nome']} </strong><br>
                    <small>Quantidade: {item['quantidade']} | Valor Unitário: R$ {item['valor_unitario']:.2f} <br>
                    Subtotal: <strong>R$ {item['subtotal']:.2f}</strong></small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col2:
                if st.button("❌", key=f"remover_{idx}"):
                    st.session_state.produtos.pop(idx)
                    st.rerun()

    st.markdown(
        f"""
        <div style="padding:10px;border-radius:8px;text-align:center;color:#ffffff;">
        <h4 style="margin:0;">💰 Total Geral: <strong>R$ {total_geral:.2f}</strong></h4>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.info("Nenhum produto adicionado ainda.")

st.markdown("---")

# ===== Opções de Impressão =====
st.subheader("🖨️ Opções de Impressão")
copias = st.selectbox("Quantas cópias deseja gerar no PDF?", ["1 página", "2 páginas (iguais)"])

# ===== Função de Geração de Página do PDF =====
def adicionar_pagina_pdf(pdf):
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)

    logo_width = 50
    page_width = 210
    x_center = (page_width - logo_width) / 2
    pdf.image(logo_path, x=x_center, y=8, w=logo_width)
    pdf.ln(20)

    data_hora = datetime.now().strftime('%d/%m/%Y %H:%M')
    pdf.set_font("Arial", '', 10)
    pdf.set_xy(160, 20)
    pdf.cell(40, 8, data_hora, ln=False)
    pdf.ln(18)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, 'Dados do Cliente:', ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, f'Nome: {cliente_nome}', ln=True)
    pdf.cell(0, 5, f'Telefone: {cliente_telefone}', ln=True)
    pdf.cell(0, 5, f'Endereço: {cliente_endereco}', ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(15, 6, 'Qtd', border=1, align='C', fill=True)
    pdf.cell(105, 6, 'Produto', border=1, align='C', fill=True)
    pdf.cell(25, 6, 'Valor (R$)', border=1, align='C', fill=True)
    pdf.cell(35, 6, 'Subtotal (R$)', border=1, align='C', fill=True)
    pdf.ln(6)

    pdf.set_font("Arial", '', 9)
    total_local = 0
    for item in st.session_state.produtos:
        total_local += item['subtotal']
        pdf.cell(15, 6, str(item['quantidade']), border=1, align='C')
        pdf.cell(105, 6, item['nome'], border=1)
        pdf.cell(25, 6, f'{item["valor_unitario"]:.2f}', border=1, align='R')
        pdf.cell(35, 6, f'{item["subtotal"]:.2f}', border=1, align='R')
        pdf.ln(6)

    pdf.set_font("Arial", 'B', 9)
    pdf.cell(145, 6, 'Total Geral (R$)', border=1, align='R')
    pdf.cell(35, 6, f'{total_local:.2f}', border=1, align='R')
    pdf.ln(10)

    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, "Data de Entrega: ___________________   Assinatura: ___________________________", ln=True)
    pdf.ln(6)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, 'Quitério Severo  |  Instagram: @quisevero', align='C')

# ===== Gerar PDF =====
if st.button("📄 Gerar Pedido em PDF"):
    if not cliente_nome or not cliente_telefone or not cliente_endereco:
        st.error("Preencha todos os dados do cliente!")
    elif not st.session_state.produtos:
        st.error("Adicione pelo menos um produto!")
    else:
        pdf = FPDF()
        num_copias = 1 if copias == "1 página" else 2
        for _ in range(num_copias):
            adicionar_pagina_pdf(pdf)

        pdf_output = "pedido.pdf"
        pdf.output(pdf_output)

        with open(pdf_output, "rb") as file:
            st.download_button(
                label="📥 Baixar Pedido em PDF",
                data=file,
                file_name=f"pedido_{cliente_nome.replace(' ', '_').lower()}.pdf",
                mime="application/pdf"
            )

        st.session_state.produtos = []
