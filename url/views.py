from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json


from django.core.serializers import serialize
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render
from .models import URL
from rest_framework.decorators import api_view
from django.http import JsonResponse
import hashlib
from .serializers import URLSerializer
from rest_framework.response import Response
import json
import environ
from url_project.settings import SECRET_TOKEN, DEBUG
from django.views.decorators.csrf import csrf_exempt

def redirect_original_url(request, hash):
    try:
        url = URL.objects.get(hash=hash)
        url.visits += 1  # Increment visits count
        url.save()
        if DEBUG:
            return redirect(f'http://{url.url}')
        return redirect(f'https://{url.url}')
    except URL.DoesNotExist:
        return Response({'error': 'FORBIDDEN'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
def create_short_url(request):
    """
    не проверяем наличие csrf token на фронте
    """
    company = None
    title = None
    if 'url' in request.data:
        original_url = request.data['url']
        if 'company' in request.data:
            company = request.data['company']
        elif 'title' in request.data:
            title = request.data['title']
        hash_value = hashlib.md5(original_url.encode()).hexdigest()[:10]
        new_url = URL.objects.get_or_create(hash=hash_value, url=original_url, company=company, title=title)[0]
        serializer = URLSerializer(new_url)
        return Response(serializer.data)
    return Response({'error': 'FORBIDDEN'}, status=status.HTTP_403_FORBIDDEN)



@api_view(['POST'])
def get_list_url(request):
    """
        all - все компании кроме None
    """
    if SECRET_TOKEN in request.data.values():
        if 'company' in request.data.keys() and request.data['company'] != 'all':
            company = request.data['company']
            new_url = URL.objects.get(company=company)
            serializer = URLSerializer(new_url)
            return Response(serializer.data)
        else:
            # получаем список всех наименований компаний
            unique_companies = URL.objects.exclude(company__isnull=True).values_list('company', flat=True).distinct()
            print(unique_companies, 'unique_companies')
            # Преобразуем в список и удаляем возможные значения None
            filtered_companies = [company for company in unique_companies if company is not None]
            response_data = {
                'list_company': filtered_companies,
            }
            return Response(response_data, status=status.HTTP_200_OK)
    return Response({'error': 'FORBIDDEN'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
def delete_url(request, hash):
    if SECRET_TOKEN in request.data.values():
        try:
            url = URL.objects.get(hash=hash)
            url.delete()
            return Response('ok', status=status.HTTP_200_OK)
        except URL.DoesNotExist:
            return Response({'error': 'Short URL not found'}, status=404)
    return Response({'error': 'FORBIDDEN'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def get_url_stats(request, hash):
    """
        статистика по hash
    """
    try:
        url = URL.objects.get(hash=hash)
        serializer = URLSerializer(url)
        return Response(serializer.data)
    except URL.DoesNotExist:
        return Response({'error': 'Short URL not found'}, status=404)
    
def simple_ui(request):
    # urls = URL.objects.all()
    # return render(request, "index.html", {"urls": urls})
    return JsonResponse({'FORBIDDEN': '403'}, status=200)

