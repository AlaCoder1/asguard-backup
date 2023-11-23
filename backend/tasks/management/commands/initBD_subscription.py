from backend.subscription.models import *
from django.core.management.base import BaseCommand




class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        initBD_organization()

        #BASE
        initBD_plan("Base",800)
        
        initBD_plansFeatures("management users",1)
        initBD_plansFeatures("Firewall",1)
        initBD_plansFeatures("ZTNA",1)
        initBD_plansFeatures("LDAP",1)
        
        #FULL
        initBD_plan("Full",1200)
        
        initBD_plansFeatures("management users",2)
        initBD_plansFeatures("Firewall",2)
        initBD_plansFeatures("ZTNA",2) 
        initBD_plansFeatures("LDAP",2)
        initBD_plansFeatures("Double Masque",2)
        initBD_plansFeatures("CASB",2)
        initBD_plansFeatures("SWG",2)
        initBD_plansFeatures("Anti-virus",2)
        
        #Custom1
        initBD_plan("Custom1",950)
        
        initBD_plansFeatures("Firewall",3)
        initBD_plansFeatures("ZTNA",3) 
        initBD_plansFeatures("LDAP",3)
        initBD_plansFeatures("Double Masque",3)
        
        #Custom2
        initBD_plan("Custom2",950)
        
        initBD_plansFeatures("Firewall",4)
        initBD_plansFeatures("ZTNA",4) 
        initBD_plansFeatures("LDAP",4)
        initBD_plansFeatures("CASB",4)
        
        #Custom3
        initBD_plan("Custom3",900)
        
        initBD_plansFeatures("Firewall",5)
        initBD_plansFeatures("ZTNA",5) 
        initBD_plansFeatures("LDAP",5)
        initBD_plansFeatures("SWG",5)
        
        #Custom4
        initBD_plan("Custom4",900)
        
        initBD_plansFeatures("Firewall",6)
        initBD_plansFeatures("ZTNA",6) 
        initBD_plansFeatures("LDAP",6)
        initBD_plansFeatures("Anti-virus",6)
        
        #Custom5
        initBD_plan("Custom5",1100)
        
        initBD_plansFeatures("Firewall",7)
        initBD_plansFeatures("ZTNA",7) 
        initBD_plansFeatures("LDAP",7)
        initBD_plansFeatures("Double Masque",7)
        initBD_plansFeatures("CASB",7)
        
        #Custom6
        initBD_plan("Custom6",1050)
        
        initBD_plansFeatures("Firewall",8)
        initBD_plansFeatures("ZTNA",8) 
        initBD_plansFeatures("LDAP",8)
        initBD_plansFeatures("Double Masque",8)
        initBD_plansFeatures("SWG",8)
        
        #Custom7
        initBD_plan("Custom7",1050)
        
        initBD_plansFeatures("Firewall",9)
        initBD_plansFeatures("ZTNA",9) 
        initBD_plansFeatures("LDAP",9)
        initBD_plansFeatures("Double Masque",9)
        initBD_plansFeatures("Anti-virus",9)
        
        #Custom8
        initBD_plan("Custom8",1200)
        
        initBD_plansFeatures("Firewall",10)
        initBD_plansFeatures("ZTNA",10) 
        initBD_plansFeatures("LDAP",10)
        initBD_plansFeatures("Double Masque",10)
        initBD_plansFeatures("CASB",10)
        initBD_plansFeatures("SWG",10)
        
        #Custom9
        initBD_plan("Custom9",1200)
        
        initBD_plansFeatures("Firewall",11)
        initBD_plansFeatures("ZTNA",11) 
        initBD_plansFeatures("LDAP",11)
        initBD_plansFeatures("Double Masque",11)
        initBD_plansFeatures("CASB",11)
        initBD_plansFeatures("Anti-virus",11)
        
        
        #Custom10
        initBD_plan("Custom10",1150)
        
        initBD_plansFeatures("Firewall",12)
        initBD_plansFeatures("ZTNA",12) 
        initBD_plansFeatures("LDAP",12)
        initBD_plansFeatures("Double Masque",12)
        initBD_plansFeatures("SWG",12)
        initBD_plansFeatures("Anti-virus",12)
        
        #Custom11
        initBD_plan("Custom11",1050)
        
        initBD_plansFeatures("Firewall",13)
        initBD_plansFeatures("ZTNA",13) 
        initBD_plansFeatures("LDAP",13)
        initBD_plansFeatures("CASB",13)
        initBD_plansFeatures("SWG",13)
        
        #Custom12
        initBD_plan("Custom12",1150)
        
        initBD_plansFeatures("Firewall",14)
        initBD_plansFeatures("ZTNA",14) 
        initBD_plansFeatures("LDAP",14)
        initBD_plansFeatures("CASB",14)
        initBD_plansFeatures("SWG",14)
        initBD_plansFeatures("Anti-virus",14)
        
        #Custom13
        initBD_plan("Custom13",1000)
        
        initBD_plansFeatures("Firewall",15)
        initBD_plansFeatures("ZTNA",15) 
        initBD_plansFeatures("LDAP",15)
        initBD_plansFeatures("SWG",15)
        initBD_plansFeatures("Anti-virus",15)
        
        #Custom14
        initBD_plan("Custom14",1050)
        
        initBD_plansFeatures("Firewall",16)
        initBD_plansFeatures("ZTNA",16) 
        initBD_plansFeatures("LDAP",16)
        initBD_plansFeatures("CASB",16)
        initBD_plansFeatures("Anti-virus",16)
        
        #Custom15
        initBD_plan("Custom15",1300)
        
        initBD_plansFeatures("Firewall",17)
        initBD_plansFeatures("ZTNA",17) 
        initBD_plansFeatures("LDAP",17)
        initBD_plansFeatures("Double Masque",17)
        initBD_plansFeatures("CASB",17)
        initBD_plansFeatures("SWG",17)
        initBD_plansFeatures("Anti-virus",17)
        
        
        
def initBD_organization():
    organization_instance = organization()
    organization_instance.groupName = "numeryx"
    organization_instance.save()
    
def initBD_plan(slug,price):
    plan_instance = plan()
    plan_instance.slug = slug
    plan_instance.price = price
    plan_instance.currency = "euro"
    plan_instance.save()
    
def initBD_plansFeatures(description,planId):
    plansFeatures_instance = plansFeatures()
    plansFeatures_instance.description = description
    plansFeatures_instance.planId = plan.objects.get(id=planId)
    plansFeatures_instance.save()
