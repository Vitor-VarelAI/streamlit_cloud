"""
Módulo para buscar posts no Reddit usando PRAW.
"""
import pandas as pd
from datetime import datetime
import time
import os
import praw
import streamlit as st

class RedditAPI:
    """Classe para interagir com o Reddit via PRAW."""
    
    def __init__(self):
        """
        Inicializa a classe RedditAPI. Requer credenciais via Streamlit secrets.
        Levanta exceção se a inicialização do PRAW falhar.
        """
        print("RedditAPI Init - Attempting PRAW initialization")
        self.last_request_time = 0
        self.request_delay = 1  # Delay para API real
        self.reddit = None
        
        try:
            # Obter segredos do Streamlit
            reddit_secrets = st.secrets.get("reddit", {})
            client_id = reddit_secrets.get("client_id")
            client_secret = reddit_secrets.get("client_secret")
            user_agent = reddit_secrets.get("user_agent")
            username = reddit_secrets.get("username") # Opcional
            password = reddit_secrets.get("password") # Opcional
            
            print(f"RedditAPI - Found secrets: client_id={'✓' if client_id else '✗'}, client_secret={'✓' if client_secret else '✗'}, user_agent={'✓' if user_agent else '✗'}")
            
            if not (client_id and client_secret and user_agent):
                raise ValueError("Erro: Credenciais essenciais do Reddit (client_id, client_secret, user_agent) não encontradas nos segredos do Streamlit.")
                
            print("RedditAPI - Initializing PRAW...")
            praw_config = {
                'client_id': client_id,
                'client_secret': client_secret,
                'user_agent': user_agent,
            }
            
            if username and password and password != "TUA_PASSWORD_AQUI":
                print("RedditAPI - Using authenticated mode")
                praw_config['username'] = username
                praw_config['password'] = password
            else:
                print("RedditAPI - Using read-only mode")
                praw_config['read_only'] = True
                
            self.reddit = praw.Reddit(**praw_config)
            # Testar conexão
            test_subreddit = self.reddit.subreddit("all")
            next(test_subreddit.new(limit=1), None)
            print("Cliente PRAW inicializado e testado com sucesso!")
            
        except Exception as e:
            print(f"FATAL: Erro ao inicializar PRAW com Streamlit secrets: {e}")
            # Levantar a exceção para impedir a instanciação da classe se PRAW falhar
            raise ConnectionError(f"Falha ao conectar à API do Reddit: {e}") from e
            
    def _respect_rate_limit(self):
        """Respeita o rate limit da API."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.request_delay:
            time.sleep(self.request_delay - time_since_last_request)
        self.last_request_time = time.time()
    
    def search_posts(self, query, subreddit=None, limit=25, sort='new'): # Simplificado sort default
        """
        Busca posts no Reddit usando PRAW.
        Retorna lista vazia em caso de erro na busca.
        """
        self._respect_rate_limit()
        print(f"RedditAPI search_posts - Query: '{query}', Subreddit: {subreddit or 'all'}")
        
        if not self.reddit:
            print("RedditAPI - Error: PRAW client not initialized.")
            return [] # Retorna lista vazia se PRAW não foi inicializado
            
        print(f"RedditAPI - Searching real Reddit posts for: '{query}' (Subreddit: {subreddit or 'all'}, Limit: {limit})")
        try:
            results = []
            praw_search_params = {
                'query': query,
                'limit': limit,
                'sort': sort
                # 'time_filter': "month" # Mantendo comentado por enquanto
            }
            print(f"RedditAPI - PRAW search params: {praw_search_params}")
            
            if subreddit:
                print(f"RedditAPI - Searching in specific subreddit: r/{subreddit}")
                target_subreddit = self.reddit.subreddit(subreddit)
                search_results = target_subreddit.search(**praw_search_params)
            else:
                print("RedditAPI - Searching in r/all")
                target_subreddit = self.reddit.subreddit("all")
                search_results = target_subreddit.search(**praw_search_params)
                
            print("RedditAPI - PRAW search executed. Processing results...")
            count = 0
            for submission in search_results:
                count += 1
                post_data = {
                    'id': submission.id,
                    'title': submission.title,
                    'selftext': submission.selftext,
                    'author': submission.author.name if submission.author else "[deleted]",
                    'subreddit': submission.subreddit.display_name,
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'created_utc': submission.created_utc,
                    'full_link': submission.permalink,
                    'is_self': submission.is_self
                }
                results.append(post_data)
            
            print(f"RedditAPI - Found {count} posts via PRAW before formatting.")
            return results
            
        except Exception as e:
            print(f"Erro durante a busca no Reddit com PRAW: {e}. Retornando lista vazia.")
            return [] # Retorna lista vazia em caso de erro na busca

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
                # Usar o permalink diretamente, prefixado com reddit.com
                'url': f"https://www.reddit.com{post.get('full_link', '')}" if not post.get('full_link', '').startswith('http') else post.get('full_link', ''),
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
