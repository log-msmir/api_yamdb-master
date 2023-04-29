from django.core.exceptions import ValidationError

from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound


class FilterMixin:

    def filter_queryset(self, queryset):
    #TODO обработка ошибки при передаче параметра и 
    #TODO отсутствия search_fields >> has_attr
        query = self.request.query_params
        if query:
            filter = {k + '__icontains':query.get(k) for k in query.keys()
                      if k in self.search_fields}
            if not filter:
                raise NotFound(detail={'error': 'No data found'})
            filtering_queryset = queryset.filter(**filter)
            return filtering_queryset
        else:
            return queryset


class SlugDeleteMixin:

    def destroy(self, request, slug, *args, **kwargs):
        queryset = self.get_queryset()
        model_name = queryset.model._meta.model_name
        try:
            data = queryset.get(slug__iexact=slug)
        except:
            return Response({'error': f'{model_name} is not exist-{slug}'}, status=status.HTTP_404)

        data.delete()
        return Response({'OK': f'Object {slug} was deleted'}, status=status.HTTP_204_NO_CONTENT)


class ValidationMixin:

    def check_data(self, instance):
        try:
            instance.full_clean()
        except ValidationError as err:
            raise ParseError(detail=err)


class UserStatusMixin:

    def is_staff(self, request):
        try:
            return request.user.role in ['moderator', 'admin']
        except:
            return False

    def is_admin(self, request):
        try:
            return request.user.role == 'admin'
        except:
            return False

    def is_authenticated(self, request):
        try:
            return bool(request.user.pk)
        except:
            return False
