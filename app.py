from flask import Flask, render_template, request
import pickle
import requests

app = Flask(__name__, template_folder='templates', static_folder='static')

similarity = pickle.load(open('similarity.pkl', 'rb'))
movies = pickle.load(open('movie_list.pkl', 'rb'))

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

@app.route('/', methods=['GET'])
def home():
     movies = pickle.load(open('movie_list.pkl', 'rb'))
     movie_list = movies['title'].values
     return render_template ('index.html', movie_list=movie_list)


@app.route('/recommend', methods=['POST'])
def index():
    if request.method == 'POST':
        movies = pickle.load(open('movie_list.pkl', 'rb'))
        movie_list = movies['title'].values

        # Handle the search bar input
        selected_movie = request.form.get('search_bar', None)

        # If the search bar is not filled, use the dropdown
        if selected_movie is None:
            selected_movie = request.form.get('selected_movie', None)

        if selected_movie:
            recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
            return render_template('index.html', 
                                    selected_movie=selected_movie,
                                    recommended_movie_names=recommended_movie_names,
                                    recommended_movie_posters=recommended_movie_posters,
                                    movie_list=movie_list)
        else:
            # Handle the case where no movie is selected
            return render_template('index.html', movie_list=movie_list)

    else:
        movies = pickle.load(open('movie_list.pkl', 'rb'))
        movie_list = movies['title'].values
        return render_template('index.html', movie_list=movie_list)

if __name__ == '__main__':
    # Load the similarity and movies data outside the route function
    # similarity = pickle.load(open('similarity.pkl', 'rb'))
    # movies = pickle.load(open('movie_list.pkl', 'rb'))
    
    app.run(debug=True)
