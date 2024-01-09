cat requirements.txt | xargs poetry add
# 
Короткие ссылки могут создавать все
Но списки получать только по Токену
```python

    urlpatterns = [
        path('url/<str:hash>/', views.redirect_original_url),
        path('url/', views.create_short_url),
        path('url/stats/<str:hash>/', views.get_url_stats),
        path('url/list/jdjdjegssh/', views.get_list_url),
        path('url/delete/<str:hash>/', views.delete_url),
    ]
```
env.dev
```python
    DJANGO_READ_DOT_ENV_FILE=True
    DEBUG=True
    ALLOWED_HOSTS=*
    SECRET_TOKEN=23456789098765432w3e4r5tydcfvgbhn
    READ_DOT_ENV_FILE=True
```