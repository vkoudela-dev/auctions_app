from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="createlisting"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category_id>", views.category_list, name="categorylist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("end_auction", views.end_auction, name="endauction"),
    path("listing/<str:listing_id>", views.listing, name="listing"),
    path("bidding_error", views.bidding, name="bidding"),
    path("remove", views.remove, name="remove"),
    path("add_comment", views.add_comment, name="addcomment")
]
