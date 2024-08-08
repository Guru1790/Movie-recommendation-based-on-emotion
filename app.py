import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from PIL import Image
import io

# Dictionary to map genres to IMDb URLs
URLS = {
    "Drama": 'https://www.imdb.com/search/title/?title_type=feature&genres=drama',
    "Action": 'https://www.imdb.com/search/title/?title_type=feature&genres=action',
    "Comedy": 'https://www.imdb.com/search/title/?title_type=feature&genres=comedy',
    "Horror": 'https://www.imdb.com/search/title/?title_type=feature&genres=horror',
    "Crime": 'https://www.imdb.com/search/title/?title_type=feature&genres=crime',
}

def fetch_movie_titles(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    titles = []
    while url:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Check for HTTP errors
            soup = BeautifulSoup(response.text, "lxml")

            # Extract movie titles
            titles.extend(a.get_text() for a in soup.find_all('a', href=re.compile(r'/title/tt\d+/')))

            # Find the next page URL
            next_page = soup.find('a', class_='next-page')
            url = next_page['href'] if next_page else None
            if url:
                url = f'https://www.imdb.com{url}'
        except requests.RequestException as e:
            st.error(f"Error fetching data: {e}")
            break

    return titles

# Streamlit App
st.set_page_config(page_title="IMDb Movie Finder", page_icon="🎬")

# Upload background image
uploaded_file = st.file_uploader("Upload background image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Read and display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Background Image', use_column_width=True)

    # Convert the image to a format that can be used in CSS
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_base64 = image_bytes.getvalue().hex()

    # Apply custom CSS for background image
    st.markdown(
        f"""
        <style>
        .reportview-container {{
            background: url(data:image/png;base64,{image_base64}) no-repeat center center fixed;
            background-size: cover;
            background-attachment: fixed;
            background-color: #000000;  /* Fallback color */
        }}
        .sidebar .sidebar-content {{
            background: rgba(255, 255, 255, 0.8);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    # Use a default background image if no file is uploaded
    st.markdown(
        """
        <style>
        .reportview-container {
            background: url('https://hips.hearstapps.com/hmg-prod.s3.amazonaws.com/images/summer-movies-1587392939.jpg') no-repeat center center fixed;
            background-size: cover;
            background-attachment: fixed;
            background-color: #000000;  /* Fallback color */
        }
        .sidebar .sidebar-content {
            background: rgba(255, 255, 255, 0.8);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

st.title("IMDb Movie Finder")

# User input for genre
genre = st.selectbox("Select Genre", list(URLS.keys()))

if st.button("Get Movies"):
    if genre:
        st.write(f"Fetching movies for genre: {genre}...")
        url = URLS.get(genre)
        movie_titles = fetch_movie_titles(url)
        
        if not movie_titles:
            st.write("No titles found.")
        else:
            max_titles = 14 if genre in ["Drama", "Action", "Comedy", "Horror", "Crime"] else 12
            st.write("### Top Movie Titles:")
            for title in movie_titles[:max_titles]:
                st.write(title)
    else:
        st.write("Please select a genre.")
