import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main {
    padding-top: 2rem;
}
.title {
    text-align: center;
    font-size: 3rem;
    font-weight: bold;
}
.subtitle {
    text-align: center;
    color: gray;
    margin-bottom: 30px;
}
.movie-card {
    padding: 15px;
    border-radius: 10px;
    background-color: #f5f5f5;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="title">🎬 Movie Recommendation System</p>',
            unsafe_allow_html=True)

st.markdown(
    '<p class="subtitle">Find movies similar to your favorites</p>',
    unsafe_allow_html=True
)

# Search area
movie_name = st.text_input(
    "Enter a Movie Name",
    placeholder="Example: Avatar"
)

# Button
if st.button("🔍 Get Recommendations", use_container_width=True):

    if movie_name == "":
        st.warning("Please enter a movie name.")
    else:
        st.success(f"Recommendations for '{movie_name}'")

        recommendations = [
            "Interstellar",
            "The Martian",
            "Guardians of the Galaxy",
            "Star Wars",
            "Inception"
        ]

        cols = st.columns(2)

        for i, movie in enumerate(recommendations):

            with cols[i % 2]:
                st.markdown(
                    f"""
                    <div class="movie-card">
                        <h4>🎥 {movie}</h4>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# Sidebar
st.sidebar.title("About")
st.sidebar.info(
    """
    Movie Recommendation System

    Built using:
    - Python
    - Pandas
    - Scikit-Learn
    - Streamlit
    """
)