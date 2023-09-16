from django.shortcuts import get_object_or_404
from rest_framework import exceptions, filters, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .permissions import IsAuthenticatedOrAuthorOrReadOnly
from .serializers import (
    CommentSerializer, FollowSerializer, GroupSerializer, PostSerializer
)
from posts.models import Follow, Group, Post, User


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrAuthorOrReadOnly,)

    def get_post_for_comments(self):
        return get_object_or_404(Post, pk=self.kwargs['post_id'])

    def get_queryset(self):
        post = self.get_post_for_comments()
        return post.comments

    def perform_create(self, serializer):
        post = self.get_post_for_comments()
        serializer.save(
            author=self.request.user,
            post=post
        )


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    http_method_names = ('get', 'post', 'head')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        return self.request.user.users

    def perform_create(self, serializer):
        following = get_object_or_404(
            User, username=self.request.data['following']
        )
        if (
            Follow.objects.filter(
                user=self.request.user, following=following).exists()
            or following == self.request.user
        ):
            raise exceptions.ValidationError
        serializer.save(
            user=self.request.user,
            following=following
        )
