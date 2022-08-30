from rest_framework import mixins, viewsets


class ListCreateDestroyViewSet(mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               mixins.CreateModelMixin,
                               viewsets.GenericViewSet):
    pass
