import os
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
import subprocess
# Create your views here.

class testAPIView(APIView):
    def get(self,request):
         # the terminal command that we want to run
         cmd = ['python3','manage.py','test']
         try:
            # run cmd in terminal
            run = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            # wait for running terminal command
            run.wait(timeout=settings.TEST_RUN_REQUEST_TIMEOUT_SECONDS) # 30 minutes
            # print output in terminal
            print(run.stdout.read())
            return JsonResponse({
             'status':'200',
             'message':'success',
            },status=200)
            
         except Exception as e:
             # if we encounter an error , this section will run
             return JsonResponse({
                 'status':'500',
                 'message':str(e) #error message
             },status = 500)
        