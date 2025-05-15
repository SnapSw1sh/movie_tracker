import os
import requests
from .models import Work

API_KEY = os.getenv("TMDB_API_KEY")

def search_tmdb(query, media_type="movie"):
    url = f"https://api.themoviedb.org/3/search/{media_type}"
    resp = requests.get(url, params={"api_key": API_KEY, "query": query})
    resp.raise_for_status()
    return resp.json().get("results", [])

def upsert_work(item, media_type="movie"):
    defaults = {
        "overview": item.get("overview", ""),
        "poster_path": item.get("poster_path") or "",
        "release_date": item.get("release_date") or None,
        "external_id": item["id"],
        "genres_text": ", ".join(str(g) for g in item.get("genre_ids", [])),
        "type": "movie" if media_type == "movie" else "series",
    }
    work, created = Work.objects.update_or_create(
        external_id=item["id"],
        defaults={**defaults, "title": item.get("title") or item.get("name")}
    )
    return work
