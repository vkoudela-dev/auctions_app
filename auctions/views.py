from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from . import util
import datetime

from .models import User, Category, Listing, Bid, BidItem, Watcher, Comment

class Listing_form(forms.ModelForm):
    title = forms.CharField(label="", max_length=64, widget = forms.TextInput(attrs={"placeholder": "Title"}))
    description = forms.CharField(label="", max_length=264, widget = forms.Textarea(attrs={"placeholder": "Description"}))
    price = forms.IntegerField(label="", widget=forms.TextInput(attrs={"placeholder": "Price"}))
    url = forms.URLField(label="", widget=forms.TextInput(attrs={"placeholder": "Image URL"}))
    category = forms.ModelChoiceField(label="", queryset=Category.objects.all(), empty_label="Select Category")

    class Meta:
        model=Listing
        fields=["title", "description", "price", "url", "category"]

class Comment_form(forms.ModelForm):
    text = forms.CharField(label="", max_length=128, widget = forms.Textarea(attrs={"placeholder": "Your comment"}))

    class Meta:
        model=Comment
        fields=["text"]

def index(request):
    user = request.user
    count = util.watchlist_count(user)
    listings = Listing.objects.filter(status=True)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "count": count
    })

def categories(request):
    user = request.user
    count = util.watchlist_count(user)
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "count": count,
        "categories": categories
    })

def category_list(request, category_id):
    user = request.user
    count = util.watchlist_count(user)
    instance_category = Category.objects.get(pk=category_id)
    category = instance_category.category
    listings = Listing.objects.filter(status=True, category_id=category_id)
    return render(request, "auctions/category.html", {
        "listings": listings,
        "count": count,
        "category": category
    })
   
@login_required
def create_listing(request):
    count = util.watchlist_count(request.user)
    if request.method == "POST":
        form = Listing_form(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            user = User.objects.get(username=request.user)
            instance.user_id = int(user.id)
            category = Category.objects.get(category=form.cleaned_data["category"])
            instance.category_id = int(category.id)
            instance.actual_price = int(form.cleaned_data["price"])
            instance.timestamp = datetime.datetime.now()
            instance.save()

            return HttpResponseRedirect(reverse("index"))
        return render(request, "auctions/error.html")
    else:
        return render(request, "auctions/create_listing.html", {
            "form": Listing_form(),
            "count": count
        })


def listing(request, listing_id):
    user = request.user
    count = util.watchlist_count(user)
    listing = Listing.objects.get(pk=listing_id)
    listing_user = listing.user
    bids_count = util.bids_count(listing_id)
    price = listing.actual_price
    comments = Comment.objects.filter(listing_id=listing_id)
    if user == listing_user:
        creator = True
    else:
        creator = False

    if listing.status == False:
        winner = util.winner(listing_id, user)
        if winner:
            msg = "Congratulations! You've won the auction!"
            victory = True
        else:
            msg = False
            victory = True
    else:
        winner = False
        victory = False
        msg = False

    return render(request, "auctions/listing.html", {
        "comment_form": Comment_form(),
        "comments": comments,
        "listing": listing,
        "count": count,
        "bids_count": bids_count,
        "price": price,
        "creator": creator,
        "winner": winner,
        "msg": msg,
        "victory": victory
    })

@login_required
def add_comment(request):
    listing_id = int(request.POST["listing_id"])
    if request.method == "POST":
        form = Comment_form(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            user = User.objects.get(username=request.user)
            instance.user_id = int(user.id)
            instance.listing_id = listing_id
            instance.text = form.cleaned_data["text"]
            instance.timestamp = datetime.datetime.now()
            instance.save()
    return HttpResponseRedirect(reverse("listing", args=[listing_id,]))

@login_required
def bidding(request):
    user = User.objects.get(username=request.user)
    user_id = int(user.id)
    listing_id = int(request.POST["listing_id"])
    listing = Listing.objects.get(pk=listing_id)
    count = util.watchlist_count(request.user)
    bids_count = util.bids_count(listing_id)
    price = listing.actual_price
    comments = Comment.objects.filter(listing_id=listing_id)

    try:
        bid_value = int(request.POST["bid_value"])
    except ValueError:
        return render(request, "auctions/listing.html", {
        "comment_form": Comment_form(),
        "comments": comments,
        "listing": listing,
        "count": count,
        "bids_count": bids_count,
        "price": price,
        "msg": "Not a number!"
    })

    biditem_instance = BidItem.objects.filter(listing_id=listing_id)
    if biditem_instance.exists():
        if bid_value <= price:
            return render(request, "auctions/listing.html", {
            "comment_form": Comment_form(),
            "comments": comments,
            "listing": listing,
            "count": count,
            "bids_count": bids_count,
            "price": price,
            "msg": "Your bid should be greater than the current price!"
            })

        biditem_instance = BidItem.objects.get(listing_id=listing_id)
        new_bid = biditem_instance.bids.create(user_id=user_id, bid=bid_value, listing_id=listing_id)
        bids_count = util.bids_count(listing_id)
        listing.actual_price = bid_value
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=[listing_id,]))
    else:
        if bid_value < price:
            return render(request, "auctions/listing.html", {
            "comment_form": Comment_form(),
            "comments": comments,
            "listing": listing,
            "count": count,
            "bids_count": bids_count,
            "price": price,
            "msg": "Your bid should be at least the current price!"
            })
        biditem_instance = BidItem()
        biditem_instance.listing = listing
        biditem_instance.timestamp = datetime.datetime.now()
        biditem_instance.save()
        listing.actual_price = bid_value
        listing.save()
        new_instance = BidItem.objects.get(listing_id=listing_id)
        new_bid = new_instance.bids.create(user_id=user_id, bid=bid_value, listing_id=listing_id)
        bids_count = util.bids_count(listing_id)
        return HttpResponseRedirect(reverse("listing", args=[listing_id,]))

@login_required
def end_auction(request):
    listing_id = int(request.POST["listing_id"])
    listing = Listing.objects.get(pk=listing_id)
    listing.status = False
    listing.save()
    user = request.user
    winner = util.winner(listing_id, user)

    if winner:
        price = listing.actual_price
        count = util.watchlist_count(user)
        return render(request, "auctions/listing.html", {
        "listing": listing,
        "count": count,
        "price": price,
        "msg": "Congratulations! You've won the auction!",
        "victory": True
        }) 
    else:
        return HttpResponseRedirect(reverse("listing", args=[listing_id,]))

@login_required
def watchlist(request):
    user = User.objects.get(username=request.user)
    user_id = int(user.id)
    count = util.watchlist_count(user)
    if request.method == "POST":
        listing = int(request.POST["listing_id"])
        instance = Watcher.objects.filter(user_id=user_id)
        
        if not instance.exists():
            instance = Watcher()
            instance.user_id = user_id
            instance.save()
            instance.listings.add(listing)
        else:
            instance = Watcher.objects.get(user_id=user_id)
            instance.listings.add(listing)

        return HttpResponseRedirect(reverse("listing", args=[listing,]))
    
    watcher = Watcher.objects.filter(user_id=user_id)
    if not watcher.exists():
        return render(request, "auctions/watchlist.html", {
            "count": count
        })
    else:
        watcher = Watcher.objects.get(user_id=user_id)
        return render(request, "auctions/watchlist.html", {
            "watchlist": watcher.listings.filter(status=True),
            "count": count
        })

@login_required
def remove(request):
    user = User.objects.get(username=request.user)
    user_id = user.id
    watchitem_id = request.POST["watchitem_id"]
    listing = Listing.objects.get(pk=int(watchitem_id))
    instance = Watcher.objects.get(user_id=user_id)
    instance.listings.remove(listing)

    return HttpResponseRedirect(reverse("watchlist"))

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