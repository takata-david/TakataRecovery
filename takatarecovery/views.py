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
Make = ""
Model = ""
Year = ""
total = 0

def makemodel1(request):
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
                        global Make
                        Make = str(k['Make'])
                        global Model
                        Model = str(k['Model'])
                        Series = str(k['Series'])
                        global Year
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
        global total
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
    yearFromDB = []
    resultList = []
    flag = 0
    try:
        if request.method == 'POST':
            oem1 = request.POST.get('oem')
            model1 = request.POST.get('model1')
            year = request.POST.get('year')

            val = makemodel.objects.values('oem', 'model', 'year', 'airbag', 'status').filter(oem=oem1,
                                                                                              model=model1)

            values = pd.DataFrame(val)
            print(values)

            #entering year values to list only if below condition is correct
            if oem1 != "" and model1 != "" and year != "" and len(values) > 0:
                for y in values['year']:
                    yStr = str(y)
                    print(yStr)
                    if "," in yStr and "-" in yStr:
                        yStr1 = yStr.split(', ')
                        print(yStr1)
                        for yS in yStr1:
                            yStr2 = yS.split('-')
                            for yo in yStr2:
                                yearFromDB.append(yo)
                            print(yStr2)
                    elif "-" in yStr:
                        yStr2 = yStr.split('-')
                        for yo in yStr2:
                            yearFromDB.append(yo)
                        print(yStr2)
                    else:
                        yearFromDB.append(yStr)
                        continue

                print(yearFromDB)
                print(year)
                #Year check based on year values in db
                if len(yearFromDB) == 4:
                    y1 = int(yearFromDB[0])
                    y2 = int(yearFromDB[1])
                    y3 = int(yearFromDB[2])
                    y4 = int(yearFromDB[3])

                    for x in range(y1, y2+1):
                        for y in range(y3, y4+1):
                            if int(year) == x or int(year) == y:
                                flag = 1
                elif len(yearFromDB) == 3:
                    y1 = int(yearFromDB[0])
                    y2 = int(yearFromDB[1])
                    y3 = int(yearFromDB[2])

                    if int(year) == y3:
                        flag = 1
                    else:
                        for y in range(y1, y2+1):
                            if int(year) == y:
                                flag = 1
                elif len(yearFromDB) == 2:
                    y1 = int(yearFromDB[0])
                    y2 = int(yearFromDB[1])

                    for y in range(y1, y2+1):
                        if int(year) == y:
                            flag = 1
                else:
                    y1 = int(yearFromDB[0])

                    if int(year) == y1:
                        flag = 1

                if flag == 1:
                    resultList = values.values.tolist()
                    print(resultList)
                else:
                    print("Not a recall vehicle!!")
        else:

            context = {
                'form': form
            }
            return render(request, 'takatarecovery/makemodel.html', context)

    except Exception:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    context = {
        'form': form,
        'result': resultList
    }
    return render(request, 'takatarecovery/makemodel.html', context)


# Database storage and mail notification
def details(request):
    server = smtplib.SMTP(host='smtp.office365.com', port=587)
    server.starttls()
    MY_ADDRESS = 'donotreply@takatarecovery.com'
    PASS = 'Takata001'
    server.login(MY_ADDRESS, PASS)

    #form = detailsForm(request.POST)
    email = "admin@takatarecovery.com"
    flag = "Error"
    today = date.today()
    currentDate = today.strftime("%Y-%m-%d")
    source = 'Website'
    location = ""
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

            if(total == 165):
                location = "Both"
            elif(total == 90):
                location = "Passenger"
            elif(total == 75):
                location = "Driver"

            if(vin != ""):
                if(businessEmail != ""):
                    bmsg = MIMEMultipart()
                    bmsg['From'] = MY_ADDRESS
                    bmsg['To'] = businessEmail
                    bmsg['Subject'] = "Takata Recovery Program – Compensation for Affected Airbags"

                    message = "Thank you for registering an Affected VIN for recovery on behalf the vehicle manufacturer.\n\n" \
                              "Details of Undeployed Takata Affected Airbags for which you will receive compensation are:\n" \
                              "\tVIN: "+vin+"\n"+ "" \
                              "\tMake: "+Make+"\n\tModel: "+Model+"\n\tYear: "+str(Year)+"\n\tPassenger/Drive/Both: "+location+"\n\tCompensation: "+str(total)+" AUD\n" \
                              "\tContact Name: "+bname+"" \
                                                       "\n\tContact Number: "+str(contactno)+"\n\tContact email: "+businessEmail+"\n\n" \
                              "Deployed Airbags may qualify for Certificate of Destruction Compensation*\n\nWe will contact you within 48 hours to arrange recovery and compensation.\n\nKind regards,\n\nDavid Nolan\nExecutive Director\nAuto Recyclers Association of Australia"

                    bmsg.attach(MIMEText(message, 'plain'))

                    server.send_message(bmsg)
                    del bmsg

                msg = MIMEMultipart()
                msg['From'] = MY_ADDRESS
                msg['To'] = email
                msg['Subject'] = "Takata Recovery Program – Compensation for Affected Airbags"

                if(bname != "" or contactno != "" or businessEmail != ""):
                    message = "Thank you for registering an Affected VIN for recovery on behalf the vehicle manufacturer.\n\n" \
                              "Details of Undeployed Takata Affected Airbags for which you will receive compensation are:\n" \
                              "\tVIN: " + vin + "\n" + "" \
                                                       "\tMake: " + Make + "\n\tModel: " + Model + "\n\tYear: " + str(
                        Year) + "\n\tPassenger/Drive/Both: " + location + "\n\tCompensation: " + str(total) + " AUD\n" \
                                                                                                              "\tContact Name: " + bname + "" \
                                                                                                                                           "\n\tContact Number: " + str(
                        contactno) + "\n\tContact email: " + businessEmail + "\n\n" \
                        "Deployed Airbags may qualify for Certificate of Destruction Compensation*\n\nWe will contact you within 48 hours to arrange recovery and compensation.\n\nKind regards,\n\nDavid Nolan\nExecutive Director\nAuto Recyclers Association of Australia"

                    msg.attach(MIMEText(message, 'plain'))

                    server.send_message(msg)
                    instance = takatarecovery(vin = vin, business_name = bname, contact_no = contactno, email = businessEmail, date=currentDate, source=source)
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