from datetime import timedelta, date
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.db.models.functions import Lower
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Profile
from .forms import RegisterForm as UserCreationForm, LoginForm as AuthenticationForm, UserUpdateForm, ProfileUpdateForm
from catalog.models import Work, Review, ListEntry, Follow
from catalog.forms import ListEntryForm

User = get_user_model()

def index_view(request):
    reviews = (
        Review.objects
              .select_related('user','work')
              .annotate(vote_sum=Coalesce(Sum('votes__value'), 0))
              .order_by('-created_at')
    )
    popular_items = Work.objects.order_by('-rating')[:10]
    page_num = request.GET.get('page', 1)
    paginator = Paginator(reviews, 5)    
    reviews_page = paginator.get_page(page_num)
    return render(request, 'index.html', {
        'activities': [],      
        'reviews': reviews_page,
        'popular_items': popular_items,
    })

@login_required
def mylist_view(request):
    work_type = request.GET.get('type', '') or ''
    genre     = request.GET.get('genre', '').strip()

    entries_qs = ListEntry.objects.filter(user=request.user) \
                                  .select_related('work') \
                                  .order_by('-added_at')

    filtered = [
        e for e in entries_qs
        if (not work_type or e.work.type == work_type)
        and (not genre     or genre.lower() in (e.work.genre or '').lower())
    ]
    page_my = request.GET.get('my_page', 1)
    paginator_my = Paginator(entries_qs, 6)    
    entries_page = paginator_my.get_page(page_my)

    if request.method == 'POST':
        form = ListEntryForm(request.POST, user=request.user)

        form.instance.user = request.user
        if form.is_valid():
            form.save()
            return redirect('mylist')
    else:

        form = ListEntryForm(user=request.user, instance=ListEntry(user=request.user))

    page_my = request.GET.get('my_page', 1)
    paginator_my = Paginator(filtered, 6)
    entries_page = paginator_my.get_page(page_my)

    return render(request, 'mylist.html', {
        'mylist': entries_page,
        'form': form,
        'type_choices': Work.TYPE_CHOICES,
        'current_type': work_type,
        'current_genre': genre,
    })

@login_required
def profile_view(request, username=None):
    if username is None:
        user = request.user
    else:
        user = get_object_or_404(User, username=username)
    stats = {
        'films':  Review.objects.filter(user=request.user, work__type=Work.MOVIE).count(),
        'series': Review.objects.filter(user=request.user, work__type=Work.SERIES).count(),
        'books':  Review.objects.filter(user=request.user, work__type=Work.BOOK).count(),
    }
    favorites = [
        entry.work
        for entry in ListEntry.objects.filter(
            user=request.user,
            status=ListEntry.STATUS_WANT
        ).select_related('work')
    ]
    description = ''

    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = Follow.objects.filter(
            follower=request.user,
            followed=user
        ).exists()

    return render(request, 'profile.html', {
        'stats': stats,
        'favorites': favorites,
        'description': description,
        'user': user,
        'is_following': is_following,  
    })

@login_required
def profile_view_by_username(request, username):
    user_obj = get_object_or_404(User, username=username)
    stats = { ... }          
    favorites = [ ... ]       
    description = ''

    is_following = Follow.objects.filter(
        follower=request.user.profile,
        followed=user_obj.profile
    ).exists()
    return render(request, 'profile.html', {
        'user': user_obj,
        'stats': stats,
        'favorites': favorites,
        'description': description,
        'is_following': is_following,
    })

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

def search_view(request):
    q = request.GET.get('q', '').strip()
    review_results = []
    work_results = []

    if q:
        q_fold = q.casefold()  


        for rev in Review.objects.select_related('user', 'work').order_by('-created_at'):
            text_fold  = rev.text.casefold()
            title_fold = rev.work.title.casefold()
            if q_fold in text_fold or q_fold in title_fold:
                review_results.append(rev)


        for work in Work.objects.order_by('-rating'):
            if q_fold in work.title.casefold():
                work_results.append(work)

    return render(request, 'search.html', {
        'query': q,
        'review_results': review_results,
        'work_results': work_results,
    })

@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')  
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'profile_edit.html', {
        'u_form': u_form,
        'p_form': p_form,
    })

@login_required
def feed_view(request):

    follows = request.user.profile.following.all()

    reviews = Review.objects.filter(
        user__profile__in=follows
    ).select_related('user','work').order_by('-created_at')

    page = request.GET.get('page', 1)
    paginator = Paginator(reviews, 5)
    reviews_page = paginator.get_page(page)

    return render(request, 'feed.html', {
        'reviews': reviews_page,
    })

@login_required
def toggle_follow(request, username):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({'error': 'Нельзя подписаться на себя'}, status=400)

    follow_obj, created = Follow.objects.get_or_create(
        follower=request.user,
        followed=target
    )
    if not created:
        follow_obj.delete()
        following = False
    else:
        following = True

    return JsonResponse({'following': following})
