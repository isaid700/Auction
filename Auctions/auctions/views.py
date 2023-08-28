from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, listings, ListingForm, Bid, BidForm, comment, commentForm


def index(request):
    all_listings = listings.objects.all()
    return render(request, "auctions/index.html", {
        "listings": all_listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

#For the listing creation page
@login_required(login_url="/login")
def product(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            new_listing = form.save(commit=False)
            new_listing.creator = request.user #make poster the 'creator'
            new_listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = ListingForm()
    
    return render(request, "auctions/create.html", {
        "form": form
    })

#for the page that shows details of each auction item when clicked
def listing_details(request, listing_id):

    # Found a geeksforgeeks page on get_list and that led me here: https://docs.djangoproject.com/en/4.2/topics/http/shortcuts/
    listing = get_object_or_404(listings, pk=listing_id)
    is_creator = False
    is_winner = False

    # Check if the user is the winner of the listing
    if request.user == listing.creator:
        is_creator = True

    # Check if the auction is closed and the user is the winner
    if listing.is_closed:
        highest_bid = listing.bid_set.order_by('-amount').first()
        if highest_bid and request.user == highest_bid.bidder:
            is_winner = True
    
    # Handles closing the page
    if request.method == "POST":
        if "close_listing" in request.POST:
            if not listing.is_active:
                message = "This listing is already closed."
        else:
            listing.is_active = False
            listing.save()
            return HttpResponseRedirect(reverse("listing_details", args=[listing_id]))
    return render(request, "auctions/listing_details.html", {
        "listing": listing,
        "is_creator": is_creator,
        "is_winner": is_winner,
    })

# Handles the logic for the wishlist
@login_required(login_url="/login")
def wishlist(request):
    if request.method == "POST":
        listing_id = request.POST.get("listing_id")
        listing = get_object_or_404(listings, pk=listing_id)
        user = request.user

        # Toggle the listing in the user's wishlist
        if listing in user.wishlist_user.all():
            user.wishlist_user.remove(listing)
        else:
            user.wishlist_user.add(listing)

    # Retrieve wishlist items for the current user
    user = request.user
    wishlist_listings = user.wishlist_user.all()

    return render(request, "auctions/wishlist.html", {
        "wishlist_listings": wishlist_listings
    })

#For placing the bid
@login_required(login_url="/login")
def place_bid(request, listing_id):
    listing = get_object_or_404(listings, pk=listing_id)
    
    if request.method == "POST":
        bid_amount = request.POST.get("bid_amount")
        if bid_amount is not None:
            try:
                bid_amount = float(bid_amount)
                if bid_amount >= listing.starting_bid and bid_amount > listing.current_bid:
                    # Create the bid object
                    bid = Bid.objects.create(amount=bid_amount, listing=listing, bidder=request.user)
                    # Update the current bid of the listing
                    listing.current_bid = bid_amount
                    listing.save()
                    return HttpResponseRedirect(reverse("listing_details", args=[listing_id]))
                else:
                    return render(request, "auctions/listing_details.html", {
                        "listing": listing,
                        "message": "Invalid bid amount."
                    })
            except ValueError:
                return render(request, "auctions/listing_details.html", {
                    "listing": listing,
                    "message": "Invalid bid amount."
                })
            
# For closing the auction
def close_auction(request, listing_id):
    listing = get_object_or_404(listings, pk=listing_id)

    # Check if the user is the creator of the listing
    if request.user == listing.creator:
        if listing.is_closed:
            message = "This listing is already closed."
        else:
            listing.is_closed = True
            listing.save()
            message = "Auction closed successfully."
    else:
        message = "You have to be the owner of the listing to close the auction."

    return render(request, "auctions/listing_details.html", {
        "listing": listing,
        "message": message
    })

# Comment submission view
def submit_comment(request, listing_id):
    listing = get_object_or_404(listings, pk=listing_id)

    if request.method == "POST":
        comment_form = commentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.item = listing
            new_comment.user = request.user
            new_comment.save()
            return HttpResponseRedirect(reverse("listing_details", args=[listing_id]))
    else:
        comment_form = commentForm()

    return render(request, "auctions/listing_details.html", {
        "listing": listing,
        "comment_form": comment_form,
    })

#Catagories
def categories(request):
    categories = listings.catagory_choices

    # Get all categories with their respective listings
    categories_with_listings = []
    for category_code, category_name in categories:
        listings_in_category = listings.objects.filter(catagory=category_code)
        categories_with_listings.append((category_code, category_name, listings_in_category))

    return render(request, "auctions/categories.html", {"categories": categories_with_listings})

def category_listings(request, category_name):
    # Get all active listings in the selected category
    listings_in_category = listings.objects.filter(catagory=category_name, is_closed=False)

    # Check if there are any listings in the category
    is_empty_category = not listings_in_category.exists()

    return render(request, "auctions/category_listings.html", {
        "listings": listings_in_category,
        "is_empty_category": is_empty_category
        })
