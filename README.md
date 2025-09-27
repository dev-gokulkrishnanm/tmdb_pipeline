# TMDB ETL Pipeline

A Python-based ETL (Extract, Transform, Load) pipeline that fetches popular movies data from The Movie DB (TMDB) API, processes it, and stores it in a SQLite database.

## Overview

This program performs the following operations:
1. **Extract**: Fetches popular movies and genre data from TMDB API
2. **Transform**: Processes and refines the movie data, adding genre names and calculating derived fields
3. **Load**: Stores the processed data into a SQLite database

## Features

- Fetches popular movies from TMDB API
- Retrieves movie genres and maps them to movies
- Calculates derived fields (release year, blockbuster status)
- Caches API responses as JSON files to avoid repeated API calls
- Stores data in SQLite database with duplicate handling
- Environment-based configuration using `.env` file


### Python Dependencies
```
sqlalchemy
python-dotenv
requests
```

### Environment Variables
Create a `.env` file in the project root with the following variables:
```
TMDB_API_KEY=your_tmdb_api_key_here
TMDB_BASE_URL=https://api.themoviedb.org/3
DB_FILE=movies.db
```

## Installation

1. Clone or download this repository
2. Install required dependencies:
   ```bash
   pip install sqlalchemy python-dotenv requests
   ```
3. Get a TMDB API key from [The Movie DB](https://www.themoviedb.org/settings/api)
4. Create a `.env` file with your API credentials (see requirements section above)

## Usage

Run the ETL pipeline:
```bash
python3 tmb_etl.py
```

## Data Flow

### 1. Extract Phase
- First attempts to load cached data from `movies.json` and `genres.json`
- If files don't exist, fetches data from TMDB API:
  - Popular movies: `/movie/popular`
  - Movie genres: `/genre/movie/list`
- Saves API responses as JSON files for future use (limit the API request rate)

### 2. Transform Phase
- Maps genre IDs to genre names using the genres lookup
- Creates refined movie records with selected fields:
  - `tmdb_id`: Original TMDB movie ID
  - `original_title`: Movie title
  - `overview`: Movie description
  - `release_date`: Release date (YYYY-MM-DD)
  - `release_year`: Extracted year from release date
  - `vote_average`: TMDB rating
  - `genres`: Array of genre names
  - `is_blockbuster`: Boolean flag for movies with rating ≥ 7.0

### 3. Load Phase
- Creates SQLite database and movies table if they don't exist
- Inserts processed movie data with duplicate handling (OR IGNORE)
- Stores genres as JSON text in the database

## Database Schema

The `movies` table contains the following columns:
- `id`: Primary key (auto-increment)
- `tmdb_id`: Unique TMDB movie ID
- `title`: Movie title
- `overview`: Movie description/plot
- `release_date`: Release date string
- `release_year`: Release year (4 characters)
- `vote_average`: Movie rating (float)
- `is_blockbuster`: Boolean indicating if rating ≥ 7.0
- `genres`: JSON string containing genre names

## Output Files

The program creates the following files:
- `movies.json`: Cached raw movie data from TMDB API
- `genres.json`: Cached genre data from TMDB API
- `movies_with_genres.json`: Processed movies with genre names
- `movies.db`: SQLite database with processed movie data

## Error Handling

- Uses try/except blocks to handle missing cache files
- Falls back to API calls when local files are unavailable
- Implements duplicate handling in database inserts
- Uses environment variables for configuration management

## Notes

- The program fetches only popular movies (typically 20 results)
- API responses are cached locally to minimize API calls
- Duplicate movies are ignored during database insertion
- SQLite database is created automatically if it doesn't exist
