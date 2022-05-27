from django.urls import path

from fitgenius.users.views import (
    user_detail_view,
    user_redirect_view,
    user_update_view, CreateUserView, UpdateUserView, ListUserView, DeleteUserView
)

app_name = "users"
urlpatterns = [
    # path("~redirect/", view=user_redirect_view, name="redirect"),
    # path("~update/", view=user_update_view, name="update"),

    path('', ListUserView.as_view(), name="list-user"),
    path("add/", CreateUserView.as_view(), name="add-user"),
    path('<uuid:uuid>/update/', UpdateUserView.as_view(), name="update-user"),
    path('<uuid:uuid>/delete/', DeleteUserView.as_view(), name="delete-user"),
    path('', ListUserView.as_view(), name="list-user"),
    # path("<str:username>/", view=user_detail_view, name="detail"),
    path("profile/", view=user_detail_view, name="detail"),
]
