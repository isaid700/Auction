from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.product, name="create"),
    path("listing/<int:listing_id>", views.listing_details, name="listing_details"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("listing/<int:listing_id>/place_bid", views.place_bid, name="place_bid"),
    path('listing/<int:listing_id>/close_auction', views.close_auction, name='close_auction'),
    path("listing/<int:listing_id>/submit_comment/", views.submit_comment, name="submit_comment"),
    path("categories/", views.categories, name="categories"),
    path("categories/<str:category_name>/", views.category_listings, name="category_listings")
]
