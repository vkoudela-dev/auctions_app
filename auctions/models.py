from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=32)

    class Meta:
        ordering = ["category"]
        
    def __str__(self):
        return f"{self.category}"

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users_listings")
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=264)
    price = models.IntegerField()
    actual_price = models.IntegerField()
    url = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings_in_category")
    timestamp = models.DateTimeField()
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"ID: {self.id} Title: {self.title} Description: {self.description} Price: ${self.price} Photo: {self.url} Category:{self.category}"

class Watcher(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listings = models.ManyToManyField(Listing, blank=True, related_name="watchers")

    def __str__(self):
        return f"{self.user}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid = models.IntegerField()

class BidItem(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bids = models.ManyToManyField(Bid, blank=True)
    timestamp = models.DateTimeField()

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    text = models.CharField(max_length=128)
    timestamp = models.DateTimeField()

