import requests, os, logging, time
from django.conf import settings
from .models import Work

TMDB_API_KEY = settings.TMDB_API_KEY
TMDB_SEARCH_URL  = 'https://api.themoviedb.org/3/search/multi'
TMDB_DETAILS_URL = 'https://api.themoviedb.org/3/{media_type}/{id}'

GOOGLE_API_KEY = settings.GOOGLE_BOOKS_KEY    
GB_SEARCH_URL  = 'https://www.googleapis.com/books/v1/volumes'
GB_VOLUME_URL  = 'https://www.googleapis.com/books/v1/volumes/{id}'

def tmdb_search(query: str, page: int = 1):
    """Возвращает сырой список результатов TMDB (фильмы + сериалы)."""
    r = requests.get(
        TMDB_SEARCH_URL,
        params={
            'api_key': TMDB_API_KEY,
            'query':   query,
            'page':    page,
            'include_adult': False,
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json().get('results', [])

def tmdb_external_results(query: str, media_type: str | None = None) -> list[dict]:
    """
    Данные для автодополнения поиска.
    Пример результата:
      {'id':'movie:27205', 'title':'Inception', 'year':'2010', 'kind':'Фильм'}
    """
    raw      = tmdb_search(query)
    results  = []
    for item in raw:
        if item["media_type"] not in ("movie", "tv"):
            continue
        if media_type and item["media_type"] != media_type:
            continue

        raw_date = item.get("release_date") or item.get("first_air_date") or ""
        year     = raw_date.split("-")[0] if raw_date else ""

        results.append({
            "id"   : f"{item['media_type']}:{item['id']}",
            "title": item.get("title") or item.get("name"),
            "year" : year,
            "kind" : "Фильм" if item["media_type"] == "movie" else "Сериал",
        })
    return results


def tmdb_fetch_and_upsert(external_id: str):
    """
    external_id: строка вида  'movie:1895'  или  'tv:456'
    Создаёт/обновляет Work и возвращает его.
    """
    try:
        media_type, tmdb_id = external_id.split(':', 1)
    except ValueError:
        raise ValueError("external_id должен быть вида 'movie:123' или 'tv:456'")

    url  = TMDB_DETAILS_URL.format(media_type=media_type, id=tmdb_id)
    resp = requests.get(url, params={'api_key': TMDB_API_KEY, 'language': 'ru-RU'})
    resp.raise_for_status()
    data = resp.json()

    defaults = {
        'title':        data.get('title') or data.get('name'),
        'overview':     data.get('overview', ''),
        'poster_path':  data.get('poster_path') or '',
        'external_id':  external_id,
        'type':         'movie'  if media_type == 'movie' else 'series',
        'genre':        ', '.join(g['name'] for g in data.get('genres', [])),
        'rating':       data.get('vote_average') or 0,
        'release_date': data.get('release_date') or data.get('first_air_date') or None,
    }

    work, _created = Work.objects.update_or_create(
        external_id=external_id,
        defaults=defaults
    )
    return work

upsert_work_from_tmdb = tmdb_fetch_and_upsert

def gbooks_search(query, limit=10):
    res = requests.get(GB_SEARCH_URL, params={
        "q"         : query,
        "maxResults": limit,
        "key"       : GOOGLE_API_KEY,
        "printType" : "books",
    }).json()

    out = []
    for item in res.get("items", []):
        info = item.get("volumeInfo", {})
        raw_date = info.get("publishedDate", "")
        year = raw_date.split("-")[0] if raw_date else ""
        out.append({
            "id"   : f"book:{item['id']}",
            "title": info.get("title", "—"),
            "year" : year,
            "kind" : "Книга",
        })
    return out

def gbooks_fetch_and_upsert(google_id):
    r = requests.get(
        GB_VOLUME_URL.format(id=google_id),
        params={'key': GOOGLE_API_KEY}
    )
    r.raise_for_status()
    data = r.json()

    info = data['volumeInfo']
    defaults = {
        'title'      : info.get('title'),
        'overview'   : info.get('description', ''),
        'poster_path': info.get('imageLinks', {}).get('thumbnail', ''),
        'genres_text': ', '.join(info.get('categories', [])),
        'type'       : Work.TYPE_BOOK,
    }
    work, _ = Work.objects.update_or_create(
        google_id = google_id,
        defaults  = defaults
    )
    return work
