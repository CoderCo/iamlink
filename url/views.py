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
        return HttpResponseNotFound("No Redirect")


@csrf_exempt
@api_view(['POST'])
def get_list_url(request):
    """
    all - все компании кроме None
    """
    try:
        list_data = request.data
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON format in the request'}, status=status.HTTP_400_BAD_REQUEST)

    if SECRET_TOKEN in list_data:
        if 'company' in list_data and list_data['company'] != 'all':
            # получаем сведения о конкретной компании
            company = list_data['company']
            list_company = URL.objects.filter(company=company)
            list_company_json = list(list_company.values())
            return Response({'list_company': list_company_json}, status=status.HTTP_200_OK)
        elif list_data['company'] == 'all':
            # получаем список всех наименований компаний
            unique_companies = URL.objects.exclude(company__isnull=True).values_list('company', flat=True).distinct()
            # Преобразуем в список и удаляем возможные значения None
            filtered_companies = [company for company in unique_companies if company is not None]
            return Response({'unique_companies': filtered_companies}, status=status.HTTP_200_OK)
    return Response({'error': 'FORBIDDEN'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
def get_list_url(request):
    """
        all - все компании кроме None
    """
    json_dumps = json.dumps(list(request.data.values()), indent=2)
    list_data = json.loads(json_dumps)
    if SECRET_TOKEN in list_data:
        if 'company' in request.data and request.data['company'] != 'all':
            # получаем сведения о конкретной компании
            company = request.data['company']
            list_company = URL.objects.filter(company=company)
            list_company = json.dumps(list(list_company.values()), indent=2)
            list_company_json = json.loads(list_company)
            return JsonResponse({'list_company': f'{list_company_json}'}, status=200)
        elif request.data['company'] == 'all':
            # получаем список всех наименований компаний
            unique_companies = URL.objects.exclude(company__isnull=True).values_list('company', flat=True).distinct()
            # Преобразуем в список и удаляем возможные значения None
            filtered_companies = [company for company in unique_companies if company is not None]
            # Преобразуем список в JSON
            json_data = json.dumps(filtered_companies, separators=(',', ':')).translate(str.maketrans('', '', '[]"'))
            return JsonResponse({'unique_companies': f'{json_data}'}, status=200)
    return JsonResponse({'error': 'FORBIDDEN'}, status=403)


@api_view(['POST'])
def delete_url(request, hash):
    json_dumps = json.dumps(list(request.data.values()), indent=2)
    list_data = json.loads(json_dumps)
    # hash = request.data['hash']
    if SECRET_TOKEN in list_data:
        try:
            url = URL.objects.get(hash=hash)
            url.delete()
            return JsonResponse({'ok': f'delete{url}'}, status=200)
        except URL.DoesNotExist:
            return Response({'error': 'Short URL not found'}, status=404)
    return JsonResponse({'error': 'FORBIDDEN'}, status=403)

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

