from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_framework.reverse import reverse

from .models import User, Title, Category, Comment, Genre, Review
from .mixins import ValidationMixin
from .utils import generate_confirmation_code


"""  Тестовые классы  """


class GenreListingField(serializers.RelatedField):

    def to_representation(self, value):
        return {'name': value.name, 'slug':value.slug}

    def get_queryset(self):
        return Genre.objects.all()


"""  <<< The end >>>  """


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        extra_kwargs = {'name': {'validators':[]}}


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')
        extra_kwargs = {'name': {'validators':[]}}


class TitleSerializer(serializers.ModelSerializer, ValidationMixin):
    genre = serializers.SerializerMethodField(read_only=False)
    category = serializers.SerializerMethodField(read_only=False, required=False)
    rating = serializers.SerializerMethodField()
    #genre = GenreListingField(many=True, required=False)
    url = serializers.HyperlinkedIdentityField(view_name='title_detail',
                                               lookup_field='pk',
                                               lookup_url_kwarg='title_id')
    test_url = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category', 'url', 'test_url')

    def get_test_url(self, obj):
        return reverse('title_detail', kwargs={'title_id': obj.pk}, request=self.context['request'])

    def get_genre(self, obj):
        genres = {'genre':[]}
        for genre in obj.genre.values():
            genres['genre'].append({'name': genre['name'], 'slug': genre['slug']})
        return genres

    def get_category(self, obj):
        category = {}
        category['name'] = obj.category.name
        category['slug'] = obj.category.slug
        return category

    def get_rating(self, obj):  # obj = Title qs
        rating = obj.reviews.all().aggregate(Avg('score'))['score__avg']
        """  Return a dict:
        "rating": {
                "score__avg": 10.0
            },
        """
        if rating:
            return float("{:.1f}".format(rating))
        else:
            return None

    def create(self, validated_data):
        payload = {k:v for k,v in self.context['request'].data.items()
                   if k in self.get_fields().keys()}

        rating = payload.get('rating', None)
        if rating:
            raise ParseError(detail={'error': 'Rating is not a writable field'})

        cat_filter = payload.get('category', None)
        genres = payload.get('genre', None)
        if cat_filter:
            category = get_object_or_404(Category, slug__iexact=cat_filter)
            title = Title(category=category, **validated_data)
            title.save()
        else:
            title = Title(**validated_data)
            title.save()
        if genres:
            for genre in genres:
                genre_obj = get_object_or_404(Genre, slug__iexact=genre)
                title.genre.add(genre_obj)

        return title

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.year = validated_data.get('year', instance.year)
        instance.description = validated_data.get('description', instance.description)

        category = validated_data.get('category', None)
        if category:
            try:
                cat = Category.objects.get(**category)
            except:
                raise ParseError(detail={'error': 'Category is not exist'})
            instance.category = cat

        genres = validated_data.get('genre', None)
        #TODO genres полное обновление жанра (PATCh)
        if genres:
            for genre in genres:
                try:
                    genre_obj = Genre.objects.get(**genre)
                except:
                    raise ParseError(detail={'erorr': 'Genre is not exist'})
                instance.genre.add(genre_obj)
        self.check_data(instance)
        instance.save()

        return instance


class UserSerializer(serializers.ModelSerializer, ValidationMixin):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'bio', 'email', 'role')

    def create(self, validated_data):
        user = User(**validated_data)
        confirmation_code = generate_confirmation_code()
        user.set_password(confirmation_code)
        self.check_data(user)
        user.save()

        send_mail(subject='YaMDB verify your email',
                  message=f'Confirmation code: {confirmation_code}',
                  from_email=settings.DEFAULT_FROM_EMAIL,
                  recipient_list=[user.email,])

        return user

    def update(self, instance, validated_data):
        role = self.context['request'].user.role

        if role == 'admin':
            instance.role = validated_data.get('role', instance.role)

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.bio = validated_data.get('bio', instance.bio)

        self.check_data(instance)
        instance.save()

        return instance


class ReviewSerializer(serializers.ModelSerializer, ValidationMixin):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def create(self, validated_data):
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        title = get_object_or_404(Title, pk=title_id)
        author = self.context['request'].user
        if not author.pk:
            raise ParseError(detail={'error': 'Author is not exist'})
        #review = Review.objects.create(author=author, title=title, **validated_data)
        review = Review(author=author, title=title, **validated_data)
        self.check_data(review)
        review.save()

        return review

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.score = validated_data.get('score', instance.score)
        self.check_data(instance)
        instance.save()

        return instance


class CommentSerializer(serializers.ModelSerializer, ValidationMixin):
    author = serializers.ReadOnlyField(source='author.username')
    id = serializers.ReadOnlyField()
    pub_date = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')

    def create(self, validated_data):
        #TODO Использовать perform_create для заполнения validated_data во view
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        review_id = self.context['request'].parser_context['kwargs']['review_id']
        review = get_object_or_404(Review, pk=review_id, title=title_id)
        author = self.context['request'].user
        if not author.pk:
            raise ParseError(detail={'error': 'Author is not exist'})
        #comment = Comment.objects.create(author=author, review=review, **validated_data)
        comment = Comment(author=author, review=review, **validated_data)
        self.check_data(comment)
        comment.save()

        return comment

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        self.check_data(instance)
        instance.save()

        return instance
