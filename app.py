import streamlit as st
import backend as api  # Importamos o nosso arquivo de lógica

# Lista padrão de gêneros para garantir consistência
LISTA_GENEROS = [
    "Ação",
    "Aventura",
    "Animação",
    "Comédia",
    "Crime",
    "Drama",
    "Fantasia",
    "Romance",
    "Sci-Fi",
    "Terror"
]

# ==================================================
# CONFIGURAÇÃO DA PÁGINA
# ==================================================
st.set_page_config(layout="wide", page_title="Catálogo de Filmes", page_icon="🎬")

st.title("🎬 Catálogo de Filmes - Elasticsearch")
st.markdown("Projeto acadêmico - Banco de Dados 2")


# ==================================================
# COMPONENTES DE UI (Funções Visuais)
# ==================================================

def renderizar_sidebar():
    """Renderiza Filtros e Formulário de Adição."""
    filtros_selecionados = []

    with st.sidebar:
        # --- SEÇÃO DE FILTROS ---
        st.header("🔍 Filtros")
        st.write("Selecione os gêneros:")

        # Cria um checkbox para cada gênero da lista
        for genero in LISTA_GENEROS:
            if st.checkbox(genero):
                filtros_selecionados.append(genero)

        st.divider()  # Linha visual para separar

        # --- SEÇÃO DE CADASTRO ---
        st.header("Cadastrar Filme")
        with st.expander("Abrir Formulário"):  # Usei expander para limpar a tela
            with st.form("form_add_filme"):
                novo_titulo = st.text_input("Título")
                novo_genero = st.selectbox("Gênero", LISTA_GENEROS)  # Usa a mesma lista
                novo_ano = st.number_input("Ano", min_value=1900, max_value=2030, step=1)
                nova_capa = st.text_input("URL Capa")
                nova_sinopse = st.text_area("Sinopse")

                btn_salvar = st.form_submit_button("Salvar")

                if btn_salvar:
                    if novo_titulo and nova_sinopse:
                        sucesso, msg = api.adicionar_filme(novo_titulo, nova_sinopse, novo_genero, novo_ano, nova_capa)
                        if sucesso:
                            st.success(msg)
                        else:
                            st.error(msg)
                    else:
                        st.warning("Preencha Título e Sinopse.")

    return filtros_selecionados


def renderizar_grid_filmes(resultados, termo_busca=None):
    """Renderiza a grade de cards baseada na lista de resultados."""
    if not resultados:
        st.warning("Nenhum filme encontrado. Tente outra palavra!")
        return

    # Feedback de quantidade
    if termo_busca:
        st.success(f"Encontramos {len(resultados)} resultados para '{termo_busca}'")

    # Grid Layout
    cols = st.columns(4)
    for i, hit in enumerate(resultados):
        filme = hit["_source"]
        score = hit["_score"]
        imagem = filme.get("capa", "https://via.placeholder.com/300x450?text=Sem+Capa")

        with cols[i % 4]:
            with st.container(border=True, height=900):
                st.image(imagem, use_container_width=True)
                st.markdown(f"### {filme.get('titulo')}")
                st.caption(f"📅 {filme.get('ano')} | ⭐ Score: {score:.2f}")
                st.write(f"**{filme.get('genero')}**")

                with st.expander("Sinopse"):
                    st.write(filme.get("sinopse"))


# ==================================================
# FLUXO PRINCIPAL (Main)
# ==================================================

# 1. Renderiza Barra Lateral
categorias_filtro = renderizar_sidebar()

# 2. Barra de Busca Principal
col_a, col_b, col_c = st.columns([1, 3, 1])
with col_b:
    termo = st.text_input("Procure um filme.", placeholder="Ex: Harry Potter, Vingadores...")

st.divider()

# 3. Busca Inteligente (Texto + Filtros)
resultados = api.buscar_filmes(termo, categorias_filtro)

# 4. Exibição dos Resultados
renderizar_grid_filmes(resultados, termo)