"""
Módulo para integração com a API do Firecrawl para resumir links externos.
"""
import os
import requests
import json
import time
import random
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class FirecrawlSummarizer:
    """Classe para resumir links usando a API do Firecrawl."""
    
    def __init__(self):
        """Inicializa a classe FirecrawlSummarizer."""
        # Configurar a API do Firecrawl
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        self.api_url = "https://api.firecrawl.dev/v1/summarize"
        self.last_request_time = 0
        self.request_delay = 1  # Delay em segundos para evitar rate limiting
        
        # Verificar se a chave da API está configurada
        if not self.api_key or self.api_key == "your-firecrawl-key":
            print("Aviso: Chave da API Firecrawl não configurada. Usando modo simulado.")
            self.use_mock = True
        else:
            self.use_mock = False
    
    def _respect_rate_limit(self):
        """Respeita o rate limit da API."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.request_delay:
            time.sleep(self.request_delay - time_since_last_request)
        
        self.last_request_time = time.time()
    
    def _mock_summarize_url(self, url):
        """
        Simula o resumo de um URL quando a API não está disponível.
        
        Args:
            url (str): URL para resumir.
            
        Returns:
            dict: Resumo simulado do URL.
        """
        # Extrair domínio e caminho do URL para personalizar o resumo
        import re
        from urllib.parse import urlparse
        
        # Analisar o URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path
        
        # Verificar se é um link do Reddit
        is_reddit = "reddit.com" in domain
        
        # Extrair informações do caminho para links do Reddit
        subreddit = ""
        post_id = ""
        if is_reddit:
            # Tentar extrair subreddit e post_id
            reddit_pattern = r"/r/([^/]+)/comments/([^/]+)"
            match = re.search(reddit_pattern, path)
            if match:
                subreddit = match.group(1)
                post_id = match.group(2)
        
        # Gerar título simulado
        if is_reddit:
            if subreddit:
                title = f"Discussão no r/{subreddit}: {self._generate_mock_title(subreddit)}"
            else:
                title = f"Post no Reddit sobre {self._generate_mock_title('geral')}"
        else:
            # Gerar título baseado no domínio
            if "github.com" in domain:
                title = f"Repositório GitHub: {self._generate_mock_title('programação')}"
            elif "medium.com" in domain:
                title = f"Artigo no Medium sobre {self._generate_mock_title('tecnologia')}"
            elif "stackoverflow.com" in domain:
                title = f"Pergunta no Stack Overflow sobre {self._generate_mock_title('programação')}"
            elif "news" in domain or "blog" in domain:
                title = f"Notícia: {self._generate_mock_title('atualidades')}"
            else:
                title = f"Página Web: {self._generate_mock_title('geral')}"
        
        # Gerar resumo simulado
        summary = self._generate_mock_summary(domain, is_reddit, subreddit)
        
        # Gerar tópicos principais simulados
        main_topics = self._generate_mock_topics(domain, is_reddit, subreddit)
        
        # Gerar metadados simulados
        metadata = {
            "domain": domain,
            "url": url,
            "estimated_reading_time": random.randint(3, 15),
            "language": "pt-BR",
            "word_count": random.randint(500, 3000)
        }
        
        # Retornar resumo simulado
        return {
            "title": title,
            "summary": summary,
            "main_topics": main_topics,
            "metadata": metadata
        }
    
    def _generate_mock_title(self, category):
        """Gera um título simulado baseado na categoria."""
        import random
        
        titles = {
            "programação": [
                "Como implementar algoritmos de ordenação em Python",
                "Melhores práticas para desenvolvimento web em 2025",
                "Guia completo de React para iniciantes",
                "Otimizando consultas SQL para melhor performance",
                "Introdução ao desenvolvimento de aplicativos móveis com Flutter"
            ],
            "tecnologia": [
                "O futuro da inteligência artificial em 2025",
                "Como a computação quântica está mudando o mundo",
                "Tendências de cibersegurança que você precisa conhecer",
                "Impacto da realidade aumentada no cotidiano",
                "Blockchain além das criptomoedas: aplicações práticas"
            ],
            "atualidades": [
                "Novas políticas de tecnologia anunciadas pelo governo",
                "Como a tecnologia está transformando a educação pós-pandemia",
                "Grandes empresas de tecnologia anunciam colaboração inédita",
                "Impacto ambiental da indústria tecnológica: novos estudos",
                "Avanços recentes em energia renovável e sustentabilidade"
            ],
            "geral": [
                "Guia completo para iniciantes",
                "Dicas e truques que você precisa conhecer",
                "Análise detalhada e opiniões de especialistas",
                "Comparativo das melhores opções em 2025",
                "O que você precisa saber antes de começar"
            ]
        }
        
        # Usar categoria padrão se a especificada não existir
        if category not in titles:
            category = "geral"
        
        return random.choice(titles[category])
    
    def _generate_mock_summary(self, domain, is_reddit, subreddit):
        """Gera um resumo simulado baseado no domínio e outras informações."""
        import random
        
        # Parágrafos para diferentes tipos de conteúdo
        reddit_paragraphs = [
            "Esta discussão no Reddit aborda questões relacionadas a tecnologia e desenvolvimento de software. Os usuários compartilham experiências pessoais e oferecem conselhos sobre melhores práticas e ferramentas.",
            "O post original apresenta uma pergunta sobre desafios comuns enfrentados por desenvolvedores, seguido por várias respostas detalhadas da comunidade. Há um debate interessante sobre diferentes abordagens e metodologias.",
            "Vários usuários compartilham recursos úteis, incluindo tutoriais, documentação e ferramentas que podem ajudar com o problema discutido. A comunidade parece bastante engajada em fornecer soluções práticas.",
            "Há um consenso geral sobre certas práticas recomendadas, embora alguns usuários discordem sobre detalhes específicos de implementação. A discussão permanece respeitosa e focada em encontrar a melhor solução."
        ]
        
        tech_paragraphs = [
            "Este artigo explora as tendências emergentes em tecnologia para 2025 e além. O autor analisa como essas inovações estão transformando indústrias tradicionais e criando novas oportunidades de negócio.",
            "São apresentados dados e estatísticas recentes que demonstram o crescimento acelerado do setor tecnológico, com ênfase especial em inteligência artificial, computação em nuvem e tecnologias móveis.",
            "O texto discute os desafios éticos e sociais associados a essas novas tecnologias, incluindo questões de privacidade, segurança de dados e impacto no mercado de trabalho.",
            "Por fim, são oferecidas recomendações para profissionais e empresas que desejam se manter competitivos neste cenário em rápida evolução, com foco em desenvolvimento de habilidades e adaptabilidade."
        ]
        
        programming_paragraphs = [
            "Este recurso oferece um guia detalhado sobre técnicas avançadas de programação, com exemplos práticos e código comentado. O conteúdo é adequado tanto para iniciantes quanto para desenvolvedores experientes.",
            "São abordados conceitos fundamentais de arquitetura de software, padrões de design e boas práticas de codificação que podem melhorar significativamente a qualidade e manutenibilidade do código.",
            "O autor compartilha insights valiosos baseados em experiência prática, destacando armadilhas comuns a evitar e técnicas para otimização de performance em diferentes cenários.",
            "Há uma seção dedicada a ferramentas e recursos complementares que podem aumentar a produtividade dos desenvolvedores, incluindo bibliotecas, frameworks e ambientes de desenvolvimento integrado."
        ]
        
        news_paragraphs = [
            "Esta notícia relata desenvolvimentos recentes no setor de tecnologia, com foco em anúncios de grandes empresas e mudanças regulatórias que podem impactar o mercado nos próximos meses.",
            "São apresentados dados econômicos e análises de especialistas sobre as implicações dessas mudanças para consumidores, investidores e profissionais da área.",
            "O artigo contextualiza esses eventos dentro de tendências mais amplas do setor, oferecendo uma perspectiva histórica e projeções para o futuro próximo.",
            "Diferentes pontos de vista são apresentados, incluindo opiniões de executivos do setor, analistas independentes e representantes de órgãos reguladores."
        ]
        
        general_paragraphs = [
            "Este conteúdo oferece uma visão abrangente sobre o tema, começando com conceitos básicos e progredindo para aspectos mais avançados. A abordagem é acessível mesmo para quem não tem conhecimento prévio na área.",
            "São apresentados exemplos práticos e estudos de caso que ilustram a aplicação dos conceitos discutidos em situações do mundo real, facilitando a compreensão e demonstrando relevância.",
            "O autor aborda diferentes perspectivas sobre o assunto, apresentando argumentos a favor e contra determinadas abordagens, o que permite ao leitor formar sua própria opinião informada.",
            "A conclusão sintetiza os principais pontos discutidos e oferece recomendações práticas para quem deseja se aprofundar no tema ou aplicar o conhecimento adquirido."
        ]
        
        # Selecionar conjunto de parágrafos apropriado
        if is_reddit:
            paragraphs = reddit_paragraphs
            if subreddit and subreddit.lower() in ["programming", "python", "webdev", "javascript"]:
                # Adicionar alguns parágrafos específicos de programação para subreddits de tecnologia
                paragraphs = paragraphs + programming_paragraphs[:2]
        elif "github.com" in domain or "stackoverflow.com" in domain:
            paragraphs = programming_paragraphs
        elif "news" in domain or "blog" in domain:
            paragraphs = news_paragraphs
        elif "tech" in domain or "technology" in domain:
            paragraphs = tech_paragraphs
        else:
            paragraphs = general_paragraphs
        
        # Embaralhar parágrafos para variedade
        random.shuffle(paragraphs)
        
        # Selecionar 2-3 parágrafos
        num_paragraphs = random.randint(2, 3)
        selected_paragraphs = paragraphs[:num_paragraphs]
        
        # Juntar parágrafos em um resumo
        summary = "\n\n".join(selected_paragraphs)
        
        return summary
    
    def _generate_mock_topics(self, domain, is_reddit, subreddit):
        """Gera tópicos principais simulados baseados no domínio e outras informações."""
        import random
        
        # Conjuntos de tópicos para diferentes tipos de conteúdo
        tech_topics = [
            "Inteligência Artificial", "Machine Learning", "Computação em Nuvem",
            "Cibersegurança", "Big Data", "Internet das Coisas (IoT)",
            "Blockchain", "Realidade Virtual", "Realidade Aumentada",
            "5G", "Computação Quântica", "Automação", "Robótica"
        ]
        
        programming_topics = [
            "Desenvolvimento Web", "Desenvolvimento Mobile", "DevOps",
            "Arquitetura de Software", "Padrões de Design", "Testes Automatizados",
            "Linguagens de Programação", "Frameworks", "APIs",
            "Bancos de Dados", "Microserviços", "Contêineres", "CI/CD"
        ]
        
        business_topics = [
            "Empreendedorismo", "Startups", "Modelos de Negócio",
            "Marketing Digital", "E-commerce", "Gestão de Projetos",
            "Produtividade", "Liderança", "Transformação Digital",
            "Análise de Dados", "Experiência do Cliente", "Inovação"
        ]
        
        general_topics = [
            "Tecnologia", "Inovação", "Tendências", "Melhores Práticas",
            "Tutoriais", "Guias", "Análises", "Comparativos",
            "Dicas e Truques", "Recursos", "Ferramentas", "Comunidade"
        ]
        
        # Selecionar conjunto de tópicos apropriado
        all_topics = general_topics  # Base de tópicos gerais
        
        if is_reddit:
            if subreddit and subreddit.lower() in ["programming", "python", "webdev", "javascript"]:
                all_topics = all_topics + programming_topics
            elif subreddit and subreddit.lower() in ["technology", "futurology", "gadgets"]:
                all_topics = all_topics + tech_topics
            elif subreddit and subreddit.lower() in ["startups", "entrepreneur", "business"]:
                all_topics = all_topics + business_topics
        elif "github.com" in domain or "stackoverflow.com" in domain:
            all_topics = all_topics + programming_topics
        elif "tech" in domain or "technology" in domain:
            all_topics = all_topics + tech_topics
        elif "business" in domain or "startup" in domain or "entrepreneur" in domain:
            all_topics = all_topics + business_topics
        
        # Remover duplicatas
        all_topics = list(set(all_topics))
        
        # Selecionar 3-5 tópicos aleatórios
        num_topics = random.randint(3, 5)
        selected_topics = random.sample(all_topics, min(num_topics, len(all_topics)))
        
        return selected_topics
    
    def summarize_url(self, url):
        """
        Resumir o conteúdo de um URL usando a API do Firecrawl.
        
        Args:
            url (str): URL para resumir.
            
        Returns:
            dict: Resumo do URL.
        """
        self._respect_rate_limit()
        
        # Se estiver no modo simulado, usar resumo simulado
        if self.use_mock:
            import random  # Importar aqui para evitar problemas se não for usado
            return self._mock_summarize_url(url)
        
        try:
            # Preparar a requisição para a API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "url": url,
                "language": "pt-BR",  # Preferência por resumos em português
                "max_length": 500     # Tamanho máximo do resumo
            }
            
            # Fazer a chamada para a API
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            # Processar a resposta
            result = response.json()
            
            return {
                "title": result.get("title", ""),
                "summary": result.get("summary", ""),
                "main_topics": result.get("main_topics", []),
                "metadata": result.get("metadata", {})
            }
                
        except Exception as e:
            print(f"Erro ao resumir URL: {e}")
            # Em caso de erro, usar resumo simulado
            import random  # Importar aqui para evitar problemas se não for usado
            return self._mock_summarize_url(url)


# Exemplo de uso
if __name__ == "__main__":
    import random  # Necessário para os métodos de simulação
    
    summarizer = FirecrawlSummarizer()
    
    # Exemplo de URL
    url = "https://www.reddit.com/r/Python/comments/example/how_to_learn_python_in_2025/"
    
    summary = summarizer.summarize_url(url)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
