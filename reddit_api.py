"""
Módulo para buscar posts no Reddit usando PRAW ou dados simulados.
"""
import pandas as pd
from datetime import datetime, timedelta
import random
import time
import json
import os

class RedditAPI:
    """Classe para interagir com o Reddit ou fornecer dados simulados."""
    
    def __init__(self, use_mock_data=True):
        """
        Inicializa a classe RedditAPI.
        
        Args:
            use_mock_data (bool): Se True, usa dados simulados em vez de API real.
        """
        self.use_mock_data = use_mock_data
        self.last_request_time = 0
        self.request_delay = 1  # Delay em segundos para evitar rate limiting
        
        # Criar diretório de dados se não existir
        os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
        
        # Gerar dados simulados se não existirem
        self._ensure_mock_data()
    
    def _respect_rate_limit(self):
        """Respeita o rate limit da API."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.request_delay:
            time.sleep(self.request_delay - time_since_last_request)
        
        self.last_request_time = time.time()
    
    def _ensure_mock_data(self):
        """Garante que os dados simulados existam."""
        mock_data_path = os.path.join(os.path.dirname(__file__), 'data', 'mock_reddit_data.json')
        
        if not os.path.exists(mock_data_path):
            # Gerar dados simulados
            mock_data = self._generate_mock_data()
            
            # Salvar dados simulados
            with open(mock_data_path, 'w', encoding='utf-8') as f:
                json.dump(mock_data, f, indent=2)
    
    def _generate_mock_data(self):
        """
        Gera dados simulados do Reddit.
        
        Returns:
            dict: Dicionário com dados simulados.
        """
        # Tópicos comuns para simular pesquisas
        topics = [
            "python", "javascript", "programming", "webdev", "machinelearning",
            "datascience", "ai", "productivity", "business", "startup",
            "marketing", "seo", "socialmedia", "design", "ux", "ui",
            "mobile", "android", "ios", "gaming", "technology", "crypto",
            "finance", "investing", "personalfinance", "career", "jobs"
        ]
        
        # Subreddits populares
        subreddits = [
            "programming", "learnprogramming", "python", "javascript", "webdev",
            "datascience", "machinelearning", "artificial", "productivity",
            "technology", "futurology", "startups", "entrepreneur", "business",
            "marketing", "seo", "socialmedia", "web_design", "userexperience",
            "androiddev", "iOSProgramming", "gamedev", "cscareerquestions",
            "personalfinance", "investing", "cryptocurrency", "wallstreetbets"
        ]
        
        # Autores simulados
        authors = [
            "tech_enthusiast", "code_master", "data_wizard", "web_guru",
            "ai_researcher", "startup_founder", "marketing_pro", "design_ninja",
            "mobile_dev", "game_creator", "crypto_expert", "finance_advisor",
            "career_coach", "productivity_hacker", "future_thinker"
        ]
        
        # Títulos e textos simulados para cada tópico
        mock_data = {}
        
        for topic in topics:
            posts = []
            
            # Gerar entre 30 e 50 posts para cada tópico
            num_posts = random.randint(30, 50)
            
            for i in range(num_posts):
                # Data aleatória nos últimos 90 dias
                days_ago = random.randint(0, 90)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                created_date = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
                created_utc = int(created_date.timestamp())
                
                # Escolher subreddit aleatório
                subreddit = random.choice(subreddits)
                
                # Escolher autor aleatório
                author = random.choice(authors)
                
                # Gerar título baseado no tópico
                title_templates = [
                    f"Dúvida sobre {topic}: como resolver este problema?",
                    f"Preciso de ajuda com {topic} para um projeto",
                    f"Alguém tem experiência com {topic}?",
                    f"Melhor maneira de aprender {topic} em 2025?",
                    f"Recursos recomendados para {topic}",
                    f"Como {topic} mudou minha carreira/vida",
                    f"Problemas comuns com {topic} e como resolvê-los",
                    f"Novidades em {topic} que você precisa conhecer",
                    f"Por que {topic} é importante para o futuro?",
                    f"Comparando diferentes abordagens para {topic}"
                ]
                title = random.choice(title_templates)
                
                # Gerar texto baseado no título
                selftext_templates = [
                    f"Estou trabalhando com {topic} há algumas semanas e encontrei um problema que não consigo resolver. Alguém pode me ajudar?",
                    f"Sou iniciante em {topic} e gostaria de saber por onde começar. Quais recursos vocês recomendam?",
                    f"Tenho um projeto que envolve {topic} e preciso de conselhos sobre as melhores práticas.",
                    f"Quais são as tendências atuais em {topic}? O que devo aprender para me manter atualizado?",
                    f"Compartilhando minha experiência com {topic} após 6 meses de estudo e prática. Aqui estão as lições que aprendi...",
                    f"Estou comparando diferentes ferramentas/frameworks para {topic}. Quais vocês recomendam e por quê?",
                    f"Como {topic} está evoluindo em 2025? Quais são as previsões para o futuro desta tecnologia/área?",
                    f"Quais habilidades complementares devo aprender junto com {topic} para aumentar minhas chances no mercado?",
                    f"Estou enfrentando um desafio específico com {topic}: [descrição detalhada do problema]. Alguma sugestão?",
                    f"Criei um projeto usando {topic} e gostaria de compartilhar com a comunidade. Feedback é bem-vindo!"
                ]
                selftext = random.choice(selftext_templates)
                
                # Adicionar mais conteúdo ao texto para torná-lo mais realista
                additional_content = [
                    f"\n\nJá tentei várias abordagens, incluindo [detalhes técnicos relacionados a {topic}], mas ainda estou tendo dificuldades.",
                    f"\n\nMeu background: tenho experiência com [tecnologias relacionadas], mas {topic} é novo para mim.",
                    f"\n\nO que já tentei: [lista de tentativas]. Nenhuma funcionou completamente.",
                    f"\n\nObjetivo final: [descrição do projeto ou meta relacionada a {topic}].",
                    f"\n\nAgradeceria muito qualquer ajuda ou direcionamento da comunidade!",
                    f"\n\nEdit: Obrigado pelas respostas até agora! Estou tentando implementar as sugestões.",
                    f"\n\nUpdate: Consegui resolver parte do problema usando [solução parcial].",
                    f"\n\nPS: Se alguém tiver recursos adicionais sobre {topic}, por favor compartilhe."
                ]
                
                # Adicionar conteúdo extra em 70% dos posts para variar o tamanho
                if random.random() < 0.7:
                    selftext += random.choice(additional_content)
                
                # Gerar estatísticas aleatórias
                score = random.randint(-5, 500)  # Alguns posts podem ter score negativo
                num_comments = random.randint(0, 50)
                is_self = random.random() < 0.8  # 80% são self posts
                
                # Gerar ID aleatório
                post_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
                
                # Criar URL
                full_link = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}/{title.lower().replace(' ', '_')[:50]}/"
                
                # Criar post
                post = {
                    'id': post_id,
                    'title': title,
                    'selftext': selftext,
                    'author': author,
                    'subreddit': subreddit,
                    'score': score,
                    'num_comments': num_comments,
                    'created_utc': created_utc,
                    'full_link': full_link,
                    'is_self': is_self
                }
                
                posts.append(post)
            
            # Ordenar posts por data (mais recentes primeiro)
            posts.sort(key=lambda x: x['created_utc'], reverse=True)
            
            mock_data[topic] = posts
        
        return mock_data
    
    def _load_mock_data(self):
        """
        Carrega dados simulados do arquivo.
        
        Returns:
            dict: Dicionário com dados simulados.
        """
        mock_data_path = os.path.join(os.path.dirname(__file__), 'data', 'mock_reddit_data.json')
        
        with open(mock_data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _search_mock_data(self, query, subreddit=None, limit=25):
        """
        Busca em dados simulados.
        
        Args:
            query (str): Termo de busca.
            subreddit (str, optional): Subreddit específico para buscar.
            limit (int, optional): Número máximo de resultados.
            
        Returns:
            list: Lista de posts encontrados.
        """
        mock_data = self._load_mock_data()
        
        # Verificar se o termo de busca existe diretamente
        if query.lower() in mock_data:
            results = mock_data[query.lower()]
        else:
            # Buscar em todos os tópicos
            results = []
            for topic, posts in mock_data.items():
                # Verificar se o termo de busca está no tópico
                if query.lower() in topic:
                    results.extend(posts)
                    continue
                
                # Buscar nos títulos e textos
                for post in posts:
                    if (query.lower() in post['title'].lower() or 
                        query.lower() in post['selftext'].lower()):
                        results.append(post)
        
        # Filtrar por subreddit se especificado
        if subreddit:
            results = [post for post in results if post['subreddit'].lower() == subreddit.lower()]
        
        # Ordenar por data (mais recentes primeiro)
        results.sort(key=lambda x: x['created_utc'], reverse=True)
        
        # Limitar resultados
        return results[:limit]
    
    def search_posts(self, query, subreddit=None, limit=25, sort='desc', sort_type='created_utc'):
        """
        Busca posts no Reddit.
        
        Args:
            query (str): Termo de busca.
            subreddit (str, optional): Subreddit específico para buscar. Default é None (busca em todos).
            limit (int, optional): Número máximo de resultados. Default é 25.
            sort (str, optional): Direção da ordenação ('asc' ou 'desc'). Default é 'desc'.
            sort_type (str, optional): Campo para ordenação. Default é 'created_utc'.
            
        Returns:
            list: Lista de posts encontrados.
        """
        self._respect_rate_limit()
        
        if self.use_mock_data:
            return self._search_mock_data(query, subreddit, limit)
        else:
            # Aqui seria implementada a integração com PRAW
            # Como estamos usando dados simulados, retornamos uma lista vazia
            print("Integração com PRAW não implementada. Usando dados simulados.")
            return self._search_mock_data(query, subreddit, limit)
    
    def format_posts(self, posts):
        """
        Formata os posts para um DataFrame pandas.
        
        Args:
            posts (list): Lista de posts retornados pela API.
            
        Returns:
            pandas.DataFrame: DataFrame com os posts formatados.
        """
        if not posts:
            return pd.DataFrame()
        
        formatted_posts = []
        for post in posts:
            # Converter timestamp para data legível
            created_utc = post.get('created_utc', 0)
            created_date = datetime.fromtimestamp(created_utc).strftime('%Y-%m-%d %H:%M:%S')
            
            formatted_post = {
                'id': post.get('id', ''),
                'title': post.get('title', ''),
                'selftext': post.get('selftext', '')[:500] + ('...' if len(post.get('selftext', '')) > 500 else ''),
                'author': post.get('author', ''),
                'subreddit': post.get('subreddit', ''),
                'score': post.get('score', 0),
                'num_comments': post.get('num_comments', 0),
                'created_date': created_date,
                'url': post.get('full_link', ''),
                'is_self': post.get('is_self', True)
            }
            formatted_posts.append(formatted_post)
        
        return pd.DataFrame(formatted_posts)
    
    def search_and_format(self, query, subreddit=None, limit=25):
        """
        Busca e formata posts em uma única função.
        
        Args:
            query (str): Termo de busca.
            subreddit (str, optional): Subreddit específico para buscar. Default é None.
            limit (int, optional): Número máximo de resultados. Default é 25.
            
        Returns:
            pandas.DataFrame: DataFrame com os posts formatados.
        """
        posts = self.search_posts(query, subreddit, limit)
        return self.format_posts(posts)


# Exemplo de uso
if __name__ == "__main__":
    reddit_api = RedditAPI(use_mock_data=True)
    posts = reddit_api.search_and_format("python programming", limit=5)
    print(posts)
