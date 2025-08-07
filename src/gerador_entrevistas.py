import pandas as pd
import numpy as np
from faker import Faker
from collections import defaultdict
import random

# Configuração inicial
fake = Faker('pt_BR')
np.random.seed(42)

class GeradorEntrevistas:
    def __init__(self, n_entrevistas=200):
        self.n_entrevistas = n_entrevistas
        self.regioes = {
            'Curitiba': {'evasao': 0.22, 'cursos': ['Ciência da Computação', 'Engenharia de Software']},
            'Londrina': {'evasao': 0.28, 'cursos': ['Sistemas de Informação', 'Ciência da Computação']},
            'Maringá': {'evasao': 0.25, 'cursos': ['Engenharia de Software', 'Tecnologia em TI']},
            'Apucarana': {'evasao': 0.35, 'cursos': ['Ciência da Computação', 'Sistemas de Informação']},
            'Ponta Grossa': {'evasao': 0.30, 'cursos': ['Engenharia de Software', 'Tecnologia em TI']},
            'Cascavel': {'evasao': 0.40, 'cursos': ['Sistemas de Informação', 'Ciência da Computação']}
        }
        
        self.motivos_evasao = {
            'financeiro': ['dificuldade financeira', 'precisava trabalhar', 'não consegui pagar as mensalidades'],
            'acadêmico': ['dificuldade nas matérias', 'não era o que esperava', 'falta de base matemática'],
            'pessoal': ['problemas de saúde', 'mudança de cidade', 'falta de tempo'],
            'institucional': ['infraestrutura ruim', 'professores despreparados', 'falta de apoio']
        }
        
        self.fatores_permanencia = {
            'apoio': ['bolsa de estudos', 'apoio da família', 'mentoria dos professores'],
            'vocação': ['gosto pela área', 'perspectivas de carreira', 'identificação com o curso'],
            'social': ['amizades no curso', 'ambiente acolhedor', 'grupo de estudos']
        }

    def _gerar_texto_evasao(self, motivo_principal):
        """Gera texto realista para alunos evadidos"""
        motivo = random.choice(self.motivos_evasao[motivo_principal])
        
        estruturas = [
            f"Tive que trancar o curso porque {motivo}. {self._complemento_evasao(motivo_principal)}",
            f"Decidi sair pois {motivo}. {self._complemento_evasao(motivo_principal)}",
            f"O principal motivo foi {motivo}. {self._complemento_evasao(motivo_principal)}",
            f"Não consegui continuar devido a {motivo}. {self._complemento_evasao(motivo_principal)}"
        ]
        
        return random.choice(estruturas)

    def _complemento_evasao(self, motivo):
        """Adiciona detalhes ao motivo de evasão"""
        complementos = {
            'financeiro': [
                "Mesmo tentando conciliar trabalho e estudos, não foi possível.",
                "As despesas com transporte e materiais pesaram no orçamento."
            ],
            'acadêmico': [
                "As disciplinas de programação foram especialmente desafiadoras.",
                "Não recebi o suporte necessário para acompanhar o ritmo."
            ],
            'pessoal': [
                "Precisei priorizar outras responsabilidades pessoais.",
                "A rotina ficou incompatível com meu horário de trabalho."
            ],
            'institucional': [
                "A infraestrutura do laboratório era precária.",
                "Faltavam professores especializados em áreas importantes."
            ]
        }
        return random.choice(complementos[motivo])

    def _gerar_texto_permanencia(self, fator_principal):
        """Gera texto realista para alunos que permaneceram"""
        fator = random.choice(self.fatores_permanencia[fator_principal])
        
        estruturas = [
            f"Continuei no curso porque {fator}. {self._complemento_permanencia(fator_principal)}",
            f"O que me fez permanecer foi {fator}. {self._complemento_permanencia(fator_principal)}",
            f"O fator decisivo foi {fator}. {self._complemento_permanencia(fator_principal)}",
            f"Graças a {fator} consegui seguir no curso. {self._complemento_permanencia(fator_principal)}"
        ]
        
        return random.choice(estruturas)

    def _complemento_permanencia(self, fator):
        """Adiciona detalhes ao fator de permanência"""
        complementos = {
            'apoio': [
                "O programa de bolsas foi essencial para minha continuidade.",
                "Os professores sempre estiveram disponíveis para tirar dúvidas."
            ],
            'vocação': [
                "Cada semestre me identifico mais com a área de TI.",
                "As oportunidades de estágio na área são muito atraentes."
            ],
            'social': [
                "Formamos um grupo de estudos que faz toda a diferença.",
                "O ambiente colaborativo entre os alunos é inspirador."
            ]
        }
        return random.choice(complementos[fator])

    def gerar_dataframe(self):
        """Gera DataFrame com entrevistas fictícias"""
        dados = []
        
        for i in range(self.n_entrevistas):
            regiao = random.choice(list(self.regioes.keys()))
            curso = random.choice(self.regioes[regiao]['cursos'])
            evasao_rate = self.regioes[regiao]['evasao']
            
            # Determinar situação baseada na taxa de evasão da região
            if random.random() < evasao_rate:
                situacao = 'Evadido'
                motivo_principal = random.choice(list(self.motivos_evasao.keys()))
                texto = self._gerar_texto_evasao(motivo_principal)
                sentimento = 'Negativo' if random.random() > 0.2 else 'Neutro'
            else:
                situacao = random.choices(['Formado', 'Cursando'], weights=[0.3, 0.7])[0]
                fator_principal = random.choice(list(self.fatores_permanencia.keys()))
                texto = self._gerar_texto_permanencia(fator_principal)
                sentimento = 'Positivo' if random.random() > 0.7 else 'Neutro'
            
            # Gerar metadados adicionais
            idade = random.randint(17, 40)
            genero = random.choices(['Masculino', 'Feminino', 'Não-binário'], weights=[0.6, 0.35, 0.05])[0]
            periodo = random.choice(['Matutino', 'Vespertino', 'Noturno', 'Integral'])
            semestre = random.randint(1, 8) if situacao == 'Cursando' else 8 if situacao == 'Formado' else random.randint(1, 6)
            
            dados.append({
                'id': i + 1,
                'texto': texto,
                'regiao': regiao,
                'curso': curso,
                'genero': genero,
                'idade': idade,
                'periodo': periodo,
                'semestre': semestre,
                'situacao': situacao,
                'sentimento': sentimento,
                'data_entrevista': fake.date_between(start_date='-2y', end_date='today')
            })
        
        return pd.DataFrame(dados)

# Exemplo de uso
if __name__ == "__main__":
    gerador = GeradorEntrevistas(300)
    df_entrevistas = gerador.gerar_dataframe()
    df_entrevistas.to_csv('dados_entrevistas_ficticias.csv', index=False)
    print("Dataset com 300 entrevistas fictícias gerado e salvo como 'dados_entrevistas_ficticias.csv'")
