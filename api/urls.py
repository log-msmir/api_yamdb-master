from django.urls import path

from .views import (TitleViewSet, GenreViewSet, CategoryViewSet,
                    UserViewSet, ReviewViewSet, CommentViewSet,
                    GetConfirmationCodeAPIView, GetJWTTokenAPIView,
                    api_root,)


auth_token = GetJWTTokenAPIView.as_view()
auth_email = GetConfirmationCodeAPIView.as_view()

comment_detail = CommentViewSet.as_view({
     'get': 'retrieve',
     'patch': 'update',
     'delete': 'destroy'},
                                        )

comment_list = CommentViewSet.as_view({
     'get': 'list',
     'post': 'create'},)

review_detail = ReviewViewSet.as_view({
     'get': 'retrieve',
     'patch': 'update',
     'delete': 'destroy'},)

review_list = ReviewViewSet.as_view({
     'get': 'list',
     'post': 'create'},)

user_info = UserViewSet.as_view({
     'get': 'user_retrieve',
     'patch': 'user_update'},)

admin_detail = UserViewSet.as_view({
     'get': 'admin_retrieve',
     'delete': 'destroy',
     'patch': 'admin_update'},)

user_list = UserViewSet.as_view({
     'get': 'list',
     'post': 'create'},)

category_detail = CategoryViewSet.as_view({
     'delete': 'destroy'},)

category_list = CategoryViewSet.as_view({
     'get': 'list',
     'post': 'create'},)

genre_detail = GenreViewSet.as_view({
     'delete': 'destroy',
     'get':'retrieve'},)

genre_list = GenreViewSet.as_view({
     'get':'list',
     'post': 'create'},)

title_detail = TitleViewSet.as_view({
     'get': 'retrieve',
     'patch': 'update',
     'delete': 'destroy'},)

title_list = TitleViewSet.as_view({
     'get': 'list',
     'post': 'create'},)


urlpatterns = [
    path('auth/token/',
         auth_token, name='auth_token'),
    path('auth/email/',
         auth_email, name='auth_email'),
    path('titles/<int:title_id>/reviews/<int:review_id>/comments/<int:comment_id>/',
         comment_detail, name='comment_detail'),
    path('titles/<int:title_id>/reviews/<int:review_id>/comments/',
         comment_list, name='comment_list'),
    path('titles/<int:title_id>/reviews/<int:review_id>/',
         review_detail, name='review_detail'),
    path('titles/<int:title_id>/reviews/',
         review_list, name='review_list'),
    path('users/me/',
         user_info, name='user_info'),
    path('users/<slug:username>/',
         admin_detail, name='admin_detail'),
    path('users/',
         user_list, name='user_list'),
    path('categories/<slug:slug>/',
         category_detail, name='category_detail'),
    path('categories/',
         category_list, name='category_list'),
    path('genres/<slug:slug>/',
         genre_detail, name='genre_detail'),
    path('genres/',
         genre_list, name='genre_list'),
    path('titles/<int:title_id>/',
         title_detail, name='title_detail'),
    path('titles/',
         title_list, name='title_list'),
    path('', api_root),
]
