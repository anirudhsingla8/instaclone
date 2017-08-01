from __future__ import unicode_literals
from django.db import models
import uuid
from custom_addons.models import BaseModel
from anirudh.settings import BASE_DIR

# Create your models here.
class UserModel(BaseModel):
    email = models.EmailField(max_length=100,unique=True,blank=False)
    name = models.CharField(max_length=120)
    username = models.CharField(max_length=120, blank=False)
    password = models.CharField(max_length=255)


class UserSession(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.PROTECT)
    session_token = models.CharField(max_length=255)
    is_valid = models.BooleanField(default=True)

    def create_session_token(self):
        self.session_token = uuid.uuid4()


class PostModel(BaseModel):
    user = models.ForeignKey(UserModel)
    image = models.FileField(upload_to='user_images')
    image_url = models.CharField(max_length=255)
    caption = models.CharField(max_length=240)
    has_liked = False


    @property
    def like_count(self):
        return len(LikeModel.objects.filter(post=self))

    @property
    def comment(self):
        return CommentModel.objects.filter(post=self).order_by('-created_on')

    @property
    def categories(self):
        return CategoryModel.objects.filter(post=self)

class LikeModel(BaseModel):
    user = models.ForeignKey(UserModel)
    post = models.ForeignKey(PostModel)


class CommentModel(BaseModel):
    user = models.ForeignKey(UserModel)
    post = models.ForeignKey(PostModel)
    comment_text = models.CharField(max_length=555)


class CategoryModel(models.Model):
    post = models.ForeignKey(PostModel)
    category_text = models.CharField(max_length=555)