from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),
    # Страница с постами для выбранной группы
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    # Профайл пользователя
    path('profile/<str:username>/', views.profile, name='profile'),
    # Редактировать записи
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    # Удалить записи
    path('posts/<int:post_id>/delete/',
         views.PostDeleteView.as_view(),
         name='post_delete'),
    # Просмотр записи
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    # Создание записи
    path('create/', views.post_create, name='post_create'),
    # Комментарий
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
    # Авторы, на которых подписан пользователь
    path('follow/', views.follow_index, name='follow_index'),
    # Подписаться на автора
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    # Отписаться от автора
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
    # Поставить рейтинг посту
    path('posts/<int:post_id>/rate', views.rate_post, name='rate_post')
]
