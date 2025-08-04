import streamlit as st
import pandas as pd
import plotly.express as px
import sys

# Importa funções do arquivo de backend
sys.path.append('.')
from update_data import coletar_links, baixar_arquivos, processar_arquivos, analisar_e_salvar
@st.cache_data
def update_and_load_data():
    try:
        with st.spinner("🔄 Atualizando dados..."):
            file_links = coletar_links()
            downloaded_files = baixar_arquivos(file_links)
            all_dataframes = processar_arquivos(downloaded_files)
            monthy_df, corr_df = analisar_e_salvar(all_dataframes)
        st.success("✅ Dados atualizados com sucesso!")
        return monthy_df, corr_df
    except Exception as e:
        st.error(f"Erro durante atualização: {e}")
        return pd.DataFrame(), pd.DataFrame()
def display_attendance_dashboard(monthy_df):
    st.header("📊 Porcentagem de entrega de Dados - Piezômetro")
    if not monthy_df.empty and 'Node_ID' in monthy_df.columns:
        node_id = st.selectbox("Selecione um Piezômetro (Presença):", sorted(monthy_df["Node_ID"].unique()))
        df_filtrado = monthy_df[monthy_df["Node_ID"] == node_id].sort_values(by='Month')

        # Mostrar nome do mês (em inglês)
        df_filtrado['Month_Str'] = pd.to_datetime(df_filtrado['Month']).dt.strftime('%B')

        fig = px.bar(
            df_filtrado,
            x="Month_Str",
            y="Monthly_Attendance_Percentage",
            labels={"Month_Str": "Month", "Monthly_Attendance_Percentage": "Attendance (%)"},
            color="Monthly_Attendance_Percentage",
            color_continuous_scale=px.colors.sequential.Viridis
        )
        fig.update_layout(yaxis_range=[0, 100], xaxis_title="Month")
        st.subheader(f"Piezômetro Selecionado: {node_id}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir.")
def display_correlation_dashboard(df_corr):
    st.header("📈 Funcionamento do sensor - Piezômetro")

    if not df_corr.empty and 'Node_ID' in df_corr.columns:
        node_id = st.selectbox("Selecione um Piezômetro (Correlação):", sorted(df_corr["Node_ID"].unique()))
        df_filtrado = df_corr[df_corr["Node_ID"] == node_id].copy()
        df_filtrado = df_filtrado.sort_values(by='Month')

        # Mostrar nome do mês (em inglês)
        df_filtrado['Month_Str'] = pd.to_datetime(df_filtrado['Month']).dt.strftime('%B')

        # Verificar correlações acima de -0.75 e exibir mensagem única
        meses_falha = df_filtrado[df_filtrado['Correlation'] > -0.75]['Month_Str'].tolist()
        if meses_falha:
            meses_formatados = ', '.join(meses_falha)
            st.warning(f"⚠️ Possível falha no sensor ou na conversão dos dados nos meses de: {meses_formatados}.")

        fig = px.bar(
            df_filtrado,
            x="Month_Str",
            y="Correlation",
            labels={"Month_Str": "Month", "Correlation": "Correlation"},
            color_discrete_sequence=["indianred"]
        )
        fig.add_shape(
            type="line",
            x0=-0.5,
            x1=len(df_filtrado['Month_Str'].unique()) - 0.5,
            y0=-0.75,
            y1=-0.75,
            line=dict(color="Red", width=2, dash="dash")
        )
        fig.update_layout(yaxis_range=[-1, 1], xaxis_title="Month")
        st.subheader(f"Piezômetro Selecionado: {node_id}")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Dados de correlação não disponíveis.")

def main():
    st.title("🔎 Dados de Instrumentação - Barragem Biritiba")
    monthy_df, corr_df = update_and_load_data()
    display_attendance_dashboard(monthy_df)
    display_correlation_dashboard(corr_df)

if __name__ == "__main__":
    main()
