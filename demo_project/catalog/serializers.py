from rest_framework import serializers
from .models import Work, Review, ListEntry
from users.models import Profile

class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    work = serializers.PrimaryKeyRelatedField(queryset=Work.objects.all())

    class Meta:
        model = Review
        fields = ['id', 'work', 'user', 'text', 'rating', 'created_at']
        read_only_fields = ['created_at']

class ListEntrySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    work = serializers.PrimaryKeyRelatedField(queryset=Work.objects.all())

    class Meta:
        model = ListEntry
        fields = ['id', 'work', 'user', 'status', 'added_at']
        read_only_fields = ['added_at']

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'avatar', 'description']
