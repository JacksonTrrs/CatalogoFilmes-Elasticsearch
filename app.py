import requests
import streamlit as st

# ==================================================
# 1. CONFIGURAÇÕES E CONSTANTES
# ==================================================

URL_ELASTIC = "http://localhost:9200/filmes/_search"


# ==================================================
# 2. BACKEND (Lógica e Conexão)
# ==================================================

def buscar_no_elastic(termo_digitado):
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
    query_json = {
        "size": 50,
        "query": {
            "match_all": {}
        }
    }
    return buscar_query(query_json)


def buscar_query(query_json):
    try:
        resposta = requests.get(URL_ELASTIC, json=query_json)
        resposta.raise_for_status()
        dados = resposta.json()
        return dados["hits"]["hits"]
    except Exception as e:
        st.error(f"Erro ao conectar no Docker: {e}")
        return []


# ==================================================
# 3. FRONTEND (Interface Visual)
# ==================================================

st.set_page_config(layout="wide", page_title="Catálogo de Filmes - Elasticsearch", page_icon="🎬")

st.title("🎬 Catálogo de Filmes - Elasticsearch")
st.markdown("Projeto acadêmico - Banco de Dados 2")

# Barra de busca centralizada
col_a, col_b, col_c = st.columns([1, 3, 1])
with col_b:
    termo = st.text_input("Procure um filme.", placeholder="Ex: Harry Poter, Vingadores...")

st.divider()


def exibir_filmes(resultados):
    if not resultados:
        st.warning("Nenhum filme encontrado. Tente outra palavra!")
    else:
        # Mostra a contagem só se for uma busca específica
        if termo:
            st.success(f"Encontramos {len(resultados)} resultados para '{termo}'")

        # --- GRID DE CARDS ---
        cols = st.columns(4)

        for i, hit in enumerate(resultados):
            filme = hit["_source"]
            score = hit["_score"]

            # Pega a imagem ou usa uma padrão se não tiver
            imagem = filme.get("capa", "https://via.placeholder.com/300x450?text=Sem+Capa")

            # Exibe no Card
            with cols[i % 4]:
                with st.container(border=True, height=900):
                    # Altura fixa na imagem ajuda a alinhar os cards (opcional)
                    st.image(imagem, use_container_width=True)

                    # Título com tamanho de fonte controlado
                    st.markdown(f"### {filme.get('titulo')}")

                    st.caption(f"📅 {filme.get('ano')} | ⭐ Score: {score:.2f}")
                    st.write(f"**{filme.get('genero')}**")

                    with st.expander("Sinopse"):
                        st.write(filme.get("sinopse"))


# ==================================================
# 4. LÓGICA PRINCIPAL
# ==================================================

# Se tiver termo digitado, busca específico.
# Se NÃO tiver (tela inicial), busca todos (Catálogo Completo).
if termo:
    resultados = buscar_no_elastic(termo)
else:
    resultados = buscar_todos()

exibir_filmes(resultados)