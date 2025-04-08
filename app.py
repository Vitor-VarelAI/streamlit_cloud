"""
Configuração otimizada para implantação no Streamlit Cloud.
"""
import streamlit as st
import pandas as pd
import time
import os
import datetime
from dotenv import load_dotenv

# Importar módulos personalizados
from reddit_api import RedditAPI
from openai_classifier import OpenAIClassifier
from firecrawl_summarizer import FirecrawlSummarizer

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="GummyClone Lite",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF4B4B;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #888888;
        margin-top: 0;
    }
    .card {
        background-color: #F0F2F6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .highlight {
        background-color: #FFE6E6;
        padding: 5px;
        border-radius: 5px;
    }
    .positive {
        color: #00CC96;
        font-weight: bold;
    }
    .negative {
        color: #EF553B;
        font-weight: bold;
    }
    .neutral {
        color: #636EFA;
        font-weight: bold;
    }
    .mixed {
        color: #AB63FA;
        font-weight: bold;
    }
    .divider {
        margin-top: 30px;
        margin-bottom: 30px;
        border-top: 1px solid #DDDDDD;
    }
    .filter-section {
        background-color: #F8F9FA;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .filter-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .footer {
        margin-top: 50px;
        text-align: center;
        color: #888888;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar sessão
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

if 'current_results' not in st.session_state:
    st.session_state.current_results = None

if 'current_summary' not in st.session_state:
    st.session_state.current_summary = None

# Inicializar APIs
@st.cache_resource
def load_apis():
    reddit_api = RedditAPI(use_mock_data=False)  # Using real Reddit API
    openai_classifier = OpenAIClassifier()  # Already configured to use real API when key is available
    firecrawl_summarizer = FirecrawlSummarizer()  # Already configured to use real API when key is available
    return reddit_api, openai_classifier, firecrawl_summarizer

reddit_api, openai_classifier, firecrawl_summarizer = load_apis()

# Lista de subreddits populares
POPULAR_SUBREDDITS = [
    "", "All Subreddits",
    "programming", "learnprogramming", "python", "javascript", "webdev",
    "datascience", "machinelearning", "artificial", "productivity",
    "technology", "futurology", "startups", "entrepreneur", "business",
    "marketing", "seo", "socialmedia", "web_design", "userexperience",
    "androiddev", "iOSProgramming", "gamedev", "cscareerquestions",
    "personalfinance", "investing", "cryptocurrency"
]

# Tipos de posts para filtro
POST_TYPES = [
    "Todos os tipos", "Pergunta", "Discussão", "Pedido de Ajuda", 
    "Tutorial", "Compartilhamento", "Notícia", "Opinião", "Desabafo"
]

# Funções auxiliares
def is_url(text):
    """Verifica se o texto é uma URL."""
    return text.startswith('http://') or text.startswith('https://')

def format_sentiment(sentiment):
    """Formata o sentimento com cores."""
    if sentiment.lower() == 'positivo':
        return '<span class="positive">Positivo</span>'
    elif sentiment.lower() == 'negativo':
        return '<span class="negative">Negativo</span>'
    elif sentiment.lower() == 'neutro':
        return '<span class="neutral">Neutro</span>'
    elif sentiment.lower() == 'misto':
        return '<span class="mixed">Misto</span>'
    else:
        return sentiment

def search_reddit(query, subreddit=None, limit=10, days_ago=None, only_text=False, post_type=None):
    """Busca posts no Reddit e classifica."""
    with st.spinner(f'Buscando posts sobre "{query}" no Reddit...'):
        # Buscar posts
        df = reddit_api.search_and_format(query, subreddit=subreddit, limit=limit)
        
        if df.empty:
            st.warning("Nenhum resultado encontrado.")
            return None
        
        # Classificar posts
        with st.spinner('Classificando posts com IA...'):
            df = openai_classifier.classify_posts_dataframe(df)
        
        # Criar uma cópia dos resultados originais antes de aplicar filtros
        original_count = len(df)
        st.session_state.original_results = df.copy()
        
        # Aplicar filtros adicionais
        filtered_df = df.copy()
        filters_applied = False
        
        # Filtrar por data
        if days_ago:
            filters_applied = True
            # Converter para datetime
            try:
                # Converter string de data para datetime
                filtered_df['datetime'] = pd.to_datetime(filtered_df['created_date'])
                
                # Calcular data limite
                current_date = datetime.datetime.now()
                filter_date = current_date - datetime.timedelta(days=days_ago)
                
                # Aplicar filtro
                filtered_df = filtered_df[filtered_df['datetime'] >= filter_date]
            except Exception as e:
                st.error(f"Erro ao filtrar por data: {e}")
                # Em caso de erro, não aplicar este filtro
                pass
        
        # Filtrar apenas posts com texto
        if only_text:
            filters_applied = True
            filtered_df = filtered_df[filtered_df['selftext'].str.len() > 10]
        
        # Filtrar por tipo de post
        if post_type and post_type != "Todos os tipos":
            filters_applied = True
            # Tornar a comparação case-insensitive
            filtered_df = filtered_df[filtered_df['categoria'].str.lower() == post_type.lower()]
        
        # Verificar se há resultados após filtros
        if filtered_df.empty and filters_applied:
            st.warning(f"Nenhum resultado encontrado após aplicar os filtros. Mostrando todos os {original_count} resultados originais.")
            return df  # Retornar resultados originais
        elif filtered_df.empty:
            st.warning("Nenhum resultado encontrado.")
            return None
            
        return filtered_df

def analyze_url(url):
    """Analisa um URL com Firecrawl."""
    with st.spinner(f'Analisando o link: {url}'):
        summary = firecrawl_summarizer.summarize_url(url)
        return summary

# Interface principal
def main():
    # Cabeçalho
    st.markdown('<h1 class="main-header">🧠 GummyClone Lite</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Pesquisa com IA: Analisar ideias, dores e perguntas reais no Reddit</p>', unsafe_allow_html=True)
    
    # Barra lateral
    with st.sidebar:
        st.markdown("## ⚙️ Configurações")
        
        # Opções de busca
        st.markdown("### Opções de Busca")
        search_limit = st.slider("Número de resultados", 5, 100, 10)
        
        # Histórico de buscas
        if st.session_state.search_history:
            st.markdown("### Histórico de Buscas")
            for i, query in enumerate(st.session_state.search_history[-5:]):
                if st.button(f"{query}", key=f"history_{i}"):
                    if is_url(query):
                        st.session_state.current_summary = analyze_url(query)
                        st.session_state.current_results = None
                    else:
                        st.session_state.current_results = search_reddit(query, limit=search_limit)
                        st.session_state.current_summary = None
        
        # Sobre
        st.markdown("### Sobre")
        st.markdown("""
        **GummyClone Lite** é uma ferramenta pessoal para analisar ideias, dores e perguntas reais no Reddit com ajuda de IA.
        
        Inclui integração com:
        - OpenAI para classificar posts
        - Firecrawl para resumir links
        
        Desenvolvido como projeto de demonstração.
        """)
    
    # Área de entrada
    st.markdown("## 🔍 O que você quer pesquisar hoje?")
    
    # Tabs para diferentes modos
    tab1, tab2 = st.tabs(["Buscar no Reddit", "Analisar Link"])
    
    with tab1:
        # Campo de busca principal
        col1, col2 = st.columns([4, 1])
        with col1:
            search_query = st.text_input("Digite uma palavra-chave para buscar no Reddit:", placeholder="Ex: python, javascript, produtividade...")
        with col2:
            search_button = st.button("🔍 Buscar", use_container_width=True)
        
        # Seção de filtros avançados
        with st.expander("Filtros Avançados", expanded=True):
            st.markdown('<div class="filter-section">', unsafe_allow_html=True)
            
            # Primeira linha de filtros
            col1, col2 = st.columns(2)
            
            with col1:
                # Seleção de subreddit
                subreddit = st.selectbox("Subreddit:", POPULAR_SUBREDDITS, index=1)
                if subreddit == "All Subreddits" or subreddit == "":
                    subreddit = None
                
                # Checkbox para posts com texto
                only_text = st.checkbox("Apenas posts com texto", value=False)
            
            with col2:
                # Intervalo de datas
                date_options = ["Qualquer data", "Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias"]
                date_filter = st.selectbox("Intervalo de datas:", date_options)
                
                days_ago = None
                if date_filter == "Últimos 7 dias":
                    days_ago = 7
                elif date_filter == "Últimos 30 dias":
                    days_ago = 30
                elif date_filter == "Últimos 90 dias":
                    days_ago = 90
                
                # Filtro por tipo de post
                post_type = st.selectbox("Tipo de post:", POST_TYPES)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Executar busca
        if search_button and search_query:
            # Adicionar à história
            if search_query not in st.session_state.search_history:
                st.session_state.search_history.append(search_query)
            
            # Realizar busca com filtros
            st.session_state.current_results = search_reddit(
                search_query, 
                subreddit=subreddit, 
                limit=search_limit, 
                days_ago=days_ago, 
                only_text=only_text,
                post_type=post_type
            )
            st.session_state.current_summary = None
    
    with tab2:
        col1, col2 = st.columns([4, 1])
        with col1:
            url_input = st.text_input("Cole um link para analisar:", placeholder="https://www.reddit.com/r/...")
        with col2:
            analyze_button = st.button("🔍 Analisar", use_container_width=True)
        
        if analyze_button and url_input:
            # Verificar se é uma URL válida
            if not is_url(url_input):
                st.error("Por favor, insira uma URL válida começando com http:// ou https://")
            else:
                # Adicionar à história
                if url_input not in st.session_state.search_history:
                    st.session_state.search_history.append(url_input)
                
                # Analisar URL
                st.session_state.current_summary = analyze_url(url_input)
                st.session_state.current_results = None
    
    # Exibir resultados da busca no Reddit
    if st.session_state.current_results is not None and not st.session_state.current_results.empty:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Mostrar estatísticas dos resultados
        df = st.session_state.current_results
        num_results = len(df)
        
        # Resumo dos resultados
        st.markdown(f"## 📊 Resultados da Busca ({num_results} posts encontrados)")
        
        # Estatísticas de sentimento
        sentiments = df['sentimento'].value_counts()
        
        # Mostrar estatísticas em colunas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Posts", num_results)
        
        with col2:
            positive_count = sentiments.get('Positivo', 0) + sentiments.get('positivo', 0)
            st.metric("Sentimento Positivo", positive_count)
        
        with col3:
            negative_count = sentiments.get('Negativo', 0) + sentiments.get('negativo', 0)
            st.metric("Sentimento Negativo", negative_count)
        
        with col4:
            neutral_count = sentiments.get('Neutro', 0) + sentiments.get('neutro', 0)
            st.metric("Sentimento Neutro", neutral_count)
        
        st.markdown("---")
        
        # Exibir cada post como um card
        for i, row in df.iterrows():
            with st.container():
                st.markdown(f'<div class="card">', unsafe_allow_html=True)
                
                # Título e metadados
                st.markdown(f"### {row['title']}")
                st.markdown(f"**Subreddit:** r/{row['subreddit']} | **Autor:** u/{row['author']} | **Data:** {row['created_date']} | **Score:** {row['score']} | **Comentários:** {row['num_comments']}")
                
                # Conteúdo
                if row['selftext']:
                    st.markdown(f"**Conteúdo:**\n{row['selftext']}")
                
                # Link
                st.markdown(f"[Ver post original no Reddit]({row['url']})")
                
                # Classificação
                st.markdown("#### 🧠 Análise de IA")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Categoria:** {row['categoria']}")
                    st.markdown(f"**Sentimento:** {format_sentiment(row['sentimento'])}", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**Tópicos:** {row['tópicos']}")
                
                st.markdown(f"**Insights:** {row['insights']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Exibir resumo de URL
    if st.session_state.current_summary is not None:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(f"## 📑 Resumo do Link")
        
        summary = st.session_state.current_summary
        
        with st.container():
            st.markdown(f'<div class="card">', unsafe_allow_html=True)
            
            # Título
            st.markdown(f"### {summary['title']}")
            
            # Metadados
            if 'metadata' in summary:
                metadata = summary['metadata']
                st.markdown(f"**Fonte:** {metadata.get('domain', 'Desconhecido')} | **Tempo de leitura estimado:** {metadata.get('estimated_reading_time', 'N/A')} min | **Palavras:** {metadata.get('word_count', 'N/A')}")
            
            # Tópicos principais
            if 'main_topics' in summary and summary['main_topics']:
                st.markdown("#### Tópicos Principais")
                topics_html = " | ".join([f'<span class="highlight">{topic}</span>' for topic in summary['main_topics']])
                st.markdown(topics_html, unsafe_allow_html=True)
            
            # Resumo
            st.markdown("#### Resumo")
            st.markdown(summary['summary'])
            
            # Link original
            if 'metadata' in summary and 'url' in summary['metadata']:
                st.markdown(f"[Ver conteúdo original]({summary['metadata']['url']})")
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Adicionar mensagem de debug para ajudar a identificar problemas
    st.markdown("---")
    with st.expander("🔧 Informações de Debug", expanded=False):
        # Mostrar status das APIs
        st.markdown("#### Status das APIs:")
        st.markdown(f"- **Reddit API (Modo Simulado):** {'✅ Ativo' if hasattr(reddit_api, '_load_mock_data') else '❌ Inativo'}")
        st.markdown(f"- **OpenAI Classifier:** {'✅ Ativo (Modo Simulado)' if openai_classifier.use_mock else '✅ Ativo (API Real)'}")
        st.markdown(f"- **Firecrawl Summarizer:** {'✅ Ativo (Modo Simulado)' if firecrawl_summarizer.use_mock else '✅ Ativo (API Real)'}")
        
        # Mostrar exemplo de busca
        if st.button("🔍 Testar Busca com 'python'"):
            st.markdown("#### Teste de Busca:")
            test_results = reddit_api.search_posts("python", limit=1)
            if test_results:
                st.success(f"✅ Busca funcionando! Encontrado: {test_results[0]['title']}")
                st.json(test_results[0])
            else:
                st.error("❌ Erro na busca. Nenhum resultado encontrado.")
                
        # Mostrar informações sobre filtros
        st.markdown("#### Informações sobre Filtros:")
        st.markdown("Se você estiver enfrentando problemas com os filtros, tente o seguinte:")
        st.markdown("1. Comece com uma busca simples sem filtros")
        st.markdown("2. Adicione filtros um por um para ver qual está causando o problema")
        st.markdown("3. Para alguns termos de busca, pode haver poucos resultados que correspondam a todos os filtros")
        
        # Botão para mostrar todos os resultados sem filtros
        if 'original_results' in st.session_state and st.button("Mostrar Todos os Resultados (Sem Filtros)"):
            st.session_state.current_results = st.session_state.original_results
            st.experimental_rerun()
    
    # Adicionar rodapé
    st.markdown('<div class="footer">GummyClone Lite - Desenvolvido para implantação no Streamlit Cloud</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
