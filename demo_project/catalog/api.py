from rest_framework import viewsets, permissions
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Work, Review, ListEntry
from users.models import Profile
from .serializers import WorkSerializer, ReviewSerializer, ListEntrySerializer, ProfileSerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class WorkViewSet(viewsets.ModelViewSet):
    queryset = Work.objects.all().order_by('title')
    serializer_class = WorkSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        qs = super().get_queryset()
        q  = self.request.query_params.get('search', '').strip()
        if q:
            q_fold = q.casefold()
            qs = [w for w in qs if q_fold in w.title.casefold()]
        return qs

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user','work').all().order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ListEntryViewSet(viewsets.ModelViewSet):
    queryset = ListEntry.objects.select_related('user','work').all().order_by('-added_at')
    serializer_class = ListEntrySerializer
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reorder(self, request):
        order = request.data.get('order', [])
        for idx, entry_id in enumerate(order, start=1):
            ListEntry.objects.filter(pk=entry_id, user=request.user) \
                             .update(position=idx)
        return Response({'status':'ok'})

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
