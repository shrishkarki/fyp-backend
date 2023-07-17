from unicodedata import category, name
from rest_framework import serializers

from .models import Blog, Image, Category, Comment, Like

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Image
        fields = ('image_url',)

    def get_image_url(self, obj):
        request = self.context.get('request')
        photo_url = obj.image.url
        return request.build_absolute_uri(photo_url)


"""
Serailizer for the Comment model
"""
class CommentSerializer(serializers.ModelSerializer):
    commented_by = serializers.ReadOnlyField(source='account.name')
    class Meta:
        model = Comment
        fields = ('comment', 'commented_at', 'commented_by')

        read_only_fields = ('commented_at', 'commented_by')


"""
Serializer for the Likes model
"""
class LikeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='account.name')
    class Meta:
        model = Like
        fields = ('name', 'liked_at')


"""
List serializer for the Blog model
"""
class BlogListSerializer(serializers.ModelSerializer):
    # adding image field to the serializer
    images = ImageSerializer(many=True, required=False)
    author = serializers.ReadOnlyField(source='author.name')
    comment_count = serializers.ReadOnlyField(source='comments.count')
    like_count = serializers.ReadOnlyField(source='likes.count')
    category = serializers.CharField(source='category.name')
    
    class Meta:
        model = Blog
        fields = (
            'id',
            'slug',
            'category',
            'title', 
            'author', 
            'pub_date', 
            'body', 
            'images',
            'author',
            'comment_count',
            'like_count',
        )
        

"""
Serializer for the detail view of the Blog model
"""
class BlogDetailSerializer(BlogListSerializer):
    images = ImageSerializer(many=True, required=False)
    author = serializers.ReadOnlyField(source='author.name')
    comment_count = serializers.ReadOnlyField(source='comments.count')
    like_count = serializers.ReadOnlyField(source='likes.count')
    category = serializers.CharField(source='category.name')
    comments = CommentSerializer(many=True, required=False)
    # likes = LikeSerializer(many=True, required=False)

    class Meta:
        model = Blog
        fields = (
            'id',
            'slug',
            'category',
            'title', 
            'author', 
            'pub_date', 
            'body', 
            'images',
            'author',
            'comment_count',
            'like_count',
            'comments',
            # 'likes',
        )
        read_only_fields = ('id', 'pub_date','comment_count','like_count','comments')

    def validate_category(self, value):
        try:
            Category.objects.get(name=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError('Category does not exist')
        return value


    def create(self, validated_data):
        # poping the images data from the request data

        # poping the category data from the validated data
        category = validated_data.pop('category')['name']

        # creating the blog instance
        blog = Blog.objects.create(**validated_data, category=Category.objects.get(name=category))
        # return blog
        blog.save()

        # adding images to the blog
        
        if 'images' in self.context['request'].data:
            images_data = self.context['request'].data.pop('images')
            for image_data in images_data:
                print(image_data)
                Image.objects.create(blog=blog, image=image_data)
                
        return blog


    def update(self, instance, validated_data):
        images_data = self.context['request'].data.pop('images')
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)

        category = validated_data.get('category', instance.category)['name']
        instance.category = Category.objects.get(name=category)

        instance.save()
        for image_data in images_data:
            Image.objects.update_or_create(blog=instance, image = image_data)
        return instance