from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Sum, Value, Count, Avg
from django.db.models.functions import Coalesce
from django.views.decorators.http import require_http_methods
from catalog.models import Work, ListEntry, Review
from catalog.forms import ReviewForm
from .models import Review, ReviewVote, Comment, ListEntry, Activity, Follow
from .forms  import CommentForm, ListEntryForm
from .services import tmdb_search, tmdb_fetch_and_upsert, gbooks_search, gbooks_fetch_and_upsert, tmdb_external_results
from .tmdb import search_tmdb, upsert_work

def works_list_view(request):
    work_type = request.GET.get('type', '') or ''
    genre     = request.GET.get('genre', '').strip()

    qs = Work.objects.of_type(work_type) \
                     .of_genre(genre) \
                     .order_by('title')
    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 12)
    works = paginator.get_page(page)

    return render(request, 'works_list.html', {
        'works': works,
        'type_choices': Work.TYPE_CHOICES,
        'current_type': work_type,
        'current_genre': genre,
    })

@login_required
def work_detail_view(request, pk):
    work = get_object_or_404(Work, pk=pk)
    reviews = (
    work.reviews
        .select_related('user')
        .annotate(vote_sum=Coalesce(Sum('votes__value'), 0))
        .order_by('-created_at')
    )
    in_list = ListEntry.objects.filter(user=request.user, work=work).exists()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.user = request.user
            rev.work = work
            rev.save()
            return redirect('work_detail', pk=work.pk)
    else:
        form = ReviewForm()
    comment_form = CommentForm()

    return render(request, 'work_detail.html', {
        'work': work,
        'reviews': reviews,
        'form': form,
        'in_list': in_list,
        'comment_form': comment_form,
    })

@login_required
def toggle_list_entry(request, pk):
    work = get_object_or_404(Work, pk=pk)
    entry, created = ListEntry.objects.get_or_create(
        user=request.user,
        work=work,
        defaults={'status': ListEntry.STATUS_WANT}
    )
    if not created:
        entry.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
           'in_list': created,
           'work': {
               'id': work.id,
               'title': work.title,
           }
       })
    return redirect('work_detail', pk=pk)

@login_required
def edit_review_view(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('work_detail', pk=review.work.pk)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'edit_review.html', {
        'form': form,
        'review': review,
    })

@login_required
def delete_review_view(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    work_pk = review.work.pk
    if request.method == 'POST':
        review.delete()
        return redirect('work_detail', pk=work_pk)
    return render(request, 'delete_review.html', {
        'review': review,
    })

@login_required
@require_POST
def vote_review(request):
    review_id = request.POST.get('review')
    val = request.POST.get('value')
    try:
        v = int(val)
        assert v in (1, -1)
    except:
        return JsonResponse({'error': 'Неверное значение голоса'}, status=400)

    review = get_object_or_404(Review, pk=review_id)
    vote, created = ReviewVote.objects.get_or_create(
        user=request.user,
        review=review,
        defaults={'value': v}
    )
    if not created:
        if vote.value == v:
            vote.delete()
        else:
            vote.value = v
            vote.save()

    score = review.votes.aggregate(
        score=Coalesce(Sum('value'), 0)
    )['score']
    return JsonResponse({'score': score})

@login_required
def add_comment(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.user   = request.user
            c.review = review
            parent_id = request.POST.get('parent_id')
            if parent_id:
                c.parent = get_object_or_404(Comment, pk=parent_id)
            c.save()
    return redirect('work_detail', pk=review.work.pk)

@login_required
@require_http_methods(["GET", "POST"])
def edit_list_entry(request, pk):
    entry = get_object_or_404(ListEntry, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ListEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'status': entry.get_status_display(),
                'score': entry.score or '',
                'progress': entry.progress or '',
                'favorite': entry.favorite,
            })
        return JsonResponse({'errors': form.errors}, status=400)

    else:
        form = ListEntryForm(instance=entry)
        html = render(request, 'edit_list_entry_form.html', {
            'form': form, 'entry': entry
        }).content.decode('utf-8')
        return JsonResponse({'html': html})
    
@login_required
def activity_feed(request):
    mode     = request.GET.get('mode', 'all')
    page_num = request.GET.get('page', 1)

    qs = Activity.objects.select_related('user').order_by('-timestamp')
    if mode == 'following':
        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('followed_id', flat=True)
        qs = qs.filter(user_id__in=following_ids)

    paginator = Paginator(qs, 10)
    page      = paginator.get_page(page_num)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = []
        for act in page:
            data.append({
                'user':        act.user.username,
                'description': act.description,
                'timestamp':   act.timestamp.strftime('%-d %b %Y, %H:%M'),
            })
        return JsonResponse({
            'activities': data,
            'has_next':   page.has_next(),
            'next_page':  page.next_page_number() if page.has_next() else None,
        })

    return render(request, 'activity.html', {
        'activities': page,
        'mode':       mode,
    })

def index_view(request):

    mode = request.GET.get('mode', 'all')


    qs = Activity.objects.select_related('user').order_by('-timestamp')
    if mode == 'following' and request.user.is_authenticated:

        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('followed_id', flat=True)
        qs = qs.filter(user_id__in=following_ids)


    page_number = request.GET.get('page_activities', 1)
    paginator = Paginator(qs, 10)
    activities = paginator.get_page(page_number)

    reviews_qs = (
        Review.objects
              .select_related('user', 'work')
              .annotate(vote_sum=Coalesce(Sum('votes__value'), Value(0)))
              .order_by('-created_at')
    )
    reviews = Paginator(reviews_qs, 5).get_page(request.GET.get('page_reviews', 1))


    popular_items = Work.objects.annotate(
        avg_score=Avg('list_entries__score'),   
        entries_count=Count('list_entries')      
    ).filter(
        entries_count__gt=0                     
    ).order_by(
        '-avg_score', '-entries_count'         
    )[:10]                                      


    return render(request, 'index.html', {
        'activities': activities,
        'mode': mode,
        'reviews': reviews,
        'popular_items': popular_items,
    })

@login_required
def api_import_movie(request):
    external_id = request.GET.get('id')    
    if not external_id:
        return JsonResponse({'error': 'no id'}, status=400)

    work = tmdb_fetch_and_upsert(external_id)  

    return JsonResponse({
        'id':    work.id,
        'title': work.title,
    })

@login_required
def api_search(request):
    q = request.GET.get("q", "").strip()
    media = request.GET.get("type", "movie")
    if not q:
        return JsonResponse({"results": []})
    results = []
    for item in search_tmdb(q, media):
        work = upsert_work(item, media)
        results.append({
            "id": work.pk,
            "title": work.title,
            "overview": work.overview,
            "poster": work.get_poster_url(),
        })
    return JsonResponse({"results": results})

@login_required
def external_search(request):
    """
    Отдаёт JSON { results: [ { id, title }, … ] }
    по TMDB-поиску (по фильмам и сериалам).
    """
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'results': []})

    try:
        items = tmdb_search(q)
    except Exception:
        return JsonResponse({'results': []}, status=503)

    results = []
    for item in items:
        if item['media_type'] not in ('movie', 'tv'):
            continue
        results.append({
            'id': f"{item['media_type']}:{item['id']}",
            'title': item.get('title') or item.get('name'),
        })

    return JsonResponse({'results': results})

@login_required
def api_import_book(request):
    gid = request.GET.get('id')
    work = gbooks_fetch_and_upsert(gid)
    return JsonResponse({'id': work.id, 'title': work.title})

@login_required
def external_search(request):
    q    = request.GET.get('q','').strip()
    kind = request.GET.get('type')
    if not q:
        return JsonResponse({'results': []})

    if kind == 'book':
        results = [
            {'id': item['id'], 'title': item['volumeInfo'].get('title')}
            for item in gbooks_search(q)
        ]
    else:
        results = tmdb_external_results(q, kind)

    return JsonResponse({'results': results})