# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect


from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
import datetime as dt
from .models import Article, NewsLetterRecipients
from .forms import NewsLetterForm, NewsArticleForm
from .email import send_welcome_email
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response 
from rest_framework.views import APIView
from rest_framework import status
from .models import MoringaMerch
from .serializer import MerchSerializer
from .permissions import IsAdminOrReadOnly


# Create your views here.
def welcome(request):
    # return HttpResponse('Welcome to the Moringa Tribune')
    return render (request, 'welcome.html')

# def news_of_day(request):
#     date = dt.date.today()

    # FUNCTION TO CONVERT DATE OBJECT TO FIND EXACT DAY
    # day = convert_dates(date)
    # html = f'''
    #     <html>
    #         <body>
    #             <h1> News for {day} {date.day}-{date.month}-{date.year} <h1>
    #     </html>
    #         '''
    # return HttpResponse(html)

def convert_dates(dates):

    # Function that gets the weekday number for the date.
    day_number = dt.date.weekday(dates)
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

    # Returning the actual day of the week
    day = days[day_number]
    return day


# View Function to present news from past days
def past_days_news(request, past_date):

    try:
        # Converts data from the string Url
        date = dt.datetime.strptime(past_date, '%Y-%m-%d').date()

    except ValueError:
        # Raise 404 error when ValueError is thrown
        raise Http404()
        assert False

    if date == dt.date.today():
        return redirect(news_today)

    return render(request, 'all-news/past-news.html', {"date": date,"news":news})

    # day = convert_dates(date)
    # html = f'''
    #     <html>
    #         <body>
    #             <h1> News for {day} {date.day}-{date.month}-{date.year} <h1>
    #     </html>
    #         '''
    # return HttpResponse(html)


def news_today(request):
    # news = Article.today_news()
    # news = Article.objects.all()
    # news.reverse()
    date = dt.date.today()
    news = Article.today_news()
    form = NewsLetterForm()

    if request.method == 'POST':
        form = NewsLetterForm(request.POST)
        if form.is_valid():
            # print('valid')
            name = form.cleaned_data['your_name']
            email = form.cleaned_data['email']

            recipient = NewsLetterRecipients(name = name, email = email)
            recipient.save()
            send_welcome_email(name, email)

            HttpResponseRedirect('news_today')
    else:
        form = NewsLetterForm()

    return render(request, 'all-news/today-news.html', {"date":date, "news":news, "letterForm":form})

def search_results(request):

    if 'article' in request.GET and request.GET["article"]:
        search_term = request.GET.get("article")
        searched_articles = Article.search_by_title(search_term)
        message = f"(search_term)"

        return render(request, 'all-news/search.html',{"message":message,"articles": searched_articles})

    else:
        message = "You haven't searched for any term"
        return render(request, 'all-news/search.html',{"message":message})



@login_required(login_url='/accounts/login/')
def article(request,article_id):
    try:
        article = Article.objects.get(id = article_id)
    except DoesNotExist:
        raise Http404()
    return render(request, "all-news/article.html", {"article":article})

@login_required(login_url='/accounts/login/')
def new_article(request):
    current_user = request.user
    if request.method == 'POST':
        form = NewsArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.editor = current_user
            article.save()
    else:
        form = NewsArticleForm()
    
    return render(request, 'new_article.html',{"form":form})

def newsletter(request):
    name = request.POST.get('your_name')
    email = request.POST.get('email')

    recipient = NewsLetterRecipients(name=name, email=email)
    recipient.save()
    send_welcome_email(name, email)
    data = {'success':'You have been sucessfully added to mailing list'}
    return JsonResponse(data)


class MerchList(APIView):
    def get(self, request, format=None):
        all_merch = MoringaMerch.objects.all()
        serializer = MerchSerializer(all_merch, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = MerchSerializer(data = request.data)
        
        permission_classes = (IsAdminOrReadOnly,)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class MerchDescription(APIView):
    permission_classes = (IsAdminOrReadOnly,)

    def get_merch(self, pk):
        try:
            return MoringaMerch.objects.get(pk=pk)
        except MoringaMerch.DoesNotExist:
            return Http404

    def get(self, request, pk, format=None):
        merch = self.get_merch(pk)
        serializer = MerchSerializer(merch)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        merch = self.get_merch(pk)
        serializer = MerchSerializer(merch, request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        merch = self.get_merch(pk)
        merch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)