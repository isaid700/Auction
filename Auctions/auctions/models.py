from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ModelForm

class User(AbstractUser):
    pass

#Defines the listings
class listings(models.Model):
#originally had these in the actual fields - code didnt work - redid syntax found here: https://stackoverflow.com/questions/27440861/django-model-multiplechoice
    catagory_choices = ( 
    ('1', 'Electronics'),
    ('2', 'Clothing'),
    ('3', 'Sporting Goods'),
    ('4', 'Health & Beauty'),
    ('5', 'Home'),
    ('6', 'Pets'))

    condition_choices = ( 
    ('excellent', 'excellent'),
    ('good', 'good'),
    ('fair', 'fair'),
    ('poor', 'poor'))


    title = models.CharField(max_length=100)
    condition = models.CharField(max_length=9, choices = condition_choices)
    description = models.CharField(max_length=2000)
    image = models.URLField(blank=True)
    wishlist = models.ManyToManyField(User, blank=True, related_name="wishlist_user")
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default= 0)
    deadline = models.DateTimeField(null=True)
    catagory = models.CharField(max_length=1, blank= True, choices = catagory_choices)
    # Learned through documentation https://docs.djangoproject.com/en/4.2/topics/auth/customizing/
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name= "listing_creator", null=True)
    is_closed = models.BooleanField(default= False)

        
#Defines the form to create a listing
class ListingForm(ModelForm):
    class Meta:
        model = listings
        fields = ['title', 'condition', 'description', 'image', 'starting_bid', 'catagory']

# returns each field as a string
def __str__(self):
    return self.title

class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    listing = models.ForeignKey(listings, on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_time = models.DateTimeField

class BidForm (ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']

class comment(models.Model):
    item = models.ForeignKey(listings, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=False)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.item.title}"

class commentForm (ModelForm):
    class Meta:
        model = comment
        fields = ['content']
