from django.urls import include, path
from rest_framework import routers

from .views import (
    UserViewSet, APISignup, APIObtainToken,
    CommentViewSet, ReviewViewSet, TitlesViewSet, GenresViewSet,
    CategoriesViewSet
)

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'titles', TitlesViewSet, 'Titles')

router.register(r'genres', GenresViewSet, 'Genres')
router.register(r'categories', CategoriesViewSet, 'Categories')

router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, 'Review')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    'Comment')

urlpatterns = [
    path('v1/auth/signup/', APISignup.as_view(), name='signup'),
    path('v1/auth/token/', APIObtainToken.as_view(), name='token'),
    path('v1/', include(router.urls)),
]
