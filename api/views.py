from django.shortcuts import get_object_or_404, get_list_or_404

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler
from drf_yasg.utils import swagger_auto_schema


from .serializers import (TitleSerializer, GenreSerializer, CategorySerializer, UserSerializer,
                          ReviewSerializer, CommentSerializer)
from .models import Title, Category, Genre, User, Review, Comment
from .mixins import FilterMixin, SlugDeleteMixin, ValidationMixin
from .utils import generate_confirmation_code
from .permissions import (ReviewPermission, CommentPermission, UserPermission, CategoryPermission,
                          GenrePermission, TitlePermission)


class TestAPIView(generics.RetrieveAPIView):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    lookup_url_kwarg = 'title_id'


@api_view(['GET'])
def test(request):
    return Response('FFF#3')


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'titles': reverse('titles', request=request, format=format)
    })


class GetConfirmationCodeAPIView(APIView, ValidationMixin):
    #  Подумать над защитой от спама
    permission_classes = (AllowAny,)

    def post(self, request):
        user_email = request.data.get('email', None)
        if not user_email:
            return Response({'error': 'Email is required'})
        user = User.objects.filter(email=user_email)
        confirmation_code = generate_confirmation_code()
        if not user:
            username = user_email.split('@')[0]
            user = User(email=user_email, username=username)
        else:
            user = get_object_or_404(User, email=user_email)

        user.set_password(confirmation_code)
        self.check_data(user)
        user.save()

        """  return Response({'error': 'Email is already used'}, status=status.HTTP_400_BAD_REQUEST)
         send_mail(subject='YaMDB verify your email',
                 message=f'Confirmation code: {confirmation_code}',
                 from_email=settings.DEFAULT_FROM_EMAIL,
                 recipient_list=[user_email,])
        return Response({'OK': f'Confirmation code was send to {user_email} {confirmation_code}'})"""
        """Для тестов закомментировать отправку email и респонс"""
        return Response({'confirmation_code':f'{confirmation_code}'})


class GetJWTTokenAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        data = {}
        data['email'] = request.data.get('email', None)
        data['confirmation_code'] = request.data.get('confirmation_code', None)

        errors = {k:'is not defined' for k,v in data.items() if v is None}
        if errors:
            return Response({'error': errors.items()}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = get_object_or_404(User, email=data['email'])
            if user.check_password(data['confirmation_code']):
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                return Response({'token': token})
            else:
                return Response({'error': 'Wrong confirmation code'})


class TitleViewSet(ModelViewSet):
    serializer_class = TitleSerializer
    queryset = Title.objects.all()
    required_fields = ['name']
    permission_classes = (TitlePermission,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter(request)
        serializer = TitleSerializer(queryset, many=True, context={'request': request})

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = TitleSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, title_id, *args, **kwargs):
        title = get_object_or_404(Title, pk=title_id)
        serializer = TitleSerializer(title, context={'request':request})

        return Response(serializer.data)

    def update(self, request, title_id, *args, **kwargs):
        instance = get_object_or_404(Title, pk=title_id)
        self.check_object_permissions(self.request, instance)
        serializer = TitleSerializer(instance=instance, data=request.data, partial=True,
                                     context={'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, title_id, *args, **kwargs):
        title = get_object_or_404(Title, pk=title_id)
        self.check_object_permissions(self.request, title)
        title.genre.clear()  # Remove m2m
        title.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def filter(self, request):
        search_fields = {
            'category__slug__iexact': request.GET.get('category', None),
            'genre__slug__iexact': request.GET.get('genre', None),
            'name__icontains': request.GET.get('name', None),
            'year': request.GET.get('year', None),}

        query = {k:v for k,v in search_fields.items() if v}
        if query:
            #  Протестировать
            queryset = get_list_or_404(Title, **query)
        else:
            queryset = self.get_queryset()
        return queryset


class GenreViewSet(FilterMixin, SlugDeleteMixin, ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (GenrePermission,)
    search_fields = ['name', 'slug']


class CategoryViewSet(FilterMixin, SlugDeleteMixin, ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ['name', 'slug']
    permission_classes = (CategoryPermission,)
    lookup_field = 'slug'


class UserViewSet(FilterMixin, ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ['username']
    permission_classes = (UserPermission,)

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def admin_retrieve(self, request, username=None, *args, **kwargs):
        user = get_object_or_404(User, username__iexact=username)
        self.check_object_permissions(self.request, user)
        serializer = UserSerializer(user)

        return Response(serializer.data)

    def destroy(self, request, username=None, *args, **kwargs):
        user = get_object_or_404(User, username__iexact=username)
        self.check_object_permissions(self.request, user)
        user.delete()

        return Response({'OK': f'User was deleted - {username}'}, status=status.HTTP_204_NO_CONTENT)

    def admin_update(self, request, username=None, *args, **kwargs):
        serializer = self.save_user_changes(username=username, request=request)

        return Response(serializer.data)

    #  Отдаем 404ю из-за попытки взять несуществующий объект, исправить ли?
    def user_update(self, request, *args, **kwargs):
        serializer = self.save_user_changes(username=request.user, request=request)

        return Response(serializer.data)

    def save_user_changes(self, username, request):
        user = get_object_or_404(User, username__iexact=username)
        self.check_object_permissions(self.request, user)
        serializer = UserSerializer(instance=user, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return serializer

    def user_retrieve(self, request, *args, **kwargs):
        username = request.user
        user = get_object_or_404(User, username__iexact=username)
        serializer = UserSerializer(user)

        return Response(serializer.data)


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (ReviewPermission,)

    def list(self, request, title_id, *args, **kwargs):
        queryset = get_list_or_404(Review, title=title_id)
        serializer = ReviewSerializer(queryset, many=True, context={'request':request})

        return Response(serializer.data)

    def create(self, request, title_id, *args, **kwargs):
        serializer = ReviewSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, title_id, review_id, *args, **kwargs):
        review = get_object_or_404(Review, title=title_id, pk=review_id)
        serializer = ReviewSerializer(review)

        return Response(serializer.data)

    def update(self, request, title_id, review_id, *args, **kwargs):
        instance = get_object_or_404(Review, title=title_id, pk=review_id)
        self.check_object_permissions(self.request, instance)
        serializer = ReviewSerializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def destroy(self, request, title_id, review_id, *args, **kwargs):
        review = get_object_or_404(Review, title=title_id, pk=review_id)
        self.check_object_permissions(self.request, review)
        review.delete()

        return Response({'OK': f'Review # {review_id} was deleted'},
                        status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (CommentPermission,)

    @swagger_auto_schema(tags=['Comment'],
                         operation_description='Получить список всех комментариев',
                         operation_id='Получить список всех комментариев',)
    def list(self, request, title_id, review_id, *args, **kwargs):
        """List of comments"""
        comments = get_list_or_404(Comment, review=review_id, review__title=title_id)
        serializer = CommentSerializer(comments, many=True)

        return Response(serializer.data)

    @swagger_auto_schema(tags=['Comment'], operation_description='Create')
    def create(self, request, title_id, review_id, *args, **kwargs):
        serializer = CommentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, title_id, review_id, comment_id, *args, **kwargs):
        comment = get_object_or_404(Comment,
                                    pk=comment_id, review=review_id, review__title=title_id)
        serializer = CommentSerializer(comment)

        return Response(serializer.data)

    def update(self, request, title_id, review_id, comment_id, *args, **kwargs):
        instance = get_object_or_404(Comment,
                                     pk=comment_id, review=review_id, review__title=title_id)
        self.check_object_permissions(self.request, instance)
        serializer = CommentSerializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, title_id, review_id, comment_id, *args, **kwargs):
        comment = get_object_or_404(Comment,
                                    pk=comment_id, review=review_id, review__title=title_id)
        self.check_object_permissions(self.request, comment)
        comment.delete()

        return Response({'OK': 'Comment was deleted'}, status=status.HTTP_204_NO_CONTENT)
