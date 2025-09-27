import json
import logging
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pprint import pprint
import requests
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Boolean, Text
from sqlalchemy.dialects.sqlite import insert
 
load_dotenv()

def Extract():
    
    try:
        with open("movies.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            print("from_try")
        with open('genres.json','r', encoding="utf-8") as g:
            genres = json.load(g)
        return genres, data
        
        
    except:
        print("from exception")
        api_key = os.getenv('TMDB_API_KEY')
        base_url = os.getenv('TMDB_BASE_URL')
        db_base = os .getenv('DB_FILE')

        headers = {'accept': 'application/json'}
        params = {'api_key':api_key}


        url = f"{base_url}/movie/popular"
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        res = requests.get('https://api.themoviedb.org/3/genre/movie/list?api_key=412d3266faab5495f7c687edec07dd1e&language=en-US')
        genres = res.json()
        with open("genres.json", 'w', encoding="utf-8") as g:
            json.dump(genres, g, indent=4, ensure_ascii=False)
        with open("movies.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    
        return genres, data

def add_genre(data, genres):
    
    genre_lookup = {g["id"]: g["name"] for g in genres["genres"]}
    for movies in data['results']:
        movies["genres"] = [genre_lookup[i] for i in movies["genre_ids"] if i in genre_lookup]
        del movies["genre_ids"]
    try:
        with open('movies_with_genres.json','r', encoding="utf-8") as gen:
            with_genres = json.load(gen)
            return with_genres
        
    except:
        with open("movies_with_genres.json", "w", encoding="utf-8") as with_gen:
            json.dump(data, with_gen, indent=4, ensure_ascii=False)
            return data

def refine(movies_data):
    refined_data = []
    for movie in movies_data['results']:
        refined_movie = {
            'tmdb_id': movie.get('id'),
            'original_title': movie.get('original_title'),
            'overview': movie.get('overview'),
            'release_date': movie.get('release_date'),
            'release_year': movie.get('release_date')[:4],
            'vote_average': movie.get('vote_average'),
            'genres': movie.get('genres'),
            'is_blockbuster': movie.get('vote_average') >= 7.0
        }
        refined_data.append(refined_movie)
    return refined_data

def load_data(data):
    db_file = os.getenv('DB_FILE', 'movies.db')
    db_url = f"sqlite:///{db_file}"
    engine = create_engine(db_url, echo=True)
    metadata = MetaData()
    movies = Table(
    "movies", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("tmdb_id", Integer, unique=True, nullable=False),
    Column("original_title", String, nullable=False),
    Column("overview", Text),
    Column("release_date", String(10)),
    Column("release_year", String(4)),
    Column("vote_average", Float),
    Column("is_blockbuster", Boolean, default=False),
    Column("genres", Text)  # store JSON/text
    )
    metadata.create_all(engine)

    with engine.begin() as conn:
        for m in data:
            stmt = insert(movies).values(
                tmdb_id=m["tmdb_id"],
                title=m["original_title"],
                overview=m["overview"],
                release_date=m["release_date"],
                release_year=m["release_year"],
                vote_average=m["vote_average"],
                is_blockbuster=m["is_blockbuster"],
                genres=json.dumps(m["genres"])
            )
            stmt = stmt.prefix_with("OR IGNORE")  # SQLite: ignore duplicates
            conn.execute(stmt)

genres, data=Extract()
#load_data(data, genres)
movies_data=add_genre(data, genres)
refined_movie_data=refine(movies_data)

load_data(refined_movie_data)



