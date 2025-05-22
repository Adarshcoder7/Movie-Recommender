import streamlit as st
import pandas as pd
import pickle
import requests
import os

# Fetch movie details
def fetch_movie_details(movie_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=67a77732d95fc052e78a06b8c092db4f&language=en-US'
    )
    data = response.json()

    # Fetch trailer key
    trailer_response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=67a77732d95fc052e78a06b8c092db4f&language=en-US'
    )
    trailer_data = trailer_response.json()
    trailer_key = None
    for video in trailer_data.get('results', []):
        if video['type'] == 'Trailer' and video['site'] == 'YouTube':
            trailer_key = video['key']
            break

    return {
        "poster": f"https://image.tmdb.org/t/p/w500/{data['poster_path']}",
        "title": data.get('title', 'Unknown'),
        "overview": data.get('overview', 'No description available.'),
        "release_date": data.get('release_date', 'N/A'),
        "genres": [genre['name'] for genre in data.get('genres', [])],
        "trailer_key": trailer_key,
    }

# Fetch trending movies
def fetch_trending_movies():
    response = requests.get(
        'https://api.themoviedb.org/3/trending/movie/week?api_key=67a77732d95fc052e78a06b8c092db4f'
    )
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        return []

# Recommendation function
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = []
    for i in distances[1:6]:  # Top 5 recommendations
        movie_id = movies.iloc[i[0]].movie_id
        details = fetch_movie_details(movie_id)
        recommended_movies.append(details)
    return recommended_movies

# Load data
moviedict = pickle.load(open('movie_dict2.pkl', 'rb'))
movies = pd.DataFrame(moviedict)
def download_file_from_google_drive(file_id, destination):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url)
    with open(destination, 'wb') as f:
        f.write(response.content)

if not os.path.exists("similarity2.pkl"):
    download_file_from_google_drive("1rKUInmfh17kNkE4dSgB7umf6znkP3c4m", "similarity2.pkl")
with open('similarity2.pkl', 'rb') as f:
    similarity = pickle.load(f)

# Set page config
st.set_page_config(page_title="Animated Movie Recommender", layout="wide")

# CSS for Animations
st.markdown(
    """
    <style>
    .movie-card {
        position: relative;
        border: 1px solid #ddd;
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        overflow: hidden;
    }
    .movie-card:hover .trailer {
        display: block;
    }
    .trailer {
        display: none;
        position: absolute;
        top: 10px;
        right: 10px;
        width: 300px;
        height: 170px;
        z-index: 1000;
        border: 2px solid white;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
        background-color: black;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header with animation
st.markdown(
    "<h1 class='fade-in'>Movie Recommendation System</h1>",
    unsafe_allow_html=True,
)

# Movie Search Section
st.markdown("<div class='slide-up'><h3>Search for a Movie</h3></div>", unsafe_allow_html=True)
search_query = st.text_input("Type a movie name to search:", "")
if search_query:
    filtered_movies = movies[movies['title'].str.contains(search_query, case=False, na=False)]
    if not filtered_movies.empty:
        selected_movie = st.selectbox("Select a Movie", filtered_movies['title'].values)

        if selected_movie:
            st.markdown("<div class='slide-up'><h3>🎬 Recommended Movies</h3></div>", unsafe_allow_html=True)
            recommended_movies = recommend(selected_movie)

            # Display Recommended Movies with Cards
            for idx, movie in enumerate(recommended_movies):
                with st.container():
                    st.markdown(
                        f"""
                        <div class="movie-card">
                            <img src="{movie['poster']}" style="width: 100px; float: left; margin-right: 20px; border-radius: 8px;">
                            <h4>{movie['title']}</h4>
                            <p><strong>Genres:</strong> {', '.join(movie['genres'])}</p>
                            <p><strong>Release Date:</strong> {movie['release_date']}</p>
                            <p>{movie['overview'][:150]}...</p>
                            {"<iframe class='trailer' src='https://www.youtube.com/embed/" + movie['trailer_key'] + "?autoplay=1' allowfullscreen></iframe>" if movie['trailer_key'] else ""}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

# Trending Movies Section
st.markdown("<div class='fade-in'><h2 style='color: red;'>Trending Movies</h2></div>", unsafe_allow_html=True)
trending_movies = fetch_trending_movies()

# Display Trending Movies
if trending_movies:
    for idx, movie in enumerate(trending_movies[:5]):
        movie_id = movie.get('id')
        details = fetch_movie_details(movie_id)
        with st.container():
            st.markdown(
                f"""
                <div class="movie-card">
                    <img src="https://image.tmdb.org/t/p/w500/{movie.get('poster_path')}" 
                         style="width: 100px; float: left; margin-right: 20px; border-radius: 8px;">
                    <h4>{movie.get('title', 'Unknown')}</h4>
                    <p><strong>Release Date:</strong> {movie.get('release_date', 'N/A')}</p>
                    <p>{movie.get('overview', 'No description available.')[:150]}...</p>
                    {"<iframe class='trailer' src='https://www.youtube.com/embed/" + details['trailer_key'] + "?autoplay=1' allowfullscreen></iframe>" if details['trailer_key'] else ""}
                </div>
                """,
                unsafe_allow_html=True,
            )
