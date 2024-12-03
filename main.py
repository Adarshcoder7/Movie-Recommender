import streamlit as st
import pandas as pd
import pickle
import requests

def fetch(movie_id):
    response = requests.get(
        'https://api.themoviedb.org/3/movie/{}?api_key=2b2380c19ea7ba3c16b9693b7096fc7a&language=en-US'.format(movie_id)
    )
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    rmovies = []
    rmovieposter = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        rmovies.append(movies.iloc[i[0]].title)
        rmovieposter.append(fetch(movie_id))
    return rmovies, rmovieposter
 
moviedict = pickle.load(open('movie_dict2.pkl', 'rb'))
movies = pd.DataFrame(moviedict)
similarity = pickle.load(open('similarity2.pkl', 'rb'))
st.markdown(
    """
    <h1 style='color: teal;'>Movie Recommender</h1>
    """,
    unsafe_allow_html=True
)
st.markdown("### Search for Movies")
option = st.selectbox(
    label='',
    options=movies['title'].values
)
if st.button('Recommend'):
    names, posters = recommend(option)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(names[0])
        st.image(posters[0])
    with col2:
        st.text(names[1])
        st.image(posters[1])
    with col3:
        st.text(names[2])
        st.image(posters[2])
    with col4:
        st.text(names[3])
        st.image(posters[3])
    with col5:
        st.text(names[4])
        st.image(posters[4])
st.markdown(
    """
    <h1 style='color: red;'>All Movies</h1>
    """,
    unsafe_allow_html=True
)
cols = st.columns(5)
for idx, row in enumerate(movies.head(10).iterrows()):
    col = cols[idx % 5]
    with col:
        st.text(row[1]['title'])
        st.image(fetch(row[1]['movie_id']))      
