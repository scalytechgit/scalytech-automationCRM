from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import streamlit as st
import pandas as pd
import plotly.express as px
from services.automation import processar_leads
from services.lead_service import carregar_leads

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Scalytech CRM", layout="wide")

# =========================
# SESSION STATE
# =========================
if "msg" not in st.session_state:
    st.session_state.msg = None

# =========================
# HEADER
# =========================
col1, col2 = st.columns([1, 6])

with col1:
    st.image("assets/logo.png", width=180)

with col2:
    st.markdown("<h1>Scalytech CRM</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>Sistema de automação e gestão de leads da Scalytech</p>", unsafe_allow_html=True)

st.divider()

# =========================
# LOAD DATA
# =========================
def load_data():
    data = carregar_leads()

    if isinstance(data, tuple):
        df, sheet = data
        is_google = True
    else:
        df = data
        sheet = None
        is_google = False

    df = pd.DataFrame(df).copy()

    colunas_obrigatorias = [
        "cliente",
        "email",
        "telefone",
        "status",
        "ultimo_envio"
    ]

    for col in colunas_obrigatorias:
        if col not in df.columns:
            df[col] = ""

    df["status"] = df["status"].replace("", "novo")

    validos = ["novo", "enviado", "followup", "respondido"]
    df["status"] = df["status"].apply(lambda x: x if x in validos else "novo")

    df["ultimo_envio"] = df["ultimo_envio"].astype(str)

    return df, sheet, is_google


df, sheet, is_google = load_data()

# =========================
# MÉTRICAS
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total", len(df))
c2.metric("Novos", len(df[df["status"] == "novo"]))
c3.metric("Enviados", len(df[df["status"] == "enviado"]))
c4.metric("Respondidos", len(df[df["status"] == "respondido"]))

st.divider()

# =========================
# DASHBOARD
# =========================
st.subheader("📊 Dashboard")
g1, g2 = st.columns(2)

with g1:
    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "quantidade"]
    fig = px.pie(status_counts, names="status", values="quantidade")
    st.plotly_chart(fig, use_container_width=True)

with g2:
    df_envio = df[df["ultimo_envio"] != ""].copy()

    if not df_envio.empty:
        df_envio["data"] = pd.to_datetime(df_envio["ultimo_envio"], errors="coerce").dt.date
        envios = df_envio.groupby("data").size().reset_index(name="envios")
        fig2 = px.line(envios, x="data", y="envios")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sem dados de envio ainda.")

st.divider()

# =========================
# TABELA + FILTROS
# =========================
st.subheader("📋 Gerenciar Leads")

# 🔎 FILTROS
f1, f2, f3 = st.columns(3)

with f1:
    filtro_status = st.multiselect(
        "Status",
        options=df["status"].unique(),
        default=df["status"].unique()
    )

with f2:
    filtro_cliente = st.text_input("Buscar cliente")

with f3:
    filtro_email = st.text_input("Buscar email")

# 🔥 APLICAR FILTROS
df_filtrado = df.copy()

df_filtrado = df_filtrado[df_filtrado["status"].isin(filtro_status)]

if filtro_cliente:
    df_filtrado = df_filtrado[
        df_filtrado["cliente"].str.contains(filtro_cliente, case=False, na=False)
    ]

if filtro_email:
    df_filtrado = df_filtrado[
        df_filtrado["email"].str.contains(filtro_email, case=False, na=False)
    ]

# 🔥 EDITOR
df_editado = st.data_editor(
    df_filtrado,
    use_container_width=True,
    num_rows="dynamic",
    hide_index=True,
    key="editor",
    column_config={
        "status": st.column_config.SelectboxColumn(
            "Status",
            options=["novo", "enviado", "followup", "respondido"]
        )
    }
)

# =========================
# BOTÕES
# =========================
b1, b2, b3 = st.columns(3)

# SALVAR (CORRIGIDO 🔥)
with b1:
    if st.button("💾 Salvar"):

        df_novo = df.copy()

        for i in df_editado.index:
            df_novo.loc[i] = df_editado.loc[i]

        df_novo = df_novo.fillna("").astype(str)

        if is_google:
            sheet.clear()
            sheet.append_row(df_novo.columns.tolist())

            for _, row in df_novo.iterrows():
                sheet.append_row(row.tolist())
        else:
            df_novo.to_excel("data/leads.xlsx", index=False)

        st.session_state.msg = "✅ Alterações salvas com sucesso!"
        st.rerun()

# AUTOMAÇÃO
with b2:
    if st.button("🚀 Rodar automação"):
        processar_leads()

        st.session_state.msg = "🤖 Automação executada com sucesso!"
        st.rerun()

# PDF
def gerar_pdf(df):
    path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    doc = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph("Relatório de Leads", styles["Title"]))
    elements.append(Spacer(1, 10))

    for _, row in df.iterrows():
        texto = f"""
        Cliente: {row.get('cliente','')}<br/>
        Nicho: {row.get('nicho','')}<br/>
        Email: {row.get('email','')}<br/>
        Instagram: {row.get('instagram','')}<br/>
        Site: {row.get('site','')}<br/>
        Telefone: {row.get('telefone','')}<br/>
        Status: {row.get('status','')}<br/>
        Último envio: {row.get('ultimo_envio','')}<br/>
        """
        elements.append(Paragraph(texto, styles["Normal"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    return path

with b3:
    if st.button("📄 Exportar PDF"):
        pdf = gerar_pdf(df_editado)

        with open(pdf, "rb") as f:
            st.download_button("📥 Baixar", f, file_name="leads.pdf")

# =========================
# MENSAGEM
# =========================
if st.session_state.msg:
    st.success(st.session_state.msg)
    st.session_state.msg = None

st.markdown("---")
st.caption("Scalytech © Sistema de automação comercial")