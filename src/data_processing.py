import spacy
import pandas as pd
from spacy import displacy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from textblob import TextBlob

class EntrevistaProcessor:
    def __init__(self):
        """Inicialização robusta com verificação de modelo e extensões"""
        try:
            self.nlp = spacy.load("pt_core_news_lg")  # Modelo maior para melhor precisão
            self._setup_custom_pipeline()
            self._valid = True
        except OSError:
            self._valid = False
            raise ImportError("Modelo de linguagem pt_core_news_lg não encontrado. Execute: python -m spacy download pt_core_news_lg")
    
    def _setup_custom_pipeline(self):
        """Configura pipeline personalizado para análise educacional"""
        # Adiciona componentes personalizados se necessário
        if not self.nlp.has_pipe('sentencizer'):
            self.nlp.add_pipe('sentencizer')
    
    def processar_entrevista(self, row):
        """Processamento completo de uma entrevista com múltiplas análises"""
        if not self._valid:
            return self._retorno_padrao(row.name)
        
        try:
            texto = str(row.get('texto', ''))
            if not texto.strip():
                return self._retorno_padrao(row.name)
            
            doc = self.nlp(texto)
            
            # Análises diversas
            temas = self._extrair_temas(doc)
            sentimento = self._analisar_sentimento_avancado(texto)
            entidades = self._extrair_entidades(doc)
            polaridade, subjetividade = self._analise_sentimento_textblob(texto)
            frases_chave = self._extrair_frases_relevantes(doc)
            
            return pd.Series({
                'temas': temas,
                'sentimento': sentimento,
                'entidades': entidades,
                'polaridade': polaridade,
                'subjetividade': subjetividade,
                'frases_chave': frases_chave,
                'tokens_limpos': ' '.join([token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct])
            }, name=row.name)
            
        except Exception as e:
            print(f"Erro ao processar linha {row.name}: {str(e)}")
            return self._retorno_padrao(row.name)
    
    def _retorno_padrao(self, name):
        """Retorna um Series padrão para casos de erro"""
        return pd.Series({
            'temas': [],
            'sentimento': 'Neutro',
            'entidades': [],
            'polaridade': 0,
            'subjetividade': 0,
            'frases_chave': [],
            'tokens_limpos': ''
        }, name=name)
    
    def _extrair_temas(self, doc):
        """Extrai temas limpos do documento com filtros específicos para educação"""
        temas_especificos = ['curso', 'professor', 'disciplina', 'faculdade', 'ensino', 
                           'aprendizado', 'dificuldade', 'evasão', 'permanência']
        
        return [token.lemma_.lower() for token in doc 
               if not token.is_stop 
               and not token.is_punct 
               and len(token.lemma_) > 2
               and token.lemma_.lower() in temas_especificos]
    
    def _extrair_entidades(self, doc):
        """Extrai entidades nomeadas com filtros para contexto educacional"""
        entidades_relevantes = ['ORG', 'LOC', 'PRODUCT']
        return [(ent.text, ent.label_) for ent in doc.ents 
                if ent.label_ in entidades_relevantes]
    
    def _analisar_sentimento_avancado(self, texto):
        """Análise de sentimento com vocabulário específico para educação"""
        palavras_pos = [
            'bom', 'ótimo', 'excelente', 'gostei', 'facilidade', 'aprendi',
            'ajudou', 'apoiou', 'consegui', 'evolui', 'melhor', 'recomendo'
        ]
        
        palavras_neg = [
            'ruim', 'difícil', 'problema', 'falta', 'abandonei', 'tranquei',
            'desisti', 'pior', 'decepcionado', 'insatisfeito', 'dificuldade',
            'precário', 'deficiente', 'carência'
        ]
        
        texto = texto.lower()
        pos = sum(1 for palavra in palavras_pos if palavra in texto)
        neg = sum(1 for palavra in palavras_neg if palavra in texto)
        
        if pos > neg * 1.5:  # Limiar mais alto para positivo
            return 'Positivo'
        elif neg > pos * 1.5:  # Limiar mais alto para negativo
            return 'Negativo'
        else:
            return 'Neutro'
    
    def _analise_sentimento_textblob(self, texto):
        """Análise de sentimento usando TextBlob para polaridade contínua"""
        analysis = TextBlob(texto)
        return analysis.sentiment.polarity, analysis.sentiment.subjectivity
    
    def _extrair_frases_relevantes(self, doc, n=3):
        """Extrai frases mais relevantes baseadas em critérios de educação"""
        # Implementação simplificada - pode ser melhorada
        frases = [sent.text for sent in doc.sents]
        return frases[:n] if len(frases) > n else frases
    
    def identificar_topicos(self, textos, n_topics=5):
        """Identifica tópicos principais usando LDA"""
        vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='portuguese')
        dtm = vectorizer.fit_transform(textos)
        
        lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
        lda.fit(dtm)
        
        topicos = []
        for idx, topic in enumerate(lda.components_):
            top_features = [vectorizer.get_feature_names_out()[i] for i in topic.argsort()[-10:]]
            topicos.append(f"Tópico {idx}: {' '.join(top_features)}")
        
        return topicos
