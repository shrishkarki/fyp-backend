from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import permissions
from rest_framework import viewsets

from .models import Blog, Category, Comment, Like
from .serializers import BlogListSerializer, BlogDetailSerializer, CommentSerializer, CategorySerializer
from .paginations import CustomLimitOffsetPagination

# Customizing the permissions model
SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class BlogListView(APIView, CustomLimitOffsetPagination):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        category = request.query_params.get('category', None)
        username = request.query_params.get('username', None)
        if category and username:
            queryset = Blog.objects.filter(category__name=category, author__username=username)
        elif category:
            queryset = Blog.objects.filter(category__name=category)
        elif username:
            queryset = Blog.objects.filter(author__username=username)
        else:
            queryset = Blog.objects.all()
        blogs = self.paginate_queryset(queryset, request, view=self)
        serializer = BlogListSerializer(blogs, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

        # if category:
        #     blogs = Blog.objects.filter(category__name=category)
        # else:
        #     blogs = Blog.objects.all()
        # blog_page = self.paginate_queryset(blogs, request, view=self)
        # serializer = BlogListSerializer(blog_page, many=True)
        
        # return self.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = BlogDetailSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlogDetailView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, slug):
        # getting the blog instance from the slug
        # if the blog is not found, raise an exception
        try:
            blog = Blog.objects.get(slug=slug)
        except Blog.DoesNotExist:
            return Response(
                {'error': 'Blog with slug {} does not exist'.format(slug)},
                status=status.HTTP_404_NOT_FOUND)
        serializer = BlogDetailSerializer(blog, context={'request': request})
        return Response(serializer.data)

        # view to update the blog
    def put(self, request, slug):
        # getting the blog from the slug
        # raising an exception if the blog does not exist
        try:
            blog = Blog.objects.get(slug=slug)
        except Blog.DoesNotExist:
            return Response(
                {'error': 'Blog with slug {} does not exist'.format(slug)},
                status=status.HTTP_404_NOT_FOUND)
        
        # checking if the user is the author of the blog
        if blog.author != request.user:
            return Response(
                {'error': 'You are not the author of the blog'},
                status=status.HTTP_403_FORBIDDEN)

        # passing the request.data to the serializer 
        serializer = BlogDetailSerializer(blog, data=request.data, context={'request': request})

        # checking if the serializer is valid
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # view for deleting the blog
    def delete(self, request, slug):
        try:
            blog = Blog.objects.get(slug=slug)
        except Blog.DoesNotExist:
            return Response(
                {'error': 'Blog with slug {} does not exist'.format(slug)},
                status=status.HTTP_404_NOT_FOUND)

        # checking if the user is the author of the blog
        if blog.author == request.user:
            blog.delete()
        else:
            raise AuthenticationFailed('You are not the author of the blog')
        return Response(
            {'message': f'Blog "{blog.title}" has been deleted'},
            status=status.HTTP_204_NO_CONTENT
            )



class BlogLikeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, slug):
        # getting the blog from the slug
        # raising an exception if the blog does not exist
        try:
            blog = Blog.objects.get(slug=slug)
        except Blog.DoesNotExist:
            return Response(
                {'error': 'Blog with slug {} does not exist'.format(slug)},
                status=status.HTTP_404_NOT_FOUND)

        # checking if the user has already liked the blog
        # disliking the blog if the user has already liked it
        if Like.objects.filter(blog=blog, account=request.user).exists():
            like = Like.objects.get(blog=blog, account=request.user)
            like.delete()
            return Response(
                {'liked': False},
                status=status.HTTP_200_OK)

        # liking the blog if the user has not liked it yet
        like = Like.objects.create(blog=blog, account=request.user)
        like.save()
        return Response(
            {'liked': True},
            status=status.HTTP_200_OK)


class BlogCommentView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, slug):
        # getting the blog from the slug
        # raising an exception if the blog does not exist
        try:
            blog = Blog.objects.get(slug=slug)
        except Blog.DoesNotExist:
            return Response(
                {'error': 'Blog with slug {} does not exist'.format(slug)},
                status=status.HTTP_404_NOT_FOUND)

        # passing the request.data to the serializer
        serializer = CommentSerializer(data=request.data, context={'request': request})
        
        # checking if the serializer is valid
        if serializer.is_valid():
            serializer.save(blog=blog, account=request.user)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            



