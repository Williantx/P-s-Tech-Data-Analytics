import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuração da Página
st.set_page_config(page_title="Predição de Obesidade", layout="wide")

# Caminhos locais
MODEL_PATH = 'modelo_obesidade.pkl'
DATA_PATH = 'Obesity.csv'

# Carregar o modelo salvo
@st.cache_resource
def carregar_modelo():
    if not os.path.exists(MODEL_PATH):
        st.error(f"Erro: Arquivo '{MODEL_PATH}' não encontrado na pasta local.")
        return None
    return joblib.load(MODEL_PATH)

pipeline = carregar_modelo()

# Título
st.title("🏥 Sistema de Apoio ao Diagnóstico de Obesidade")
st.markdown("---")

# Abas
tab1, tab2, tab3 = st.tabs(["🔮 Predição Clínica", "📊 Dashboard Analítico", "📝 Relatórios e Insights"])


with tab1:
    st.header("Formulário do Paciente")
    col1, col2, col3 = st.columns(3)

    # --- Dicionários de Tradução (Visual -> Modelo) ---
    mapa_genero = {'Masculino': 'Male', 'Feminino': 'Female'}
    mapa_sim_nao = {'Sim': 'yes', 'Não': 'no'}
    mapa_frequencia = {
        'Às vezes': 'Sometimes', 
        'Frequentemente': 'Frequently', 
        'Sempre': 'Always', 
        'Não': 'no'
    }
    mapa_transporte = {
        'Transporte Público': 'Public_Transportation', 
        'Caminhada': 'Walking', 
        'Carro': 'Automobile', 
        'Moto': 'Motorbike', 
        'Bicicleta': 'Bike'
    }

    # Coleta de Dados
    with col1:
        # Interface mostra as chaves (PT), variável guarda a escolha
        genero_visual = st.selectbox("Gênero", list(mapa_genero.keys()))
        idade = st.number_input("Idade", 1, 120, 25)
        altura = st.number_input("Altura (m)", 0.5, 2.5, 1.70)
        peso = st.number_input("Peso (kg)", 10.0, 300.0, 70.0)
        historia_fam_visual = st.selectbox("Histórico Familiar de Sobrepeso?", list(mapa_sim_nao.keys()))

    with col2:
        favc_visual = st.selectbox("Consome comida calórica frequentemente?", list(mapa_sim_nao.keys()))
        fcvc = st.slider("Frequência de consumo de vegetais (1-3)", 1, 3, 2)
        ncp = st.slider("Número de refeições principais", 1, 4, 3)
        caec_visual = st.selectbox("Come entre refeições?", list(mapa_frequencia.keys()))
        smoke_visual = st.selectbox("Fumante?", list(mapa_sim_nao.keys()))

    with col3:
        ch2o = st.slider("Consumo de água diário (1-3L)", 1, 3, 2)
        scc_visual = st.selectbox("Monitora calorias ingeridas?", list(mapa_sim_nao.keys()))
        faf = st.slider("Frequência de atividade física (0-3)", 0, 3, 1)
        tue = st.slider("Tempo usando dispositivos (0-2)", 0, 2, 1)
        calc_visual = st.selectbox("Consumo de álcool", list(mapa_frequencia.keys()))
        mtrans_visual = st.selectbox("Meio de transporte principal", list(mapa_transporte.keys()))

    # Botão de Predição
    if st.button("Realizar Diagnóstico"):
        if pipeline:
            # Engenharia de Features: Calcular IMC
            imc = peso / (altura ** 2)
            
            # --- Conversão para o formato do Modelo (PT -> EN) ---
            # Aqui usamos os dicionários para pegar o valor em inglês correspondente à escolha em PT
            dados_input = pd.DataFrame({
                'genero': [mapa_genero[genero_visual]],
                'idade': [idade],
                'altura_m': [altura],
                'peso_kg': [peso],
                'historia_familiar_sobrepeso': [mapa_sim_nao[historia_fam_visual]],
                'come_comida_calorica_freq': [mapa_sim_nao[favc_visual]],
                'freq_consumo_vegetais': [fcvc],
                'num_refeicoes_principais': [ncp],
                'come_entre_refeicoes': [mapa_frequencia[caec_visual]],
                'fumante': [mapa_sim_nao[smoke_visual]],
                'consumo_agua_litros': [ch2o],
                'monitora_calorias': [mapa_sim_nao[scc_visual]],
                'freq_atividade_fisica': [faf],
                'tempo_uso_dispositivos': [tue],
                'freq_consumo_alcool': [mapa_frequencia[calc_visual]],
                'meio_transporte': [mapa_transporte[mtrans_visual]],
                'imc': [imc]
            })

            try:
                predicao = pipeline.predict(dados_input)[0]
                
                # Opcional: Traduzir o output final também, se desejar
                # st.success(f"### Resultado Previsto: {predicao}") 
                st.success(f"### Nível de Obesidade Previsto: {predicao}")
                st.info(f"IMC Calculado: {imc:.2f}")
            except Exception as e:
                st.error(f"Erro na predição: {e}")
                

with tab2:
    st.header("Insights da Base de Dados")
    
    if os.path.exists(DATA_PATH):
        df_dash = pd.read_csv(DATA_PATH)
        
        # --- TRADUÇÃO DOS DADOS (Visualização) ---
        # 1. Dicionário para traduzir as categorias de obesidade
        mapa_obesidade = {
            'Insufficient_Weight': 'Abaixo do Peso',
            'Normal_Weight': 'Peso Normal',
            'Overweight_Level_I': 'Sobrepeso Nível I',
            'Overweight_Level_II': 'Sobrepeso Nível II',
            'Obesity_Type_I': 'Obesidade Tipo I',
            'Obesity_Type_II': 'Obesidade Tipo II',
            'Obesity_Type_III': 'Obesidade Tipo III'
        }
        
        # 2. Criar uma coluna nova traduzida no DataFrame
        df_dash['Classificacao_PT'] = df_dash['Obesity'].map(mapa_obesidade)
        # -----------------------------------------

        # Métricas
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Pacientes", len(df_dash))
        c2.metric("Média de Peso", f"{df_dash['Weight'].mean():.1f} kg")
        c3.metric("Média de Idade", f"{df_dash['Age'].mean():.1f} anos")

        # Gráficos
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("Distribuição de Obesidade")
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            
            # Alteração: Usamos a coluna 'Classificacao_PT' no eixo Y
            sns.countplot(
                y='Classificacao_PT', 
                data=df_dash, 
                order=df_dash['Classificacao_PT'].value_counts().index, 
                palette='viridis', 
                ax=ax1
            )
            
            # Alteração: Traduzir títulos dos eixos
            ax1.set_xlabel("Quantidade de Pacientes")
            ax1.set_ylabel("") # Remove o label Y para ficar mais limpo
            st.pyplot(fig1)
            
        with col_g2:
            st.subheader("Peso vs Altura")
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            
            # Alteração: Usamos 'Classificacao_PT' no hue (cores)
            sns.scatterplot(
                x='Weight', 
                y='Height', 
                hue='Classificacao_PT', 
                data=df_dash, 
                alpha=0.6, 
                ax=ax2
            )
            
            # Alteração: Traduzir títulos dos eixos e legenda
            ax2.set_xlabel("Peso (kg)")
            ax2.set_ylabel("Altura (m)")
            # Move a legenda e traduz o título dela
            ax2.legend(title="Diagnóstico", fontsize='small')
            
            st.pyplot(fig2)
    else:
        st.warning(f"Arquivo '{DATA_PATH}' não encontrado. Coloque-o na mesma pasta do script.")

    with tab3:
        st.header("Relatórios de Inteligência de Dados")
        st.markdown("Análise detalhada dos principais fatores de risco identificados pelo modelo.")
        st.markdown("---")

        # --- Insight 1 ---
        st.subheader("1. Impacto do Histórico Familiar")
        # Coloque o nome exato do seu arquivo png abaixo
        if os.path.exists("grafico_historico.png"):
            st.image("grafico_historico.png", caption="Correlação entre Histórico e Obesidade", use_container_width=True)

        st.info("""
        **Insight para a equipe médica:** Pacientes com histórico familiar de sobrepeso têm uma probabilidade drasticamente maior de desenvolver sobrepeso ou obesidade. 
        A investigação do histórico familiar é um passo de triagem fundamental e de baixo custo.
        """)
        st.markdown("---")

        # --- Insight 2 ---
        st.subheader("2. Atividade Física como Fator de Proteção")
        if os.path.exists("grafico_atividade.png"):
            st.image("grafico_atividade.png", caption="Frequência de Atividade Física vs Peso", use_container_width=True)

        st.info("""
        **Insight para a equipe médica:** A falta de atividade física está fortemente correlacionada com os níveis mais altos de obesidade. 
        Incentivar a prática de exercícios (mesmo que 1-2 dias por semana) pode ser uma das intervenções mais eficazes.
        """)
        st.markdown("---")

        # --- Insight 3 ---
        st.subheader("3. O Transporte Diário Importa")
        if os.path.exists("grafico_transporte.png"):
            st.image("grafico_transporte.png", caption="Meio de Transporte vs IMC", use_container_width=True)

        st.info("""
        **Insight para a equipe médica:** O sedentarismo associado ao uso de Automóvel e Transporte Público é um fator de risco visível. 
        Pacientes que utilizam esses meios podem precisar de atenção extra e incentivo a caminhadas ou outras atividades compensatórias.
        """)
        st.markdown("---")

        # --- Insight 4 ---
        st.subheader("4. Distribuição de Idade por Nível de Obesidade")
        if os.path.exists("grafico_idade.png"):
            st.image("grafico_idade.png", caption="Faixa Etária e Classificação", use_container_width=True)

        st.info("""
        **Insight para a equipe médica:** A idade média tende a ser maior nos grupos com obesidade, sugerindo que o risco aumenta com o envelhecimento. 
        Programas de prevenção podem ser focados em adultos jovens para evitar a progressão para a obesidade.
        """)
