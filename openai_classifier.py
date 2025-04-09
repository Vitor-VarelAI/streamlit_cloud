"""
Módulo para integração com a API da OpenAI para classificação de posts.
"""
import os
import json
import time
import httpx
from openai import OpenAI
import pandas as pd
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OpenAIClassifier:
    """Classe para classificar posts usando a API da OpenAI."""
    
    def __init__(self):
        """Inicializa a classe OpenAIClassifier."""
        # Verificar se a OpenAI API está disponível
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            try:
                api_key = st.secrets.openai.api_key
                logging.info("Found OpenAI API key in Streamlit secrets")
            except (AttributeError, KeyError):
                logging.warning("OpenAI API key not found in environment or secrets")
                api_key = None
        
        self.use_mock = not api_key
        if self.use_mock:
            logging.warning("Using mock classification mode (no API key)")
        
        self.last_request_time = 0
        self.request_delay = 1  # Delay em segundos para evitar rate limiting
    
    def _respect_rate_limit(self):
        """Respeita o rate limit da API."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.request_delay:
            time.sleep(self.request_delay - time_since_last_request)
        
        self.last_request_time = time.time()
    
    def _mock_classify_post(self, post_title, post_text):
        """
        Simula a classificação de um post quando a API não está disponível.
        
        Args:
            post_title (str): Título do post.
            post_text (str): Texto do post.
            
        Returns:
            dict: Classificação simulada do post.
        """
        # Categorias comuns para classificação
        categories = [
            "Pergunta", "Discussão", "Pedido de Ajuda", "Tutorial", 
            "Compartilhamento", "Notícia", "Opinião", "Desabafo"
        ]
        
        # Sentimentos possíveis
        sentiments = ["Positivo", "Neutro", "Negativo", "Misto"]
        
        # Tópicos comuns baseados no conteúdo
        topics = [
            "Programação", "Tecnologia", "Carreira", "Educação",
            "Desenvolvimento Web", "Ciência de Dados", "Inteligência Artificial",
            "Produtividade", "Negócios", "Marketing", "Design", "Mobile"
        ]
        
        # Simular classificação baseada em palavras-chave no título e texto
        title_lower = post_title.lower()
        text_lower = post_text.lower()
        
        # Determinar categoria
        if "?" in post_title or "como" in title_lower or "dúvida" in title_lower:
            category = "Pergunta"
        elif "ajuda" in title_lower or "problema" in title_lower:
            category = "Pedido de Ajuda"
        elif "tutorial" in title_lower or "guia" in title_lower or "como fazer" in title_lower:
            category = "Tutorial"
        elif "notícia" in title_lower or "lançamento" in title_lower or "anúncio" in title_lower:
            category = "Notícia"
        elif "opinião" in title_lower or "acho que" in title_lower:
            category = "Opinião"
        elif "compartilhando" in title_lower or "criei" in title_lower:
            category = "Compartilhamento"
        elif "desabafo" in title_lower or "frustrado" in title_lower:
            category = "Desabafo"
        else:
            category = "Discussão"
        
        # Determinar sentimento
        if any(word in text_lower for word in ["ótimo", "excelente", "bom", "gosto", "feliz", "sucesso"]):
            sentiment = "Positivo"
        elif any(word in text_lower for word in ["ruim", "péssimo", "problema", "difícil", "frustrado", "triste"]):
            sentiment = "Negativo"
        elif any(word in text_lower for word in ["mas", "porém", "entretanto", "contudo"]) and (
            any(word in text_lower for word in ["bom", "gosto"]) and 
            any(word in text_lower for word in ["ruim", "problema"])):
            sentiment = "Misto"
        else:
            sentiment = "Neutro"
        
        # Determinar tópicos
        post_topics = []
        topic_keywords = {
            "Programação": ["código", "programação", "programar", "função", "algoritmo"],
            "Tecnologia": ["tecnologia", "tech", "inovação", "gadget", "dispositivo"],
            "Carreira": ["carreira", "emprego", "trabalho", "vaga", "entrevista", "cv", "currículo"],
            "Educação": ["aprender", "curso", "estudar", "faculdade", "universidade", "bootcamp"],
            "Desenvolvimento Web": ["web", "site", "frontend", "backend", "html", "css", "javascript"],
            "Ciência de Dados": ["dados", "data", "análise", "estatística", "pandas", "visualização"],
            "Inteligência Artificial": ["ia", "ai", "machine learning", "ml", "modelo", "gpt", "neural"],
            "Produtividade": ["produtividade", "eficiência", "organização", "tempo", "hábito"],
            "Negócios": ["negócio", "empresa", "startup", "empreendedor", "mercado", "cliente"],
            "Marketing": ["marketing", "divulgação", "propaganda", "audiência", "cliente", "seo"],
            "Design": ["design", "ui", "ux", "interface", "usuário", "experiência", "visual"],
            "Mobile": ["mobile", "app", "aplicativo", "android", "ios", "celular", "smartphone"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in title_lower or keyword in text_lower for keyword in keywords):
                post_topics.append(topic)
        
        # Se nenhum tópico for identificado, adicionar um genérico
        if not post_topics:
            post_topics = ["Discussão Geral"]
        
        # Gerar insights simulados
        insights = []
        
        if category == "Pergunta" or category == "Pedido de Ajuda":
            insights.append("O usuário está buscando informações ou assistência.")
        
        if sentiment == "Negativo":
            insights.append("O tom do post sugere frustração ou dificuldade com o assunto.")
        elif sentiment == "Positivo":
            insights.append("O usuário demonstra entusiasmo ou satisfação com o tema.")
        
        if "Programação" in post_topics or "Desenvolvimento Web" in post_topics:
            insights.append("Este post está relacionado a desenvolvimento de software.")
        
        if "Carreira" in post_topics:
            insights.append("O usuário pode estar em transição de carreira ou buscando crescimento profissional.")
        
        # Adicionar insight genérico se poucos foram gerados
        if len(insights) < 2:
            insights.append("Este post parece ser relevante para a comunidade de tecnologia.")
        
        # Retornar classificação simulada
        return {
            "categoria": category,
            "sentimento": sentiment,
            "tópicos": post_topics,
            "insights": insights
        }
    
    def classify_post(self, post_title, post_text):
        """
        Classifica um post usando a API da OpenAI.
        
        Args:
            post_title (str): Título do post.
            post_text (str): Texto do post.
            
        Returns:
            dict: Classificação do post.
        """
        self._respect_rate_limit()
        
        # Se estiver no modo simulado, usar classificação simulada
        if self.use_mock:
            return self._mock_classify_post(post_title, post_text)
        
        try:
            # Try to get API key
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                try:
                    api_key = st.secrets.openai.api_key
                except (AttributeError, KeyError):
                    logging.error("OpenAI API key not found in environment or secrets")
                    return self._mock_classify_post(post_title, post_text)
            
            # Using a custom httpx client without proxies
            http_client = httpx.Client(
                base_url="https://api.openai.com",
                follow_redirects=True,
                timeout=60.0
            )
            
            # Create a new client with our custom http_client
            client = OpenAI(
                api_key=api_key,
                http_client=http_client
            )
            
            logging.info("Created custom OpenAI client without proxies in classifier")
            
            # Preparar o prompt para a API
            prompt = f"""
            Analise o seguinte post do Reddit e forneça uma classificação detalhada:
            
            Título: {post_title}
            
            Texto: {post_text}
            
            Forneça uma análise no seguinte formato JSON:
            {{
                "categoria": "Categoria do post (ex: Pergunta, Discussão, Pedido de Ajuda, Tutorial, etc.)",
                "sentimento": "Tom geral do post (Positivo, Neutro, Negativo, Misto)",
                "tópicos": ["Lista de tópicos relevantes abordados no post"],
                "insights": ["Lista de insights ou observações sobre o post"]
            }}
            
            Responda apenas com o JSON, sem texto adicional.
            """
            
            # Fazer a chamada para a API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em analisar posts do Reddit."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={ "type": "json_object" }
            )
            
            # Extrair e retornar a resposta
            result = response.choices[0].message.content
            return json.loads(result)
            
        except Exception as e:
            logging.error(f"Erro ao classificar post: {e}")
            return self._mock_classify_post(post_title, post_text)
    
    def classify_posts_dataframe(self, df):
        """
        Classifica todos os posts em um DataFrame.
        
        Args:
            df (pandas.DataFrame): DataFrame com posts do Reddit.
            
        Returns:
            pandas.DataFrame: DataFrame original com colunas de classificação adicionadas.
        """
        if df.empty:
            return df
        
        # Criar cópias das colunas de classificação
        df['categoria'] = None
        df['sentimento'] = None
        df['tópicos'] = None
        df['insights'] = None
        
        # Classificar cada post
        for i, row in df.iterrows():
            title = row['title']
            text = row['selftext']
            
            classification = self.classify_post(title, text)
            
            df.at[i, 'categoria'] = classification.get('categoria', '')
            df.at[i, 'sentimento'] = classification.get('sentimento', '')
            df.at[i, 'tópicos'] = ', '.join(classification.get('tópicos', []))
            df.at[i, 'insights'] = '; '.join(classification.get('insights', []))
        
        return df


# Exemplo de uso
if __name__ == "__main__":
    classifier = OpenAIClassifier()
    
    # Exemplo de post
    title = "Dúvida sobre Python: como resolver este problema?"
    text = "Estou trabalhando com Python há algumas semanas e encontrei um problema que não consigo resolver. Alguém pode me ajudar?"
    
    classification = classifier.classify_post(title, text)
    print(json.dumps(classification, indent=2, ensure_ascii=False))
