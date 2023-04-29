from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse

from .models import User, Title, Category, Genre, Review


class ApiTest(APITestCase):
#TODO добавить anon
#TODO проверить фильтры
#TODO проработать 401 и 400 ошибки
#TODO отрефакторить это безобразие

    def setUp(self) -> None:
        self.user = User.objects.create(email='user@mail.ru',
                                        username='user',
                                        role='user')
        self.moderator = User.objects.create(email='moderator@mail.ru',
                                             username='moderator',
                                             role='moderator')
        self.admin = User.objects.create(email='admin@mail.ru',
                                         username='admin',
                                         role='admin')

        self.category = Category.objects.create(name='Тестовая категория',
                                                slug='test-category')
        self.genre = Genre.objects.create(name='Тестовый жанр',slug='test-genre')
        self.title = Title.objects.create(name='Заголовок', category=self.category)
        self.title.genre.add(self.genre)

        self.registraton()
    
    def registraton(self):#  Изменение инициализации получения токена
        client_user = APIClient()
        request_user = client_user.post(reverse('auth_email'),
                                        data={'email': self.user.email})
        self.assertEqual(request_user.status_code, 200)
        confirmation_code_user = request_user.data.get('confirmation_code')
        self.assertIsNotNone(confirmation_code_user)
        request_user = client_user.post(reverse('auth_token'),
                                        data={'email': self.user.email,
                                              'confirmation_code': confirmation_code_user})
        self.token_user = 'Bearer ' + request_user.data.get('token')

        client_moderator = APIClient()
        request_moderator = client_moderator.post(reverse('auth_email'),
                                                  data={'email': self.moderator.email})
        self.assertEqual(request_moderator.status_code, 200)
        confirmation_code_moderator = request_moderator.data.get('confirmation_code')
        self.assertIsNotNone(confirmation_code_moderator)
        request_moderator = client_moderator.post(reverse('auth_token'),
            data={'email': self.moderator.email, 'confirmation_code':confirmation_code_moderator})
        self.token_moderator = 'Bearer ' + request_moderator.data.get('token')

        client_admin = APIClient()
        request_admin = client_admin.post(reverse('auth_email'),
                                          data={'email': self.admin.email})
        self.assertEqual(request_admin.status_code, 200)
        confirmation_code_admin = request_admin.data.get('confirmation_code')
        self.assertIsNotNone(confirmation_code_admin)
        request_admin = client_admin.post(reverse('auth_token'),
                                          data={'email': self.admin.email,
                                                'confirmation_code': confirmation_code_admin})
        self.token_admin = 'Bearer ' + request_admin.data.get('token')
    """  Titles  """
    def test_user_title(self):
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_user)
        """  GET LIST  """
        request = user.get(reverse('title_list'))
        self.assertEqual(request.status_code, 200)

        """  POST LIST  """
        title_name = 'Тестируемый заголовок'
        request = user.post(reverse('title_list'), data={'name': title_name})
        self.assertEqual(request.status_code, 403)

        """  GET DETAIL  """
        request = user.get(reverse('title_detail', kwargs={'title_id':self.title.pk}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=self.title.name)
        self.assertContains(response=request, text=self.genre.name)
        self.assertContains(response=request, text=self.category.name)

        """  PATCH DETAIL  """
        request = user.patch(reverse('title_detail', kwargs={'title_id':self.title.pk}))
        self.assertEqual(request.status_code, 403)

        """  DELETE DETAIL  """
        request = user.delete(reverse('title_detail', kwargs={'title_id':self.title.pk}))
        self.assertEqual(request.status_code, 403)

    def test_moderator_title(self):
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_moderator)
        """  GET LIST  """
        request = user.get(reverse('title_list'))
        self.assertEqual(request.status_code, 200)

        """  POST LIST  """
        title_name = 'Тестируемый заголовок'
        request = user.post(reverse('title_list'), data={'name': title_name})
        self.assertEqual(request.status_code, 403)

        """  GET DETAIL  """
        request = user.get(reverse('title_detail', kwargs={'title_id':self.title.pk}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=self.title.name)
        self.assertContains(response=request, text=self.genre.name)
        self.assertContains(response=request, text=self.category.name)

        """  PATCH DETAIL  """
        request = user.patch(reverse('title_detail', kwargs={'title_id':self.title.pk}))
        self.assertEqual(request.status_code, 403)

        """  DELETE DETAIL  """
        request = user.delete(reverse('title_detail', kwargs={'title_id':self.title.pk}))
        self.assertEqual(request.status_code, 403)

    def test_anon_title(self):
        user = APIClient()
        """  GET LIST  """
        request = user.get(reverse('title_list'))
        self.assertEqual(request.status_code, 200)

        """  POST LIST  """
        title_name = 'Тестируемый заголовок'
        request = user.post(reverse('title_list'), data={'name': title_name})
        self.assertEqual(request.status_code, 403)

        """  GET DETAIL  """
        request = user.get(reverse('title_detail', kwargs={'title_id':self.title.pk}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=self.title.name)
        self.assertContains(response=request, text=self.genre.name)
        self.assertContains(response=request, text=self.category.name)

        """  PATCH DETAIL  """
        request = user.patch(reverse('title_detail', kwargs={'title_id':self.title.pk}))
        self.assertEqual(request.status_code, 403)

        """  DELETE DETAIL  """
        request = user.delete(reverse('title_detail', kwargs={'title_id':self.title.pk}))
        self.assertEqual(request.status_code, 403)

    def test_admin_title(self):#  Образец
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_admin)
        """  GET LIST  """
        request = user.get(reverse('title_list'))
        self.assertEqual(request.status_code, 200)

        """  POST LIST  """
        title_name = 'Тестируемый заголовок'
        genre_default = 'Без жанра'
        category_default = 'Без категории'
        request = user.post(reverse('title_list'), data={'name': title_name})
        self.assertEqual(request.status_code, 201)
        title_id = request.data['id']

        """  GET DETAIL  """
        request = user.get(reverse('title_detail', kwargs={'title_id':title_id}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=title_name)
        self.assertContains(response=request, text=genre_default)
        self.assertContains(response=request, text=category_default)

        """  PATCH DETAIL  """
        title_name = 'Тестирование PATCH'
        request = user.patch(reverse('title_detail',
                                     kwargs={'title_id':title_id}),
                                     data={'name': title_name})
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=title_name)

        """  DELETE DETAIL  """
        request = user.delete(reverse('title_detail', kwargs={'title_id':title_id}))
        self.assertEqual(request.status_code, 204)
        request = user.get(reverse('title_detail', kwargs={'title_id':title_id}))
        self.assertEqual(request.status_code, 404)
    """  Genres  """
    def test_admin_genre(self):#  Образец
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_admin)
        """  Genre LIST  """
        request = user.get(reverse('genre_list'))
        self.assertEqual(request.status_code, 200)

        """  Genre POST  """
        genre_name = 'Авадакедабра'
        genre_slug = 'avadakedabra'
        request = user.post(reverse('genre_list'), data={'name': genre_name, 'slug': genre_slug})
        self.assertEqual(request.status_code, 201)
        request = user.get(reverse('genre_list'))
        self.assertContains(response=request, text=genre_name)
        self.assertContains(response=request, text=genre_slug)

        """  Genre DELETE  """
        request = user.delete(reverse('genre_detail', kwargs={'slug': genre_slug}),
                              data={'name': genre_name, 'slug': genre_slug})
        self.assertEqual(request.status_code, 204)
        request = user.get(reverse('genre_list'))
        self.assertNotContains(response=request, text=genre_name)
        self.assertNotContains(response=request, text=genre_slug)

    def test_user_genre(self):
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_user)
        """  Genre LIST  """
        request = user.get(reverse('genre_list'))
        self.assertEqual(request.status_code, 200)

        """  Genre POST  """
        genre_name = 'Авадакедабра'
        genre_slug = 'avadakedabra'
        request = user.post(reverse('genre_list'), data={'name': genre_name, 'slug': genre_slug})
        self.assertEqual(request.status_code, 403)
        request = user.get(reverse('genre_list'))
        self.assertNotContains(response=request, text=genre_name)
        self.assertNotContains(response=request, text=genre_slug)
        self.assertContains(response=request, text=self.genre.name)
        self.assertContains(response=request, text=self.genre.slug)

        """  Genre DELETE  """
        request = user.delete(reverse('genre_detail', kwargs={'slug': genre_slug}),
                              data={'name': genre_name, 'slug': genre_slug})
        self.assertEqual(request.status_code, 403)

    def test_moderator_genre(self):
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_moderator)
        """  Genre LIST  """
        request = user.get(reverse('genre_list'))
        self.assertEqual(request.status_code, 200)

        """  Genre POST  """
        genre_name = 'Авадакедабра'
        genre_slug = 'avadakedabra'
        request = user.post(reverse('genre_list'), data={'name': genre_name, 'slug': genre_slug})
        self.assertEqual(request.status_code, 403)
        request = user.get(reverse('genre_list'))
        self.assertNotContains(response=request, text=genre_name)
        self.assertNotContains(response=request, text=genre_slug)
        self.assertContains(response=request, text=self.genre.name)
        self.assertContains(response=request, text=self.genre.slug)

        """  Genre DELETE  """
        request = user.delete(reverse('genre_detail', kwargs={'slug': genre_slug}),
                              data={'name': genre_name, 'slug': genre_slug})
        self.assertEqual(request.status_code, 403)

    def test_anon_genre(self):
        user = APIClient()
        """  Genre LIST  """
        request = user.get(reverse('genre_list'))
        self.assertEqual(request.status_code, 200)

        """  Genre POST  """
        genre_name = 'Авадакедабра'
        genre_slug = 'avadakedabra'
        request = user.post(reverse('genre_list'), data={'name': genre_name, 'slug': genre_slug})
        self.assertEqual(request.status_code, 403)
        request = user.get(reverse('genre_list'))
        self.assertNotContains(response=request, text=genre_name)
        self.assertNotContains(response=request, text=genre_slug)
        self.assertContains(response=request, text=self.genre.name)
        self.assertContains(response=request, text=self.genre.slug)

        """  Genre DELETE  """
        request = user.delete(reverse('genre_detail', kwargs={'slug': genre_slug}),
                              data={'name': genre_name, 'slug': genre_slug})
        self.assertEqual(request.status_code, 403)
    """  Categories  """
    def test_admin_category(self):#  Образец
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_admin)
        """  Category LIST  """
        request = user.get(reverse('category_list'))
        self.assertEqual(request.status_code, 200)

        """  Category POST  """
        category_name = 'Искусство'
        category_slug = 'art'
        request = user.post(reverse('category_list'),
                            data={'name':category_name, 'slug':category_slug})
        self.assertEqual(request.status_code, 201)
        request = user.get(reverse('category_list'))
        self.assertContains(response=request, text=category_name)
        self.assertContains(response=request, text=category_slug)

        """  Category DELETE  """
        request = user.delete(reverse('category_detail', kwargs={'slug': category_slug}))
        self.assertEqual(request.status_code, 204)
        request = user.get(reverse('category_list'))
        self.assertNotContains(response=request, text=category_name)
        self.assertNotContains(response=request, text=category_slug)

    def test_user_category(self):
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_user)
        """  Category LIST  """
        request = user.get(reverse('category_list'))
        self.assertEqual(request.status_code, 200)

        """  Category POST  """
        category_name = 'Искусство'
        category_slug = 'art'
        request = user.post(reverse('category_list'),
                            data={'name': category_name, 'slug': category_slug})
        self.assertEqual(request.status_code, 403)
        request = user.get(reverse('category_list'))
        self.assertNotContains(response=request, text=category_name)
        self.assertNotContains(response=request, text=category_slug)

        """  Category DELETE  """
        request = user.delete(reverse('category_detail', kwargs={'slug': self.category.slug}))
        self.assertEqual(request.status_code, 403)
        request = user.get(reverse('category_list'))
        self.assertContains(response=request, text=self.category.name)
        self.assertContains(response=request, text=self.category.slug)

    def test_moderator_category(self):
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_moderator)
        """  Category LIST  """
        request = user.get(reverse('category_list'))
        self.assertEqual(request.status_code, 200)

        """  Category POST  """
        category_name = 'Искусство'
        category_slug = 'art'
        request = user.post(reverse('category_list'),
                            data={'name': category_name, 'slug': category_slug})
        self.assertEqual(request.status_code, 403)
        request = user.get(reverse('category_list'))
        self.assertNotContains(response=request, text=category_name)
        self.assertNotContains(response=request, text=category_slug)

        """  Category DELETE  """
        request = user.delete(reverse('category_detail', kwargs={'slug': self.category.slug}))
        self.assertEqual(request.status_code, 403)
        request = user.get(reverse('category_list'))
        self.assertContains(response=request, text=self.category.name)
        self.assertContains(response=request, text=self.category.slug)

    def test_anon_category(self):
        user = APIClient()
        """  Category LIST  """
        request = user.get(reverse('category_list'))
        self.assertEqual(request.status_code, 200)

        """  Category POST  """
        category_name = 'Искусство'
        category_slug = 'art'
        request = user.post(reverse('category_list'),
                            data={'name': category_name, 'slug': category_slug})
        self.assertEqual(request.status_code, 403)
        request = user.get(reverse('category_list'))
        self.assertNotContains(response=request, text=category_name)
        self.assertNotContains(response=request, text=category_slug)

        """  Category DELETE  """
        request = user.delete(reverse('category_detail', kwargs={'slug': self.category.slug}))
        self.assertEqual(request.status_code, 403)
        request = user.get(reverse('category_list'))
        self.assertContains(response=request, text=self.category.name)
        self.assertContains(response=request, text=self.category.slug)
    """  Users  """
    def test_admin_users(self):
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_admin)
        """  USERS LIST  """
        request = user.get(reverse('user_list'))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=self.user.username)
        self.assertContains(response=request, text=self.admin.username)
        self.assertContains(response=request, text=self.moderator.username)

        """  USERS POST  """
        test_user_1 = {'username': 'test_user', 'email': 'test_user@gmail.com'}
        request = user.post(reverse('user_list'), data=test_user_1)
        self.assertEqual(request.status_code, 201)
        request = user.get(reverse('user_list'))
        self.assertContains(response=request, text=test_user_1['username'])
        self.assertContains(response=request, text=test_user_1['email'])

        """  USERS ADMIN DETAIL  """
        request = user.get(reverse('admin_detail', kwargs={'username': test_user_1['username']}))
        self.assertEqual(request.status_code, 200)

        """  USERS ADMIN PATCH  """
        test_user_2 = {'username': 'test_user_patch', 'email': 'test_user_patch@gmail.com'}
        request = user.patch(reverse('admin_detail', kwargs={'username': test_user_1['username']}),
                    data={'username': test_user_2['username'], 'email': test_user_2['email']})
        self.assertEqual(request.status_code, 200)
        request = user.get(reverse('admin_detail', kwargs={'username': test_user_2['username']}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=test_user_2['username'])
        self.assertContains(response=request, text=test_user_2['email'])

        """  USERS ADMIN DELETE  """
        request = user.delete(reverse('admin_detail', kwargs={'username': test_user_2['username']}))
        self.assertEqual(request.status_code, 204)
        request = user.get(reverse('admin_detail', kwargs={'username': test_user_2['username']}))
        self.assertEqual(request.status_code, 404)
        request = user.get(reverse('user_list'))
        self.assertNotContains(response=request, text=test_user_2['username'])
        self.assertNotContains(response=request, text=test_user_2['email'])

        """  USERS USER INFO  """
        request = user.get(reverse('user_info'))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=self.admin.username)
        self.assertContains(response=request, text=self.admin.email)
        """  USERS USER INFO PATCH  """
        request = user.patch(reverse('user_info'), data=test_user_2)
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=test_user_2['username'])
        self.assertContains(response=request, text=test_user_2['email'])

    def test_user_users(self):
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_user)
        """  USERS LIST  """
        request = user.get(reverse('user_list'))
        self.assertEqual(request.status_code, 403)
        """  USERS POST  """
        test_user_1 = {'username': 'test_user', 'email': 'test_user@gmail.com'}
        request = user.post(reverse('user_list'), data=test_user_1)
        self.assertEqual(request.status_code, 403)
        """  USERS ADMIN DETAIL  """
        request = user.get(reverse('admin_detail', kwargs={'username': self.admin.username}))
        self.assertEqual(request.status_code, 403)
        """  USERS ADMIN PATCH  """
        request = user.patch(reverse('admin_detail',
                                     kwargs={'username': self.admin.username}),
                                     data=test_user_1)
        self.assertEqual(request.status_code, 403)
        """  USERS ADMIN DELETE  """
        request = user.delete(reverse('admin_detail', kwargs={'username': self.admin.username}))
        self.assertEqual(request.status_code, 403)
        """  USERS USER INFO  """
        request = user.get(reverse('user_info'))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=self.user.username)
        self.assertContains(response=request, text=self.user.email)
        """  USERS USER INFO PATCH  """
        request = user.patch(reverse('user_info'), data=test_user_1)
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=test_user_1['username'])
        self.assertContains(response=request, text=test_user_1['email'])

    def test_moderator_users(self):
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_moderator)
        """  USERS LIST  """
        request = user.get(reverse('user_list'))
        self.assertEqual(request.status_code, 403)
        """  USERS POST  """
        test_user_1 = {'username': 'test_user', 'email': 'test_user@gmail.com'}
        request = user.post(reverse('user_list'), data=test_user_1)
        self.assertEqual(request.status_code, 403)
        """  USERS ADMIN DETAIL  """
        request = user.get(reverse('admin_detail', kwargs={'username': self.admin.username}))
        self.assertEqual(request.status_code, 403)
        """  USERS ADMIN PATCH  """
        request = user.patch(reverse('admin_detail',
                                     kwargs={'username': self.admin.username}),
                                     data=test_user_1)
        self.assertEqual(request.status_code, 403)
        """  USERS ADMIN DELETE  """
        request = user.delete(reverse('admin_detail', kwargs={'username': self.admin.username}))
        self.assertEqual(request.status_code, 403)
        """  USERS USER INFO  """
        request = user.get(reverse('user_info'))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=self.moderator.username)
        self.assertContains(response=request, text=self.moderator.email)
        """  USERS USER INFO PATCH  """
        request = user.patch(reverse('user_info'), data=test_user_1)
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=test_user_1['username'])
        self.assertContains(response=request, text=test_user_1['email'])

    def test_anon_users(self):
        user = APIClient()
        """  USERS LIST  """
        request = user.get(reverse('user_list'))
        self.assertEqual(request.status_code, 403)
        """  USERS POST  """
        test_user_1 = {'username': 'test_user', 'email': 'test_user@gmail.com'}
        request = user.post(reverse('user_list'), data=test_user_1)
        self.assertEqual(request.status_code, 403)
        """  USERS ADMIN DETAIL  """
        request = user.get(reverse('admin_detail', kwargs={'username': self.admin.username}))
        self.assertEqual(request.status_code, 403)
        """  USERS ADMIN PATCH  """
        request = user.patch(reverse('admin_detail',
                                     kwargs={'username': self.admin.username}),
                                     data=test_user_1)
        self.assertEqual(request.status_code, 403)
        """  USERS ADMIN DELETE  """
        request = user.delete(reverse('admin_detail', kwargs={'username': self.admin.username}))
        self.assertEqual(request.status_code, 403)
        """  USERS USER INFO  """
        request = user.get(reverse('user_info'))
        self.assertEqual(request.status_code, 403)
        """USERS USER INFO PATCH"""
        request = user.patch(reverse('user_info'), data=test_user_1)
        #TODO по логику тут должна быть 403
        self.assertEqual(request.status_code, 404)
    """  Reviews  """
    def test_admin_review(self):
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_admin)
        """  Review list  """
        review = {'text': 'Ревьюшечка', 'score': 10}
        review_patch = {'text': 'Ревьюшечка PATCH', 'score': 5}
        request = user.post(reverse('review_list', kwargs={'title_id':1}), data=review)
        self.assertEqual(request.status_code, 201)
        request = user.get(reverse('review_list', kwargs={'title_id':1}))
        self.assertContains(response=request, text=review['text'])
        self.assertContains(response=request, text=review['score'])
        """  Review detail  """
        request = user.patch(reverse('review_detail',kwargs={'title_id':1, 'review_id': 1}),
                             data=review_patch)
        self.assertEqual(request.status_code, 200)

        request = user.get(reverse('review_detail', kwargs={'title_id':1, 'review_id': 1}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=review_patch['text'])
        self.assertContains(response=request, text=review_patch['score'])

        request = user.delete(reverse('review_detail', kwargs={'title_id':1, 'review_id': 1}))
        self.assertEqual(request.status_code, 204)
        request = user.get(reverse('review_detail', kwargs={'title_id':1, 'review_id': 1}))
        self.assertEqual(request.status_code, 404)

    def test_user_review(self):
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_user)
        """  Review list  """
        review = {'text': 'Ревьюшечка', 'score': 10}
        review_patch = {'text': 'Ревьюшечка PATCH', 'score': 5}
        request = user.post(reverse('review_list', kwargs={'title_id':1}), data=review)
        self.assertEqual(request.status_code, 201)
        request = user.get(reverse('review_list', kwargs={'title_id':1}))
        self.assertContains(response=request, text=review['text'])
        self.assertContains(response=request, text=review['score'])
        """  Review detail  """
        request = user.patch(reverse('review_detail',kwargs={'title_id':1, 'review_id': 1}),
                             data=review_patch)
        self.assertEqual(request.status_code, 200)

        request = user.get(reverse('review_detail', kwargs={'title_id':1, 'review_id': 1}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=review_patch['text'])
        self.assertContains(response=request, text=review_patch['score'])

        request = user.delete(reverse('review_detail', kwargs={'title_id':1, 'review_id': 1}))
        self.assertEqual(request.status_code, 204)
        request = user.get(reverse('review_detail', kwargs={'title_id':1, 'review_id': 1}))
        self.assertEqual(request.status_code, 404)

    def test_moderator_review(self):
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_moderator)
        """  Review list  """
        review = {'text': 'Ревьюшечка', 'score': 10}
        review_patch = {'text': 'Ревьюшечка PATCH', 'score': 5}
        request = user.post(reverse('review_list', kwargs={'title_id':1}), data=review)
        self.assertEqual(request.status_code, 201)
        request = user.get(reverse('review_list', kwargs={'title_id':1}))
        self.assertContains(response=request, text=review['text'])
        self.assertContains(response=request, text=review['score'])
        """  Review detail  """
        request = user.patch(reverse('review_detail',
                                     kwargs={'title_id':1, 'review_id': 1}),
                                     data=review_patch)
        self.assertEqual(request.status_code, 200)

        request = user.get(reverse('review_detail', kwargs={'title_id':1, 'review_id': 1}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=review_patch['text'])
        self.assertContains(response=request, text=review_patch['score'])
        
        request = user.delete(reverse('review_detail', kwargs={'title_id':1, 'review_id': 1}))
        self.assertEqual(request.status_code, 204)
        request = user.get(reverse('review_detail', kwargs={'title_id':1, 'review_id': 1}))
        self.assertEqual(request.status_code, 404)

    def test_anon_review(self):
        user = APIClient()
        admin_user = APIClient()
        admin_user.credentials(HTTP_AUTHORIZATION=self.token_admin)
        """  Review list  """
        review = {'text': 'Ревьюшечка', 'score': 10}
        review_patch = {'text': 'Ревьюшечка PATCH', 'score': 5}

        request = user.post(reverse('review_list', kwargs={'title_id':1}), data=review)
        self.assertEqual(request.status_code, 403)

        request = admin_user.post(reverse('review_list', kwargs={'title_id':1}), data=review)

        request = user.get(reverse('review_list', kwargs={'title_id':1}))
        self.assertContains(response=request, text=review['text'])
        self.assertContains(response=request, text=review['score'])
        """  Review detail  """
        request = user.patch(reverse('review_detail',kwargs={'title_id':1, 'review_id': 1}),
                             data=review_patch)
        self.assertEqual(request.status_code, 403)

        request = user.get(reverse('review_detail', kwargs={'title_id':1, 'review_id': 1}))
        self.assertEqual(request.status_code, 200)

        request = user.delete(reverse('review_detail', kwargs={'title_id':1, 'review_id': 1}))
        self.assertEqual(request.status_code, 403)
    """  Comments  """    
    def test_admin_comment(self):
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_admin)
        review = Review.objects.create(text='Ревьюшка', score=10, title=self.title, author=self.admin)
        comment = {'text': 'Комментарий'}
        comment_patch = {'text': 'Комментарий PATCH'}
        """  Comment list  """
        request = user.post(reverse('comment_list', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk}), data=comment)
        comment_id = request.data.get('id')
        self.assertEqual(request.status_code, 201)
        request = user.get(reverse('comment_list', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=comment['text'])
        """  Comment detail  """
        request = user.get(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=comment['text'])

        request = user.patch(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}), data=comment_patch)
        self.assertEqual(request.status_code, 200)
        request = user.get(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=comment_patch['text'])

        request = user.delete(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}))
        self.assertEqual(request.status_code, 204)

        request = user.get(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}))
        self.assertEqual(request.status_code, 404)

    def test_user_comment(self):
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_user)
        review = Review.objects.create(text='Ревьюшка', score=10, title=self.title, author=self.admin)
        comment = {'text': 'Комментарий'}
        comment_patch = {'text': 'Комментарий PATCH'}
        """  Comment list  """
        request = user.post(reverse('comment_list', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk}), data=comment)
        comment_id = request.data.get('id')
        self.assertEqual(request.status_code, 201)
        request = user.get(reverse('comment_list', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=comment['text'])
        """  Comment detail  """
        request = user.get(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=comment['text'])

        request = user.patch(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}), data=comment_patch)
        self.assertEqual(request.status_code, 200)
        request = user.get(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=comment_patch['text'])
        
        request = user.delete(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}))
        self.assertEqual(request.status_code, 204)

        request = user.get(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}))
        self.assertEqual(request.status_code, 404)

    def test_moderator_comment(self):
        user = APIClient()
        user.credentials(HTTP_AUTHORIZATION=self.token_moderator)
        review = Review.objects.create(text='Ревьюшка', score=10, title=self.title, author=self.admin)
        comment = {'text': 'Комментарий'}
        comment_patch = {'text': 'Комментарий PATCH'}
        """  Comment list  """
        request = user.post(reverse('comment_list', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk}), data=comment)
        comment_id = request.data.get('id')
        self.assertEqual(request.status_code, 201)
        request = user.get(reverse('comment_list', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=comment['text'])
        """  Comment detail  """
        request = user.get(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=comment['text'])

        request = user.patch(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}), data=comment_patch)
        self.assertEqual(request.status_code, 200)
        request = user.get(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=comment_patch['text'])

        request = user.delete(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}))
        self.assertEqual(request.status_code, 204)

        request = user.get(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}))
        self.assertEqual(request.status_code, 404)

    def test_anon_comment(self):
        user = APIClient()
        admin_user = APIClient()
        admin_user.credentials(HTTP_AUTHORIZATION=self.token_admin)
        review = Review.objects.create(text='Ревьюшка', score=10, title=self.title, author=self.admin)
        comment = {'text': 'Комментарий'}
        comment_patch = {'text': 'Комментарий PATCH'}
        """  Comment list  """
        request = user.post(reverse('comment_list', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk}), data=comment)
        self.assertEqual(request.status_code, 403)
        request = admin_user.post(reverse('comment_list', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk}), data=comment)
        comment_id = request.data.get('id')
        request = user.get(reverse('comment_list', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=comment['text'])
        """  Comment detail  """
        request = user.get(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}))
        self.assertEqual(request.status_code, 200)
        self.assertContains(response=request, text=comment['text'])
        
        request = user.patch(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}), data=comment_patch)
        self.assertEqual(request.status_code, 403)

        request = user.delete(reverse('comment_detail', kwargs={'title_id':self.title.pk,
                                                            'review_id': review.pk,
                                                            'comment_id': comment_id}))
        self.assertEqual(request.status_code, 403)
