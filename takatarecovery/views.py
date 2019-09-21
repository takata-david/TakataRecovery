from django.shortcuts import render

# Create your views here.
import json as js
import pandas as pd
import requests
from .models import takatarecovery, makemodel
from araa import settings
import smtplib
import sys
from . forms import vinCheckForm, detailsForm, makeModelForm
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

#resultdf = pd.DataFrame()
vin = ""


def makemodel(request):
    return render(request, 'takatarecovery/makemodel.html')

def aboutus(request):
    return render(request, 'takatarecovery/about.html')

def privacy(request):
    return render(request, 'takatarecovery/privacy.html')

def contact(request):
    return render(request, 'takatarecovery/contact.html')

# Vin check
def home(request):
    totald = 0
    totalp = 0
    total = 0
    resultdf = pd.DataFrame()
    form = vinCheckForm(request.POST)
    form1 = detailsForm(request.POST)
    try:
        if request.method == 'POST':
            global vin

            vin = request.POST.get('vin')
            if (len(vin) == 17):
                url = "https://takatalive.com/api/takata/"+vin
                getRequest = requests.get(url)
                data = getRequest.json()
                starValue = js.loads(data)
                hasMatch = starValue['HasMatch']

                if hasMatch == "YES":
                    result = starValue['Result']
                    for k in result:
                        print(k['VIN'])
                        VehicleAirbagID = str(k['VehicleAirbagID'])
                        VehicleID = str(k['VehicleID'])
                        VIN = str(k['VIN'])
                        PRANum = str(k['PRANum'])
                        Make = str(k['Make'])
                        Model = str(k['Model'])
                        Series = str(k['Series'])
                        Year = str(k['Year'])
                        AirbagLocation = str(k['AirbagLocation'])
                        IsAlpha = str(k['IsAlpha'])
                        IsSubmitted = str(k['IsSubmitted'])
                        if(AirbagLocation == "Driver"):
                            totald = 75
                        else:
                            totalp = 90

                        #global resultdf

                        resultdf = resultdf.append(
                            {'VIN': VIN, 'Make': Make, 'Model': Model,
                             'Series': Series, 'Year': Year, 'AirbagLocation': AirbagLocation, 'Alpha': IsAlpha}, ignore_index=True)
                        #print(resultdf)
        else:
            context1 = {
                'form': form
            }
            return render(request, 'takatarecovery/index.html', context1)

        resultList = resultdf.values.tolist()
        total = totald + totalp
        print(total)

    except Exception:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    context = {
        'result': resultList,
        'total': total,
        'form1': form1
    }
    return render(request, 'takatarecovery/index-result.html', context)

#make-model check

def makeModelCheck(request):
    form = makeModelForm(request.POST)
    try:
        if request.method == 'POST':
            oem = request.POST.get('oem')
            model = request.POST.get('model')
            year = request.POST.get('year')

        else:
            locatedQuery = makemodel.objects.raw(
                'select id, oem, model, year, airbag, status from takatarecovery_makemodel')

            located = pd.DataFrame(locatedQuery)
            print(located)
            context = {
                'form': form
            }
            return render(request, 'takatarecovery/make-model.html', context)

    except Exception:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    context = {
        'form': form
    }
    return render(request, 'takatarecovery/make-model.html', context)


# Database storage and mail notification
def details(request):
    server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    server.starttls()
    MY_ADDRESS = 'takatarecovery@gmail.com'
    PASS = 'Takata001'
    server.login(MY_ADDRESS, PASS)

    #form = detailsForm(request.POST)
    email = "vedant@takatarecovery.com"
    flag = "Error"
    today = date.today()
    currentDate = today.strftime("%Y-%m-%d")
    print(currentDate)
    global vin
    print(vin)
    try:
        if request.method == 'POST':
            bname = request.POST.get('business_name')
            contactno = request.POST.get('contact_no')
            businessEmail = request.POST.get('email')
            print(bname)
            print(contactno)
            print(businessEmail)

            if(vin != ""):
                if(businessEmail != ""):
                    bmsg = MIMEMultipart()
                    bmsg['From'] = MY_ADDRESS
                    bmsg['To'] = businessEmail
                    bmsg['Subject'] = "TakataRecovery Website Confirmation"

                    message = "Hi,\n\n\tYour details are sent to ARAA.\n\tWe will contact you.\n\tThank you.\n\nRegards,\nTakata Recovery"

                    bmsg.attach(MIMEText(message, 'plain'))

                    server.send_message(bmsg)
                    del bmsg

                msg = MIMEMultipart()
                msg['From'] = MY_ADDRESS
                msg['To'] = email
                msg['Subject'] = "TakataRecovery Website Notification"

                if(bname != "" or contactno != "" or businessEmail != ""):
                    message = "Hi,\n\n\tFollowing business check the VIN: "+vin+"\n\tBusiness name: "+bname+"\n\tContact no: "+contactno+"\n\tEmail: "+businessEmail+"\n\tPlease, contact the business.\n\nRegards,\nTakata Recovery"

                    msg.attach(MIMEText(message, 'plain'))

                    server.send_message(msg)
                    instance = takatarecovery(vin = vin, business_name = bname, contact_no = contactno, email = businessEmail, date=currentDate)
                    instance.save()
                    flag = "Success"

                del msg
                server.quit()
                print("completed")

    except Exception:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    context = {
        'flag': flag
    }
    return render(request, 'takatarecovery/success.html', context)