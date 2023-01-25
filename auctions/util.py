from .models import *

def watchlist_count(user):
    user_check = User.objects.filter(username=user)
    if user_check.exists():
        user = User.objects.get(username=user)
        user_id = int(user.id)
        instance = Watcher.objects.filter(user_id=user_id)
        if instance.exists():
            watcher = Watcher.objects.get(user_id=user_id)
            count = watcher.listings.filter(status=True).count()
            return count
        else:
            return None
    return None

def bids_count(listing_id):
    biditem_check = BidItem.objects.filter(listing_id=listing_id)
    if biditem_check.exists():
        bid_item_object = BidItem.objects.get(listing_id=listing_id)
        bids_count = bid_item_object.bids.all().count()
        return bids_count
    return 0

def winner(listing_id, user):
    biditem_instance = BidItem.objects.filter(listing_id=listing_id)
    if biditem_instance.exists():
        biditem_instance = BidItem.objects.get(listing_id=listing_id)
        biditem_last_bid = biditem_instance.bids.last()
        user = User.objects.get(username=user)
        user_id_signed = user.id
        user_id = biditem_last_bid.user_id
        if user_id_signed == user_id:
            return True
        return False
    return