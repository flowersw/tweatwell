# Create your views here.
import sys, types
from django.http import HttpResponse, Http404,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from tweatwell import settings
from tweatwell.accounts.models import UserProfile
from tweatwell.web.utils import handle_uploaded_file, query_restcat
from tweatwell.web.pointsrank.models  import PointsRank
from tweatwell.web.questionstips.models  import QuestionTips
from tweatwell.web.awards.models  import Award
from tweatwell.web.upload.forms import PickFruitForm, PickVeggieForm
import datetime, os
import pycurl
import StringIO, json, types
from operator import itemgetter, attrgetter


def home_index(request, error=None):
    responsedict={'code': 500, 'bodylist':[]}
    commentslist=[]
    fruitform = PickFruitForm()
    veggieform = PickVeggieForm()
    all={'checkins': 0,
         'points': 0,
         'fruit': 0,
         'vegatble': 0,
         'alcohol': 0,
         'water': 0,
         'junk': 0,
         'protien': 0,
         'drinks': 0,
         'carb': 0,
         'dairy': 0,
         'pointspoll': 0,
         'coachespoll':0,
         'gender': 0}
    
    
    qt=QuestionTips.objects.get(pk=1)

    try:
        u=User.objects.get(username=request.user)
        awards =Award.objects.filter(user=u)
        
        PresidentAward=False
        ProfessorAward=False
        DeanAward=False
        SparkpeopleAward=False
        EventAward=False
        for a in awards:
            if a.award_class=="President":
                PresidentAward=True
            if a.award_class=="Dean":
                DeanAward=True
            if a.award_class=="Professor":
                ProfessorAward=True    
            if a.award_class=="Sparkpeople":
                SparkpeoplePresidAward=True    
            if a.award_class=="Event":
                EventAward=True
        
        
    except(User.DoesNotExist):
        return HttpResponseRedirect('/login')
    try:    
        p=u.get_profile()
    except(UserProfile.DoesNotExist):
        return HttpResponseRedirect('/login')  
        
    try:
        pr=PointsRank.objects.get(user=u)
        all['pointspoll']=pr.rank
    except(PointsRank.DoesNotExist):
        all['pointspoll']=0
        
         
    try:
        #get every transaction for this user
        URL="%sapi/omhe/all/%s/" % (settings.RESTCAT_SERVER, u.email)
        responsedict=query_restcat(URL)
        #print responsedict
        if responsedict['code']==200:
            num_transactions=len(responsedict['bodylist'])
            all['checkins']=num_transactions
            print "numtx=",num_transactions
            for j in reversed(responsedict['bodylist']):
                if type(j)==dict:
                    if j.has_key('omhe'):
                        if j['omhe']=="veg":
                            all['vegatble']=all['vegatble']+1
                        
                        if j['omhe']=='frt':	
                            all['fruit']=all['fruit']+1
                            
                        if j['omhe']=='alc':	
                            all['alcohol']=all['alcohol']+1
                            
                        if j['omhe']=='wtr':	
                            all['water']=all['water']+1
                            
                        if j['omhe']=='ptn':	
                            all['protien']=all['protien']+1
                            
                        if j['omhe']=='crb':	
                            all['carb']=all['carb']+1
                            
                        if j['omhe']=='jnk':	
                            all['junk']=all['junk']+1
                            
                        if j['omhe']=='dry':	
                            all['dairy']=all['dairy']+1
                        
                        if j['omhe']=='drk':	
                            all['drinks']=all['drinks']+1

                    if j.has_key('points'):
                        all['points']=int(all['points']) + int(j['points'])
                            
                    #if j.has_key('pbf_numeric'):
                    #    all['pbf_numeric']=j['pbf_numeric']
 
                    
                    if j.has_key('ci_payload') and not j.has_key('idr'):
                        all['status']=j['ci_payload']
                        
                    if j.has_key('omhe') and not j.has_key('idr'):
                        all['status']=j['texti']  
 
        else:
            msg="Error Fetching your data: HTTPCODE=%s %s" % (
                                        str(responsedict['code']),
                                        str(responsedict['bodylist']))
            error=msg
        #get last 50 tx every transaction for the population
        URL="%sapi/population/omhe/50/" % (settings.RESTCAT_SERVER)
        responsedict=query_restcat(URL)
        
        if responsedict['code']==200:
            commentslist=[]
            commentsguidlist=[]
            for i in responsedict['bodylist']:
                i['comments']=[]
                i['display_status']=None
                i['id']=i['_id']
                del i['_id']
                try:
                    u=User.objects.get(email=i['subj'])
                except:
                    u=None
                if u:
                    try:
                        p=u.get_profile()
                        i['username']=u.username
                        i['display_name']=u.username
                    except(UserProfile.DoesNotExist):
                        p=None
                    except:
                        pass
                
                #display comments
                if (i['omhe'])=="ci" and (not i.has_key('idr')):
                    i['showme']=True
                    ds="%s." % (i['ci_payload'])
                    i['display_status']=ds
                    
                if i.has_key('idr'):
                    ds="%s." % (i['ci_payload'])
                    i['display_status']=ds
                    commentslist.append(i)
                    i['showme']=False
                    
                display_commands=['frt', 'ptn', 'veg', 'wtr', 'alc', 'jnk', 'ans']    
                if (display_commands.__contains__(i['omhe'])) and (not i.has_key('idr')):
                    i['showme']=True
                    ds="%s" % (i['texti'])
                    i['display_status']=ds
                
            responsedict['bodylist']= sorted(responsedict['bodylist'], key=itemgetter('sinceid'), reverse=True)
                
        else:
            responsedict['bodylist']=None
        
        return render_to_response(
            'index.html',
            {
            'PresidentAward':PresidentAward,
            'ProfessorAward': ProfessorAward,
            'DeanAward': DeanAward,
            'SparkpeopleAward': SparkpeopleAward,
            'EventAward': EventAward,
            'commentslist':commentslist,
            'publicfeed': responsedict['bodylist'],
            'all': all,
            'qt': qt,
            'awards': awards,
            'veggieform': veggieform,
            'fruitform': fruitform,
             },
            context_instance = RequestContext(request),)    
        

    except:
        msg="""Something went wrong. HTTP/500."""
        error= msg + str(sys.exc_info())
        #print error
        return render_to_response(
            'index.html',
            {'error':error,
             'ci': responsedict['bodylist'],
            'all': all,
            },
            context_instance = RequestContext(request),)
