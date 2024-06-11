from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt 
from django.http import JsonResponse
from django.conf import settings
from .models import BlogPost
from pytube import YouTube
from pathlib import Path
from decouple import config
import assemblyai as aai
# import openai
import json

# Create your views here.
@login_required
def index(request):
    return render(request,'home.html')

@csrf_exempt
def generate_blog(request):
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
            
        except(KeyError,json.JSONDecodeError):
            return JsonResponse({'error':'Invalid data sent'},status=400)
        
        title = yt_title(yt_link)

        transcription = get_transcription(yt_link)
        
        if not transcription:
            return JsonResponse({'error':"Filed to get transcript"},status=500)
        
        ''' WHEN WE ACCESS generate_blog_from_transcription(transcription) FUNCTION THEN USE BELOW CODES

        # blog_content = generate_blog_from_transcription(transcription)
        # print(f"blog_content: {blog_content}")
        # if not blog_content:
        #     return JsonResponse({'errpr':"Failed to generate blog article"},status=500)        
        # return JsonResponse({'content':blog_content}) '''

        BlogPost.objects.create(
            user = request.user,
            yt_video_title = title,
            yt_video_link = yt_link,
            yt_video_transcript = transcription,
            # generator_content = blog_content,
        )

        
        return JsonResponse({'content':transcription})
    else:
        return JsonResponse({'error':'Invalid request method'},status=405)
    
def yt_title(link):
    yt = YouTube(link)
    title = yt.title
    return title

def download_audio(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    old_file = Path(out_file)
    base = old_file.stem    
    new_file = old_file.with_name(base + '.mp3')
    old_file.rename(new_file) 
    return new_file

def get_transcription(link):
    audio_file = download_audio(link)    
    aai.settings.api_key = config('AAI_API_KEY')  
    transcriber = aai.Transcriber()   
    transcript = transcriber.transcribe(str(audio_file))   
    return transcript.text

''' IF WE PAY FOR API KEY THEN WE CAN USE THIS FUNCTION

# def generate_blog_from_transcription(transcription):
#     openai.api_key = config('OPENAI_API_KEY')
#     prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it  based  on the transcript, but dont make it look like a youtube video, make it look like a proper blog article:\n\n{transcription}\n\nArticle:"

#     response = openai.completions.create(
#         model="gpt-3.5-turbo",
#         prompt=prompt,
#         max_tokens=1000
#     )
    
#     generated_content = response.choices[0].text.strip()
#     return generated_content '''

def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request,"all_blogs.html",{'blog_articles':blog_articles})

def blog_details(request, pk):
    blog_article_details = BlogPost.objects.get(id=pk)
    if request.user == blog_article_details.user:
        return render(request,'blog_details.html',{'blog_article_details':blog_article_details})
    else:
        return redirect('/')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('/')
        else:
            error_message = 'Invalid username or password'
            return render(request,'login.html',{'error_message':error_message})
    return render(request,'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']
        
        if password == repeatPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request,user)
                return redirect('/')
            except:
                error_message = 'Error creating account'
                return render(request, 'signup.html',{'error_message':error_message})
        
        else:
            error_message = 'Password do not match'
            return render(request,'signup.html',{'error_message':error_message})
    return render(request,'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')

