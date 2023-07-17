from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BlogListView,
    BlogDetailView,
    BlogLikeView,
    BlogCommentView,
    CategoryViewSet
)


urlpatterns = [
    # listing all the blogs
    path('', BlogListView.as_view(), name='blog-list'),

    # detail view of a blog
    path('b/<slug:slug>/', BlogDetailView.as_view(), name='blog-detail'),

    # liking a blog
    path('b/<slug:slug>/like/', BlogLikeView.as_view(), name='blog-like'),

    # commenting on a blog
    path('b/<slug:slug>/comment/', BlogCommentView.as_view(), name='blog-comment'),
]

router = DefaultRouter()
router.register('categories', CategoryViewSet)

urlpatterns += router.urls