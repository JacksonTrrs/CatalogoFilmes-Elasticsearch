import requests

# ==================================================
# CONFIGURAÇÕES E CONSTANTES
# ==================================================
URL_BUSCAR_FILME = "http://localhost:9200/filmes/_search"
URL_ADD_FILME = "http://localhost:9200/filmes/_doc"

# ==================================================
# FUNÇÕES DE LÓGICA
# ==================================================

def buscar_query(query_json):
    """Função auxiliar para executar o GET no Elastic."""
    try:
        resposta = requests.get(URL_BUSCAR_FILME, json=query_json)
        resposta.raise_for_status()
        dados = resposta.json()
        return dados["hits"]["hits"]
    except Exception as e:
        print(f"Erro no Backend: {e}") # Log no terminal
        return []

def buscar_no_elastic(termo_digitado):
    """Busca por termo específico (Multi-match)."""
    if not termo_digitado:
        return []

    query_json = {
        "size": 50,
        "query": {
            "multi_match": {
                "query": termo_digitado,
                "fields": ["titulo^3", "sinopse"],
                "fuzziness": "AUTO"
            }
        }
    }
    return buscar_query(query_json)

def buscar_todos():
    """Busca todos os filmes (Match All)."""
    query_json = {
        "size": 50,
        "query": {
            "match_all": {}
        }
    }
    return buscar_query(query_json)

def buscar_com_filtros(termo_digitado, categorias_selecionadas):
    #Realiza busca combinando texto (opcional) e filtros de categoria (opcional). Usa a query 'bool' do Elasticsearch.

    # 1. Monta a parte de TEXTO (MUST)
    if termo_digitado:
        must_clause = {
            "multi_match": {
                "query": termo_digitado,
                "fields": ["titulo^3", "sinopse"],
                "fuzziness": "AUTO"
            }
        }
    else:
        # Se não digitou nada, traz tudo
        must_clause = {"match_all": {}}

    # 2. Monta a parte de FILTRO (FILTER)
    filter_clause = []
    if categorias_selecionadas:
        # 'terms' busca qualquer filme que tenha UMA das categorias da lista.
        filter_clause.append({
            "terms": {
                "genero": categorias_selecionadas
            }
        })

    # 3. Monta a Query Final
    query_json = {
        "size": 50,
        "query": {
            "bool": {
                "must": must_clause,
                "filter": filter_clause
            }
        }
    }

    return buscar_query(query_json)

def adicionar_filme(titulo, sinopse, genero, ano, capa):
    """Envia um POST para adicionar um novo filme."""
    filme_doc = {
        "titulo": titulo,
        "sinopse": sinopse,
        "genero": genero,
        "ano": int(ano),
        "capa": capa
    }
    try:
        resposta = requests.post(URL_ADD_FILME, json=filme_doc)
        resposta.raise_for_status()
        return True, "Filme adicionado com sucesso."
    except Exception as e:
        return False, f"Erro ao adicionar: {e}"