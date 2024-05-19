from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.renderers import JSONRenderer

from django.core.serializers import serialize
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render
from .models import URL
from django.http import JsonResponse
import hashlib
from .serializers import URLSerializer
from url_project.settings import SECRET_TOKEN, DEBUG


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
    Create a short URL without checking CSRF token on the front end.
    """
    if request.method == 'POST':
        original_url = request.data.get('url')
        if not original_url:
            return Response({'error': 'URL is required.'}, status=status.HTTP_400_BAD_REQUEST)

        company = original_url.split('.')[0]
        title = request.data.get('title')

        try:
            hash_value = hashlib.sha256(original_url.encode()).hexdigest()[:10]
            new_url, created = URL.objects.get_or_create(hash=hash_value,
                                                         defaults={'url': original_url, 'company': company,
                                                                   'title': title})
            if not created:
                return Response({'message': 'URL already exists.', 'hash': hash_value}, status=status.HTTP_409_CONFLICT)

            serializer = URLSerializer(new_url)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'error': 'Invalid request method.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def get_list_url(request):
    """
    all - все компании кроме None
    """
    if request.method == 'POST':
        if 'SECRET_TOKEN' in request.data and request.data['SECRET_TOKEN'] == '23456789098765432w3e4r5tydcfvgbhn':
            if 'company' in request.data and request.data['company'] != 'all':
                company = request.data['company']
                try:
                    new_url = URL.objects.get(company=company)
                    serializer = URLSerializer(new_url)
                    return Response(serializer.data)
                except URL.DoesNotExist:
                    return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                # получаем список всех наименований компаний
                unique_companies = URL.objects.exclude(company__isnull=True).values_list('company',
                                                                                         flat=True).distinct()
                filtered_companies = [company for company in unique_companies if company is not None]
                return Response({'list_company': filtered_companies}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid or missing token"}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
def delete_url(request, hash):
    if request.method == 'POST':
        if SECRET_TOKEN in request.data.values():
            try:
                url = URL.objects.get(hash=hash)
                url.delete()
                return Response('ok', status=status.HTTP_200_OK)
            except URL.DoesNotExist:
                return Response({'error': 'Short URL not found'}, status=404)


@csrf_exempt
@api_view(['POST'])
def delete_company(request, company):
    if request.method == 'POST':
        company = request.data.get('company')
        if SECRET_TOKEN in request.data.values() and company:
            try:
                url = URL.objects.filter(company=company).delete()
                return Response('ok', status=status.HTTP_200_OK)
            except URL.DoesNotExist:
                return Response({'error': 'company not allowed'}, status=404)


@api_view(['POST'])
def all_company_urls(request, company):
    if request.method == 'POST':
        if SECRET_TOKEN in request.data.values():
            try:
                new_url = URL.objects.filter(company=company)
                serializer = URLSerializer(new_url)
                return Response(serializer.data)
            except URL.DoesNotExist:
                return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
            except URL.DoesNotExist:
                return Response({'error': 'Short URL not found'}, status=404)


@api_view(['POST'])
def get_url_stats(request, hash):
    """
        статистика по hash
    """
    if request.method == 'POST':
        try:
            url = URL.objects.get(hash=hash)
            serializer = URLSerializer(url)
            return Response(serializer.data)
        except URL.DoesNotExist:
            return Response({'error': 'Short URL not found'}, status=404)


def simple_ui(request):
    urls = URL.objects.all()
    return render(request, "index.html", {"urls": urls})
    # return JsonResponse({'FORBIDDEN': '403'}, status=200)
