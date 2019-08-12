from django.shortcuts import render,  redirect
from django.views import generic
from django.contrib.auth.decorators import login_required
import re
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from . models import vinfile, business
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from . forms import vinfileForm
import pandas as pd
import json as js
import requests
from . models import washed_vins, original_vins, vin_conflicts, wiki_vincodes, business, original_extension
from araa import settings
import io
import datetime
from django.db.models import Count
from django import template

# Create your views here.


def home(request):
    context = {
        'title': 'Wassup homie',
    }
    return render(request, 'vinwash/home.html', context)

@login_required
def dashboard(request):
    return render(request, 'vinwash/dashboard.html')


@login_required
def process(request):
    return render(request, 'vinwash/process.html')


'''
class FileCreateView(LoginRequiredMixin, CreateView):
    model = vinfile
    fields = ['filename', 'date', 'user', 'notes']
    #jimmy = business.objects.get(id=1)
    def form_valid(self, form):
        form.instance.business = business.objects.get(id=1)
        return super().form_valid(form)


class FileDetailView(DetailView):
    model = vinfile


def upload(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        print(uploaded_file.name)
        print(uploaded_file.size)
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, request.FILES['document'])
        url = fs.url(name)
        context = {
            'url': url
        }
        print(url)
    else:
        context = {
            'url': 'nothing to upload'
        }
    return render(request, 'vinwash/upload_useless.html', context)
'''


def file_list(request):
    return render(request, 'vinwash/file_list.html')


def original_vinsdb(df, fileid):

    '''
    list1 = original_vins.objects.values_list('vin', flat=True)
    vin_list = list(list1)
    print(vin_list)
    dup_vins = df[df['vin'].isin(vin_list)] # duplicate b/w 2 files
    print(dup_vins['vin'])
    dup_data = original_vins.objects.filter(vin__in=list(dup_vins['vin'])).values_list('vin', 'file_id')
    #dup_data = original_vins.objects.filter(vin__in=list(dup_vins))
    print(dup_data)
    for (vin, filid) in dup_data:
        instance = vin_conflicts(vin=vin, originalvins_business=filid, conflict_location='a', conflict_stocknumber='b',
                                 conflict_filename=fileid, cnflict_business_id=1)
        instance.save()

    df = df[~df['vin'].isin(vin_list)]

    for j in df.iterrows():
        vn = j[1]['vin']
        lc = j[1]['location']
        st = j[1]['stock']
        instance = original_vins(vin=vn, location=lc, stock_number=st, date='2019-07-24', file_id=fileid,
                                     business_id=1)
        instance.save()

    return df
    '''
    #return vin_list

'''
def validate_vins(df):
    df = df[df['vin'].apply(lambda x: len(x) == 17)]
    #df['vin'] = df['vin'].str.replace(['.', ',', ';', ':', '+', '-', '_', '=', '/'], '')
    df['vin'] = df['vin'].str.replace('i', '1')
    df['vin'] = df['vin'].str.replace('o', '0')
    return df
'''

def processcsv(df, fileid):

    #df1 = validate_vins(df)  #validate original vins
    df1 = original_vinsdb(df, fileid)  # save original vins to database

    dfToList = df1['vin'].tolist()
    url = "https://takatalive.com/api/takata/bulk"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=js.dumps(dfToList), headers=headers)
    p = r.json()
    j = js.loads(p)
    result = j['Result']

    resultdf = pd.DataFrame(columns=['VehicleAirbagID', 'VehicleID', 'VIN', 'PRANum', 'Make', 'Model', 'Series', 'Year',
                                     'AirbagLocation', 'IsAlpha', 'IsSubmitted'])
    if result != None:
        for k in result:
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

            resultdf = resultdf.append({'VehicleAirbagID': VehicleAirbagID,
                                        'VehicleID': VehicleID,
                                        'VIN': VIN,
                                        'PRANum': PRANum,
                                        'Make': Make,
                                        'Model': Model,
                                        'Series': Series,
                                        'Year': Year,
                                        'AirbagLocation': AirbagLocation,
                                        'IsAlpha': IsAlpha,
                                        'IsSubmitted': IsSubmitted
                                        }, ignore_index=True)

            instance = washed_vins(vehicleairbagid=VehicleAirbagID, vehicleid=VehicleID, vin=VIN, pranum=PRANum,
                                   make=Make, model=Model, series=Series, year=Year, airbaglocation=AirbagLocation,
                                   isalpha=IsAlpha, issubmitted=IsSubmitted, bagcollectiondate='2019-07-24',
                                   business_id=1)
            instance.save()
    return resultdf

    #return df1


def upload_file(request):
    if request.method == 'POST':
        form = vinfileForm(request.POST, request.FILES)
        if form.is_valid():
            bid = request.POST.get('business')
            udt = request.POST.get('date')
            print('business id after this')
            print(bid)

            uploaded_file = request.FILES['filename']
            file1 = pd.read_csv(uploaded_file, usecols=[0, 1, 2], encoding='latin1', sep=',')

            df = pd.DataFrame(data=file1)
            df.columns = ['vin', 'location', 'stock']
            df['vin'] = df['vin'].str.replace('.', '')
            df['vin'] = df['vin'].str.replace(',', '')
            df['vin'] = df['vin'].str.replace(';', '')
            df['vin'] = df['vin'].str.replace('\'', '')
            df['vin'] = df['vin'].str.replace(':', '')
            df['vin'] = df['vin'].str.replace('+', '')
            df['vin'] = df['vin'].str.replace('=', '')
            df['vin'] = df['vin'].str.replace('@', '')
            df['vin'] = df['vin'].str.replace('#', '')
            df['vin'] = df['vin'].str.replace('$', '')
            df['vin'] = df['vin'].str.replace('%', '')
            df['vin'] = df['vin'].str.replace('^', '')
            df['vin'] = df['vin'].str.replace('&', '')
            df['vin'] = df['vin'].str.replace('*', '')

            print(df)

            df = df[df['vin'].apply(lambda x: len(str(x)) == 17)]
            df['vin'] = df['vin'].str.replace('i', '1')
            df['vin'] = df['vin'].str.replace('o', '0')
            df = df.drop_duplicates(subset='vin', keep='first')

            list1 = original_vins.objects.values_list('vin', flat=True)
            vin_list = list(list1)
            # print(vin_list)
            dup_vins = df[df['vin'].isin(vin_list)]  # duplicate b/w 2 files
            # print(dup_vins['vin'])
            dup_data = original_vins.objects.filter(vin__in=list(dup_vins['vin'])).values_list('vin', 'file_id')
            # dup_data = original_vins.objects.filter(vin__in=list(dup_vins))
            # print(dup_data)

            df = df[~df['vin'].isin(vin_list)]

            if df.shape[0] > 0:
                forminstance = form.save()
                recordid = forminstance.pk
                for (vin, filid) in dup_data:
                    instance = vin_conflicts(vin=vin, previous_occurence_fileid=filid,
                                             current_occurence_fileid=recordid,
                                             conflict_location='', conflict_stocknumber='')
                    instance.save()

                print(wiki_vincodes.objects.values_list('id', 'code', 'make'))
                table_frame = pd.DataFrame(wiki_vincodes.objects.values_list('id', 'code', 'make'))
                table_frame.columns = ['id', 'code', 'make']
                print('table frame below this')
                print(table_frame)
                # codes = wiki_vincodes.objects.all()
                prefix_list = list(table_frame['code'])
                print(prefix_list)
                for j in df.iterrows():
                    vn = j[1]['vin']
                    lc = j[1]['location']
                    st = j[1]['stock']

                    pre3 = vn[0:3]
                    pre2 = vn[0:2]
                    if pre2 in prefix_list:
                        m_pre = pre2
                        m_oem = list(table_frame[table_frame['code'] == pre2]['id'])
                        print(m_oem[0])
                    elif pre3 in prefix_list:
                        m_pre = pre3
                        m_oem = list(table_frame[table_frame['code'] == pre3]['id'])
                        print(m_oem[0])
                    else:
                        m_pre = ''
                        m_oem = ''
                    instance = original_vins(vin=vn, location=lc, stock_number=st, date=udt, file_id=recordid,
                                             business_id=bid, wiki_id=m_oem)
                    instance.save()

                df1 = df
                dfToList = df1['vin'].tolist()
                url = "https://takatalive.com/api/takata/bulk"
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                r = requests.post(url, data=js.dumps(dfToList), headers=headers)
                p = r.json()
                j = js.loads(p)
                result = j['Result']

                resultdf = pd.DataFrame(
                    columns=['VehicleAirbagID', 'VehicleID', 'VIN', 'PRANum', 'Make', 'Model', 'Series', 'Year',
                             'AirbagLocation', 'IsAlpha', 'IsSubmitted'])
                if result != None:
                    for k in result:
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

                        resultdf = resultdf.append({'VehicleAirbagID': VehicleAirbagID,
                                                    'VehicleID': VehicleID,
                                                    'VIN': VIN,
                                                    'PRANum': PRANum,
                                                    'Make': Make,
                                                    'Model': Model,
                                                    'Series': Series,
                                                    'Year': Year,
                                                    'AirbagLocation': AirbagLocation,
                                                    'IsAlpha': IsAlpha,
                                                    'IsSubmitted': IsSubmitted
                                                    }, ignore_index=True)

                        instance1 = washed_vins(vehicleid=VehicleID, vin=VIN, pranum=PRANum,
                                                make=Make, model=Model, series=Series, year=Year,
                                                airbaglocation=AirbagLocation,
                                                isalpha=IsAlpha, issubmitted=IsSubmitted,
                                                bagcollectiondate="2015-11-22",
                                                file_id=recordid)
                        instance1.save()
                messages.add_message(request, messages.INFO, "Process executed successfully")
            else:
                messages.add_message(request, messages.INFO, "All vins in this file already exist in DB!!")

            return redirect('dashboard')
    else:
        form = vinfileForm()
    context = {
        'form': form
    }
    return render(request, 'vinwash/upload_file.html', context)


#def upload_automated(request):
def upload_bulk(request):
    meta = settings.MEDIA_ROOT + '\\' + 'filenames.csv'
    file1 = pd.read_csv(meta, usecols=[0, 1, 2, 3, 4, 5],  encoding='latin1',  sep=',')
    file1.columns = ['business', 'filename', 'date', 'coord', 'bid', 'filetype']
    metaframe = pd.DataFrame(data=file1)
    for j in metaframe.iterrows():
        bs = j[1]['business']
        fl = j[1]['filename']
        ftyp = j[1]['filetype']
        filepath = settings.MEDIA_ROOT + '\\electronic\\' + fl
        dt = j[1]['date']
        dt = datetime.datetime.strptime(dt, "%d/%m/%Y").strftime("%Y-%m-%d")
        cr = str(j[1]['coord'])
        bd = j[1]['bid']
        print(fl)
        # from here business files will be read.
        instance = vinfile(filename=fl, date=dt, user=cr, notes=' ', business_id=bd, filetype=ftyp)
        instance.save()
        fid = instance.id

        of = pd.read_csv(filepath, usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
                            encoding='latin1', sep=',')
        of.columns = ['vin', 'location', 'stock', 'image', 'model', 'year', 'inventoried', 'odoreading', 'engine',
                      'gearboxtype', 'gears', 'doors', 'site', 'registration', 'cod', 'enginenumber', 'purchasedate',
                      'fueltype', 'bodystyle', 'classification']

        df = of
        df['vin'] = df['vin'].str.replace('.', '')
        df['vin'] = df['vin'].str.replace(',', '')
        df['vin'] = df['vin'].str.replace(';', '')
        df['vin'] = df['vin'].str.replace('\'', '')
        df['vin'] = df['vin'].str.replace(':', '')
        df['vin'] = df['vin'].str.replace('+', '')
        df['vin'] = df['vin'].str.replace('=', '')
        df['vin'] = df['vin'].str.replace('@', '')
        df['vin'] = df['vin'].str.replace('#', '')
        df['vin'] = df['vin'].str.replace('$', '')
        df['vin'] = df['vin'].str.replace('%', '')
        df['vin'] = df['vin'].str.replace('^', '')
        df['vin'] = df['vin'].str.replace('&', '')
        df['vin'] = df['vin'].str.replace('*', '')

        df = df[df['vin'].apply(lambda x: len(str(x)) == 17)]
        df['vin'] = df['vin'].str.replace('i', '1')
        df['vin'] = df['vin'].str.replace('o', '0')
        df = df.drop_duplicates(subset='vin', keep='first')

        list1 = original_vins.objects.values_list('vin', flat=True)
        vin_list = list(list1)
        dup_vins = df[df['vin'].isin(vin_list)]  # duplicate b/w 2 files
        dup_data = original_vins.objects.filter(vin__in=list(dup_vins['vin'])).values_list('vin', 'file_id')
        recordid = fid
        if len(list(dup_vins['vin'])) > 0:
            for (vin, filid) in dup_data:
                e1 = vinfile.objects.get(id=filid)
                c1 = e1.business_id

                e2 = vinfile.objects.get(id=recordid)
                c2 = e2.business_id

                if c1 == c2:
                    pass
                else:
                    instance = vin_conflicts(vin=vin, previous_occurence_fileid=filid, current_occurence_fileid=recordid,
                                             conflict_location='', conflict_stocknumber='')
                    instance.save()

        df = df[~df['vin'].isin(vin_list)] #unique vins
        if df.shape[0] > 0:
            table_frame = pd.DataFrame(wiki_vincodes.objects.values_list('id', 'code', 'make'))
            table_frame.columns = ['id', 'code', 'make']
            prefix_list = list(table_frame['code'])
            for h in df.iterrows():
                vn = h[1]['vin']
                lc = h[1]['location']
                st = h[1]['stock']
                img = h[1]['image']
                ext = 'JPG'
                if pd.isnull(img):
                    loc = ''
                else:
                    loc = img + '.' + ext
                pre3 = vn[0:3]
                pre2 = vn[0:2]
                if pre2 in prefix_list:
                    m_oem = int(table_frame[table_frame['code'] == pre2]['id'])
                elif pre3 in prefix_list:
                    m_oem = int(table_frame[table_frame['code'] == pre3]['id'])
                else:
                    m_oem = ''

                instance = original_vins(vin=vn, location=lc, stock_number=st, date=dt, file_id=recordid,
                                         business_id=bd, wiki_id=m_oem, img=loc)
                instance.save()
                sdsf =  ['model', 'year', 'inventoried', 'odoreading', 'engine',
                 'gearboxtype', 'gears', 'doors', 'site', 'registration', 'cod', 'enginenumber', 'purchasedate',
                 'fueltype', 'bodystyle', 'classification']

                instance1 = original_extension(vin=vn, model=h[1]['model'], year=h[1]['year'], inventoried=h[1]['inventoried'],
                                              odoreading=h[1]['odoreading'], engine=h[1]['engine'], gearboxtype=h[1]['gearboxtype'],
                                              gears=h[1]['gears'], doors=h[1]['doors'], sute=h[1]['site'], registration=h[1]['registration'],
                                              cod=h[1]['cod'], enginenumber=h[1]['enginenumber'], purchasedate=h[1]['purchasedate'],
                                              fueltype=h[1]['fueltype'], bodystyle=h[1]['bodystyle'], classification=h[1]['classification'])
                instance1.save()

            df1 = df
            dfToList = df1['vin'].tolist()
            url = "https://takatalive.com/api/takata/bulk"
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.post(url, data=js.dumps(dfToList), headers=headers)
            p = r.json()
            j = js.loads(p)
            result = j['Result']

            resultdf = pd.DataFrame(
                columns=['VehicleAirbagID', 'VehicleID', 'VIN', 'PRANum', 'Make', 'Model', 'Series', 'Year',
                         'AirbagLocation', 'IsAlpha', 'IsSubmitted'])
            if result != None:
                for k in result:
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

                    stk_frame = df[df['vin'] == VIN]

                    if len(stk_frame['stock'].values) > 0:
                        stk = stk_frame['stock'].values[0]
                        lac = stk_frame['location'].values[0]
                    else:
                        stk = ''
                        lac = ''

                    resultdf = resultdf.append({'VehicleAirbagID': VehicleAirbagID,
                                                'VehicleID': VehicleID,
                                                'VIN': VIN,
                                                'PRANum': PRANum,
                                                'Make': Make,
                                                'Model': Model,
                                                'Series': Series,
                                                'Year': Year,
                                                'AirbagLocation': AirbagLocation,
                                                'IsAlpha': IsAlpha,
                                                'IsSubmitted': IsSubmitted
                                                }, ignore_index=True)

                    instance1 = washed_vins(vehicleid=VehicleID, vin=VIN, pranum=PRANum,
                                            make=Make, model=Model, series=Series, year=Year,
                                            airbaglocation=AirbagLocation,
                                            isalpha=IsAlpha, issubmitted=IsSubmitted, bagcollectiondate="2015-11-22",
                                            file_id=recordid, stock_number=stk, location=lac)
                    instance1.save()

    context = {
        'abc': 'prafull'
    }
    return render(request, 'vinwash/upload_file.html', context)


def vins_located(request):
    a = original_vins.objects.values('wiki_id').annotate(dcount=Count('wiki_id'))
    b = pd.DataFrame(a)
    b.columns = ['count', 'wiki_id']
    tf = pd.DataFrame(wiki_vincodes.objects.values('id', 'code', 'make'))
    tf.columns = ['code', 'id', 'make']
    print(tf)
    resultdf = pd.DataFrame()

    for j in b.iterrows():
        ct = j[1]['count']
        wid = j[1]['wiki_id']
        if len(wid) > 0:
            rs = tf[tf['id'] == int(wid)]
            print(rs)
            resultdf = resultdf.append({'make': rs['make'].values[0], 'code': rs['code'].values[0],
                                        'count': ct}, ignore_index=True)

    listt = resultdf.values.tolist()

    context = {
        'res': listt
    }
    return render(request, 'vinwash/report-1.html', context)


def vins_make_consl(request):
    #a = washed_vins.objects.filter(item=item).values_list('shared_note', flat=True).distinct()
    a = washed_vins.objects.values_list('make').annotate(dcount=Count('make')) # affected airbags
    a = pd.DataFrame(a)
    a.columns = ['make', 'count']

    makes = list(a['make'])

    q = washed_vins.objects.all().values('make').annotate(count=Count('vin', distinct=True)).order_by() # affected vins
    q = pd.DataFrame(q)
    q.columns = ['count', 'make']

    #d = washed_vins.objects.all().values('make').annotate(count=Count('vin', distinct=True)).filter(isalpha=True) #alpha
    d = washed_vins.objects.all().values('make').annotate(count=Count('vin')).filter(isalpha=True)  # alpha
    d = pd.DataFrame(d)
    d.columns = ['count', 'make']

    resultdf = pd.DataFrame()
    for j in a.iterrows():
        make = j[1]['make']
        airbags = j[1]['count']

        rs = q[q['make'] == make]
        affected_vins = rs['count'].values[0]

        rs1 = d[d['make'] == make]
        if len(rs1['count']) > 0:
            alpha = rs1['count'].values[0]
        else:
            alpha = 0

        resultdf = resultdf.append({'make': make, 'airbags': airbags,
                                    'vins': affected_vins, 'alpha': alpha}, ignore_index=True)
        print(make, airbags, affected_vins, alpha)

    listt = resultdf.values.tolist()
    #print(a)
    #print(q)

    #print(list(a['make']))
    #print(a)

    context = {
        'table': listt
    }
    return render(request, 'vinwash/report-2.html', context)


def vin_lookup(request, vin):
    a = vin
    dd = original_vins.objects.all().values('img', 'date', 'stock_number', 'location', 'business_id',
                                           'file_id', 'wiki_id').filter(vin=a).count()
    if dd > 0:
        d = original_vins.objects.all().values('img', 'date', 'stock_number', 'location', 'business_id',
                                                    'file_id', 'wiki_id').filter(vin=a)


        #print(dd)

        d = pd.DataFrame(d)
        #print(d['img'].values[0])
        listt = d.values.tolist()
        listt = listt[0]
        #print(listt)
        biz = business.objects.all().values('bname', 'state').filter(id=listt[0])
        biz = pd.DataFrame(biz)
        listt1 = biz.values.tolist()
        listt1 = listt1[0]

        if listt[3] != None:
            path = settings.MEDIA_ROOT + '\\manual\\' + str(listt[0]) + listt[3]
            context = {
                'vals': listt,
                'path': path,
                'folder': 'manual',
                'biz': listt1
            }
        else:
            filid = listt[2]
            print(filid)
            filname = vinfile.objects.values('filename').filter(id=filid)
            print(filname[0]['filename'])

            print('vin has electronic file as source')
            path = settings.MEDIA_ROOT + '\\electronic\\' + filname[0]['filename']
            print(path)
            context = {
                'elec': filname[0]['filename'],
                'vals1': listt,
                'path': path,
                'folder': 'manual',
                'biz': listt1
            }
    else:
        context = {
            'notfound': 'Vin Not Found in business files'
        }
    return render(request, 'vinwash/vinlookup.html', context)
