
import requests
from django.conf import settings
from django.shortcuts import render,redirect

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from .models import *
from .serializer import *
from django.contrib.auth import logout,authenticate, login
from django.http import JsonResponse,HttpResponseBadRequest,HttpResponse
from oauth2_provider.models import AccessToken, Application
from django.utils import timezone
from django.contrib.auth.models import User
from urllib.parse import urlencode
from datetime import timedelta


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @protected_resource()
def hello_world(request):
    print("Hello World")
    return JsonResponse({'message': 'Hello, World!'},status=200)



# @login_required
@api_view(['GET'])
def logout_view(request):   
    logout(request)
    return Response({'message': 'logged out, World!'})





@api_view(['GET'])
@permission_classes([IsAuthenticated])
# @login_required
def user_projects_view(request):
    user = request.user
    print("helllo")
    # print("User ",request.headers)
    if not user:
        return Response({'error': 'User not found'}, status=404)
    print("User ",user)
    projects = Project.objects.filter(user=user)
    serializer = ProjectSerializer(projects, many=True)
    # print("Projects ",serializer.data)
    return Response({'projects': serializer.data}, status=200)






def google_auth_redirect(request):
    print("google_auth_redirect")
    google_auth_url = "https://accounts.google.com/o/oauth2/auth"
    redirect_uri = request.build_absolute_uri(settings.REDIRECT_URI)
    client_id = settings.CLIENT_ID
    scope = "openid email profile"  # Specify scopes as needed
    response_type = "code"
    state = "your_state_parameter"  # Optional: Include a state parameter for security

    auth_params = {
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'response_type': response_type,
        'scope': scope,
        'state': state,
    }

    # Construct the authorization URL
    auth_url = f"{google_auth_url}?{urlencode(auth_params)}"

    return redirect(auth_url)



def get_user_info(access_token):
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token}
    response = requests.get(userinfo_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to retrieve user info")
    
def google_auth_callback(request):
    print("google_auth_callback")
    error = request.GET.get('error')
    if error:
        return HttpResponseBadRequest(f"Authorization error: {error}")

    code = request.GET.get('code')
    state = request.GET.get('state')  # Optional: Validate state parameter if used

    if not code:
        return HttpResponseBadRequest("Authorization code not received")

    try:
        access_token, expires_in = exchange_code_for_token(code)
        user_info = get_user_info(access_token)

        # Authenticate the user in Django
        email = user_info['email']
        username = user_info.get('name', email)

        user, created = User.objects.get_or_create(email=email, defaults={'username': username})

        # If user was created, you can set additional fields here
        if created:
            user.set_unusable_password()  # User cannot login with a password
            user.save()

        # Log the user in
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        print("User ",settings.CLIENT_ID)
        print("Login Done")
        application = Application.objects.get(client_id=settings.CLIENT_ID)
        print("Application ",application)
    # Set expiration date
        expires = timezone.now() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)

        # Generate token
        token_model = AccessToken(
            user=user,
            scope='read write',  # Set appropriate scopes
            expires=expires,
            token=access_token,
            application=application
        )
        token_model.save()
        print("Access Token created")
        streamlit_url = 'http://localhost:8501'  # Replace with your Streamlit app URL
        token_param = urlencode({'token': access_token})
        redirect_url = f"{streamlit_url}/?{token_param}"

        return redirect(redirect_url)

    except Exception as e:
        return HttpResponseBadRequest(f"Failed to retrieve access token: {str(e)}")


def exchange_code_for_token(authorization_code):
    token_url = 'https://oauth2.googleapis.com/token'
    redirect_uri = settings.REDIRECT_URI
    client_id = settings.CLIENT_ID
    client_secret = settings.CLIENT_SECRET

    data = {
        'code': authorization_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
    }

    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        expires_in = token_data.get('expires_in')
        return access_token, expires_in
    else:
        # Handle token exchange failure
        error_message = f"Failed to retrieve access token: {response.status_code}, {response.text}"
        raise Exception(error_message)

    
     # Redirect to a profile page or another relevant view



@api_view(['POST'])
def save_research_paper(request):
    print("Save Research Paper",request.data)
    serializer = ResearchPaperSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from bs4 import BeautifulSoup
import requests

def scrap(request):
# Sample URL (replace with actual website)
    url = "https://www.researchgate.net/publication/372878456_Deep_Learning_in_the_Ubiquitous_Human-Computer_Interactive_6G_Era_Applications_Principles_and_Prospects"

    # Send GET request and get HTML content
    response = requests.get(url)
    content = response.content
    print(content)
    # Parse HTML content
    soup = BeautifulSoup(content, "html.parser")

    # Define elements to extract (replace with appropriate class names/tags)
    title_element = soup.find("h1", class_="paper-title")
    author_element = soup.find("div", class_="author-list")
    abstract_element = soup.find("p", class_="abstract")

    # Extract data (modify based on element structure)
    title = title_element.text.strip() if title_element else None
    authors = [author.text.strip() for author in author_element.find_all("span", class_="author-name")] if author_element else None
    abstract = abstract_element.text.strip() if abstract_element else None

    # Print scraped data (modify for storage or export)
    print(f"Title: {title}")
    print(f"Authors: {', '.join(authors) if authors else None}")
    print(f"Abstract: {abstract}")
    return render(request, "intex.html", {"title": content})

import requests
from bs4 import BeautifulSoup
# import spacy
import re

# Load SpaCy model
# nlp = spacy.load("en_core_web_sm")

def scrape_text_from_webpage(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    session = requests.Session()
    response = session.get(url, headers=headers)
    print("Retrieved the webpage content.",response.status_code)
    if response.status_code == 200:
        print("Successfully retrieved the webpage content.")
        soup = BeautifulSoup(response.content, 'html.parser')
        text_content = soup.get_text(separator='\n')
        print("Successfully parsed the webpage content.")
        return text_content
    else:
        return ""

def extract(text):
    # Process the text with SpaCy NLP model
    # doc = nlp(text)
    
    # Custom rules to extract information
    title = re.search(r'Title: (.*)', text)
    authors = re.search(r'Authors:(.*)', text)
    abstract = re.search(r'Abstract:(.*?)(\n\n|\nFigure)', text, re.DOTALL)
    
    title_text = title.group(1).strip() if title else "Title not found"
    authors_text = authors.group(1).strip() if authors else "Authors not found"
    abstract_text = abstract.group(1).strip() if abstract else "Abstract not found"
    
    # Clean up authors text
    authors_text = authors_text.replace('Show all', '')
    
    return {
        "title": title_text,
        "authors": authors_text,
        "abstract": abstract_text
    }

def extract_information(text):
    url = 'https://www.researchgate.net/publication/372878456_Deep_Learning_in_the_Ubiquitous_Human-Computer_Interactive_6G_Era_Applications_Principles_and_Prospects' 
    text_content = scrape_text_from_webpage(url)
    if text_content:
        info = extract(text_content)
        print("Title:", info['title'])
        print("Authors:", info['authors'])
        print("Abstract:", info['abstract'])
    else:
        print("Failed to retrieve or parse the webpage content.")
    return JsonResponse(info)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests

@csrf_exempt
def url_headers(request):
    print("URL Headers")
    if request.method == 'POST':
        data = json.loads(request.body)
        print("Data ",data)
        url = data.get('url')
        headers = data.get('headers')
    #     headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    # }

        
        # Fetch the content of the webpage
        print("URL:", url)
        # print("Headers:", headers)
        response = requests.get(url)
        # print(response)
        if response.status_code == 200:
            print("Successfully retrieved the webpage content.")
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text(separator='\n')
            print("Successfully parsed the webpage content.",text_content)
             # Print first 1000 characters of content for brevity
            llamas = llama(text_content)
            if llamas:
                print("Title:", llamas.get('title', 'Title not found'))
                print("Authors:", llamas.get('authors', 'Authors not found'))
                print("Abstract:", llamas.get('abstract', 'Abstract not found'))
                print("Introduction:", llamas.get('introduction', 'Introduction not found'))
            else:
                print("Failed to retrieve or parse the webpage content.")   
            return JsonResponse({'status': 'success', 'message': 'Data received', 'content': llamas})
        else:
            print("Failed to retrieve content.",response.status_code)
            return JsonResponse({'status': 'failure', 'message': 'Failed to retrieve content', 'status_code': response.status_code})
    return JsonResponse({'status': 'failure', 'message': 'Invalid request method'}, status=400)

# Load model directly
# from transformers import AutoTokenizer, AutoModelForCausalLM

# tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-70b-chat-hf")
# model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-70b-chat-hf")
from transformers import LlamaTokenizer, LlamaForCausalLM, pipeline

model_name = "meta-llama/Llama-2-7b-hf"

tokenizer = LlamaTokenizer.from_pretrained(model_name)
model = LlamaForCausalLM.from_pretrained(model_name)

# Step 3: Create a pipeline for generating responses
chatbot_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)



from transformers import pipeline

def llama(text):
    nlp = pipeline("question-answering", model="meta-llama/Llama-2-7b-chat-hf")
    
    questions = {
        "title": "What is the title of the paper?",
        "authors": "Who are the authors of the paper?",
        "abstract": "What is the abstract of the paper?",
        "introduction": "What is the introduction of the paper?"
    }
    
    answers = {}
    for key, question in questions.items():
        result = nlp(question=question, context=text)
        answers[key] = result['answer']
    
    return answers
