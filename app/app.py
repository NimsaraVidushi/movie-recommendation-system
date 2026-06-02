import streamlit as st

st.title("🎬 Movie Recommendation System")

st.write("Welcome to my Movie Recommendation System!")

movie_name = st.text_input("Enter a movie name")

if st.button("Recommend"):
    st.write(f"You entered: {movie_name}")