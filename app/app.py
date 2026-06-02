import requests
import streamlit as st
from functools import lru_cache

TMDB_API_KEY = st.secrets.get("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w342"

# Page configuration
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

# Theme selector
theme = st.sidebar.radio("Theme", ["Light", "Dark"], index=0)

is_dark = theme == "Dark"
background = "#111111" if is_dark else "#f8f9fa"
card_bg = "#1f1f1f" if is_dark else "#ffffff"
text_color = "#f5f5f5" if is_dark else "#0f172a"
muted_color = "#cbd5e1" if is_dark else "#64748b"

# Custom CSS
st.markdown(
    f"""
    <style>
    .main {{
        padding-top: 2rem;
        color: {text_color};
    }}
    body, .stApp {{
        background-color: {background};
        color: {text_color};
    }}
    .title {{
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        color: {text_color};
    }}
    .subtitle {{
        text-align: center;
        color: {muted_color};
        margin-bottom: 30px;
    }}
    .movie-card {{
        padding: 18px;
        border-radius: 18px;
        background-color: {card_bg};
        color: {text_color};
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
        margin-bottom: 16px;
    }}
    .tmdb-poster {{
        border-radius: 12px;
        width: 100%;
    }}
    .movie-meta {{
        color: {muted_color};
        margin-bottom: 8px;
    }}
    .genre-pill {{
        display: inline-block;
        margin: 0 4px 4px 0;
        padding: 4px 10px;
        border-radius: 999px;
        background-color: rgba(255,255,255,0.08);
        color: {text_color};
        font-size: 0.85rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown('<p class="title">🎬 Movie Recommendation System</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Search with TMDB, filter genres, and view ratings, posters, and confidence scores.</p>', unsafe_allow_html=True)

# TMDB API helpers

def tmdb_get(path, params=None):
    params = params or {}
    params.update({"api_key": TMDB_API_KEY, "language": "en-US"})
    response = requests.get(f"{TMDB_BASE_URL}{path}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()

@lru_cache(maxsize=1)
def get_genre_map():
    try:
        response = tmdb_get("/genre/movie/list")
        return {genre["id"]: genre["name"] for genre in response.get("genres", [])}
    except Exception:
        return {}


def make_poster_url(path):
    return f"{TMDB_IMAGE_BASE}{path}" if path else None


def search_movie(query):
    response = tmdb_get("/search/movie", {"query": query, "include_adult": False, "page": 1})
    return response.get("results", [])


def get_movie_details(movie_id):
    return tmdb_get(f"/movie/{movie_id}", {"append_to_response": "credits"})


def get_similar_movies(movie_id):
    response = tmdb_get(f"/movie/{movie_id}/similar", {"page": 1})
    return response.get("results", [])


def get_trending_movies():
    response = tmdb_get("/trending/movie/week")
    return response.get("results", [])[:10]


def genre_names(genre_ids):
    genre_map = get_genre_map()
    return [genre_map.get(genre_id, "Unknown") for genre_id in genre_ids]


def score_confidence(vote_average, popularity):
    confidence = 0.5 * vote_average * 10 + min(popularity / 15, 30)
    return round(min(100.0, confidence), 1)

# Sidebar content
st.sidebar.title("About")
st.sidebar.info(
    """
    This movie recommendation app uses The Movie Database (TMDB) API to deliver:
    - Movie posters
    - Ratings and release year
    - Genre filters
    - Trending movie picks
    - Recommendation confidence scores
    """
)

if not TMDB_API_KEY:
    st.sidebar.error("Add TMDB_API_KEY to Streamlit secrets to enable TMDB integration.")

# Trending section in sidebar
try:
    trending_movies = get_trending_movies() if TMDB_API_KEY else []
except Exception:
    trending_movies = []

if trending_movies:
    st.sidebar.markdown("### 🔥 Top 10 Trending Movies")
    for movie in trending_movies:
        poster = make_poster_url(movie.get("poster_path"))
        if poster:
            st.sidebar.image(poster, width=90)
        st.sidebar.markdown(f"**{movie.get('title', 'Unknown')}**  \n{movie.get('release_date', '')[:4]} • ⭐ {movie.get('vote_average', 0)}")
        st.sidebar.markdown("---")

# Search controls
movie_name = st.text_input("Enter a movie name", placeholder="Example: Avatar")
selected_genres = st.multiselect(
    "Filter recommended movies by genre",
    options=sorted(get_genre_map().values()),
    help="Only show similar movies that match the selected genres."
)

if st.button("🔍 Get Recommendations", use_container_width=True):
    if not movie_name:
        st.warning("Please enter a movie name.")
    elif not TMDB_API_KEY:
        st.error("TMDB API key is missing. Please add it to secrets.")
    else:
        try:
            search_results = search_movie(movie_name)
        except requests.RequestException:
            st.error("Unable to reach TMDB. Please check your internet connection and API key.")
            search_results = []

        if not search_results:
            st.warning(f"No movie found for '{movie_name}'. Try another title.")
        else:
            movie = search_results[0]
            movie_id = movie["id"]
            try:
                details = get_movie_details(movie_id)
            except requests.RequestException:
                st.error("Unable to fetch movie details from TMDB.")
                details = movie

            genres = []
            if isinstance(details.get("genres"), list):
                genres = [genre.get("name") for genre in details.get("genres", []) if genre.get("name")]
            elif isinstance(details.get("genre_ids"), list):
                genres = genre_names(details.get("genre_ids", []))

            poster_url = make_poster_url(details.get("poster_path"))
            overview = details.get("overview", "No overview available.")
            release_year = details.get("release_date", "Unknown")[:4]
            rating = details.get("vote_average", 0)
            popularity = details.get("popularity", 0)

            st.markdown(
                f"""
                <div class="movie-card">
                    <div style='display:flex; gap: 24px; flex-wrap: wrap;'>
                        <div style='flex: 0 0 220px;'>
                            {'<img class="tmdb-poster" src="' + poster_url + '" />' if poster_url else '<div style="width:220px;height:330px;background:#333;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#ddd;">No Image</div>'}
                        </div>
                        <div style='flex: 1; min-width: 280px;'>
                            <h2>🎬 {details.get('title', movie.get('title', 'Unknown'))} ({release_year})</h2>
                            <p class="movie-meta">Rating: ⭐ {rating} / 10 • Popularity: {popularity:.1f}</p>
                            <p class="movie-meta">Genres: {' • '.join(genres) if genres else 'Unknown'}</p>
                            <p>{overview}</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            try:
                similar_movies = get_similar_movies(movie_id)
            except requests.RequestException:
                similar_movies = []

            if selected_genres:
                similar_movies = [
                    item for item in similar_movies
                    if set(selected_genres) & set(genre_names(item.get("genre_ids", [])))
                ]

            if not similar_movies:
                st.info("No similar titles found for this selection. Showing trending movies instead.")
                similar_movies = trending_movies[:6]

            st.markdown("### Recommended Movies")
            rec_columns = st.columns(2)
            for index, rec in enumerate(similar_movies[:6]):
                with rec_columns[index % 2]:
                    rec_poster = make_poster_url(rec.get("poster_path"))
                    rec_genres = genre_names(rec.get("genre_ids", []))
                    rec_score = score_confidence(rec.get("vote_average", 0), rec.get("popularity", 0))
                    st.markdown(
                        f"""
                        <div class="movie-card">
                            <h4>🎥 {rec.get('title', 'Unknown')}</h4>
                            {f'<img class="tmdb-poster" src="{rec_poster}" />' if rec_poster else ''}
                            <p class="movie-meta">{rec.get('release_date', '')[:4]} • ⭐ {rec.get('vote_average', 0)} / 10</p>
                            <p class="movie-meta">Confidence: <strong>{rec_score}%</strong></p>
                            <p>{rec.get('overview', 'No overview available.')[:160]}...</p>
                            <div>{' '.join(f'<span class="genre-pill">{genre}</span>' for genre in rec_genres)}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            if trending_movies:
                st.markdown("---")
                st.markdown("### 🔥 Trending Now")
                trending_cols = st.columns(5)
                for idx, item in enumerate(trending_movies):
                    with trending_cols[idx % 5]:
                        poster = make_poster_url(item.get("poster_path"))
                        if poster:
                            st.image(poster, use_column_width=True)
                        st.markdown(f"**{item.get('title', 'Unknown')}**", unsafe_allow_html=True)
                        st.markdown(
                            f"<p class='movie-meta'>{item.get('release_date', '')[:4]} • ⭐ {item.get('vote_average', 0)}</p>",
                            unsafe_allow_html=True,
                        )
