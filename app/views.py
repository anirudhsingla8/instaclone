# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
import datetime
from anirudh.settings import BASE_DIR
from imgurpython import ImgurClient

from models import UserModel, SessionToken, PostModel, LikeModel, CommentModel
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm
import sendgrid
from sendgrid.helpers.mail import *
from clarifai.rest import ClarifaiApp


clari = 'fb62f6d1e3c7455fa3f6167604bece61'
YOUR_CLIENT_ID = "061fbca36570a61"
YOUR_CLIENT_SECRET = "7d9841c62e75b77a4592391463c09747496e0cd7"
API_KEY = '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'

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = UserModel(name=name, password=make_password(password), email=email, username=username)
            user.save()

            sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
            from_email = Email("support@InstaClone.com")
            to_email = Email(email)
            subject = "Signup Succesfull!"
            content = Content("text/plain","Welcome to InstaClone.Login and enjoy!")
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())

            return render(request, 'success.html')
    else:
        form = SignUpForm()
    today=datetime.now()
    return render(request, 'index.html',{'today':today}, {'form':form})


def login_view(request):
    response_data = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = UserModel.objects.filter(username=username).first()

            if user:
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    response_data['message'] = 'Incorrect Password! Please try again!'

    elif request.method == 'GET':
        form = LoginForm()

    response_data['form'] = form
    return render(request, 'login.html', response_data)


def post_view(request):
    user = check_validation(request)

    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()

                path = str(BASE_DIR + '\\' + post.image.url)

                client = ImgurClient(YOUR_CLIENT_ID, YOUR_CLIENT_SECRET)
                post.image_url = client.upload_from_path(path,anon=True)['link']
                post.save()


                return redirect('/feed/')

        else:
            form = PostForm()
        return render(request, 'post.html', {'form' : form})
    else:
        return redirect('/login/')


def feed_view(request):
    user = check_validation(request)
    if user:

        posts = PostModel.objects.all().order_by('created_on')

        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True

        return render(request, 'feed.html', {'posts': posts})
    else:

        return redirect('/login/')


def like_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
            else:
                existing_like.delete()
            return redirect('/feed/')
    else:
        return redirect('/login/')


def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()

            posting = PostModel.objects.filter(id=post_id).first()
            userid = posting.user_id
            user = UserModel.objects.filter(id=userid).first()
            mail = user.email

            sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
            from_email = Email("support@InstaClone.com")
            to_email = Email(mail)
            subject = "Comment Notification"
            content = Content("text/plain", "Someone just commented on your post!")
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())

            return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login')

def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            return session.user
    else:
        return None

def category(post):
    app = ClarifaiApp(api_key=clari)
    model = app.models.get("general-v1.3")
    response = model.predict_by_url(url=post.image_url)
    if response["status"]["code"] == 10000:
        if response["outputs"]:
            if response["outputs"][0]["data"]:
                if response["outputs"][0]["data"]["concepts"]:
                    for index in range(0, len(response["outputs"][0]["data"]["concepts"])):
                        category = Category(post=post,category_text=response["outputs"][0]["data"]["concepts"][index]["name"])
                        category.save()
                else:
                    print "No Concepts List found"
            else:
                print "No Data found"
        else:
            print "No Outputs List found"
    else:
        print "Response Code not found"



