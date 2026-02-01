from faker import Faker
from datetime import date
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import csv
import random
import string

fake = Faker('en_CA')

physician_list = []
for _ in range(12):
    dr = fake.last_name()
    physician_list.append(dr)
    
class DataQuality(Enum):
    PERFECT = "perfect"
    GOOD = "good"
    POOR = "poor"
    BAD = "bad"

@dataclass
class Patient:
    patient_id:str
    first_name: str
    family_name: str
    dob: date
    health_card: str
    version_code: str
    address: str
    
@dataclass 
class Visit:
    visit_id:str
    patient_id:str    
    date_of_visit: date
    procedure_1: str | None = None
    procedure_2: str | None = None
    attending_physician: str | None = None
    vitals_bp: str | None = None
    vitals_hr: str | None = None
    vitals_temp: str | None = None
    notes: str | None = None

@dataclass
class Paramedic:
    last_name:str
    first_name:str
    moh_id:int
    level:Enum
   
class Paramedic_Level(Enum):
    ACP="ACP"
    PCP="PCP"   

def create_paramedic(number_to_create:int) -> list:
    '''This will create a list of Paramedics with data populated'''
    counter = 0
    paramedic_list = []
    while counter < number_to_create:
        last_name = fake.last_name()
        first_name = fake.first_name()
        # random int 0-99 less than 75 = PCP else ACP
        # moh_id_pool = set() create unique list 

    
        counter+=1

    return paramedic_list

def create_patient(number_to_create:int) -> list:
    ''''This will return a list of Patient objects populated with synthetic PID data'''

    good_or_bad = random.randint(1,100)
    # if good_or_bad > 20
    #     DataQuality = PERFECT
    # elif good_or_bad == 1
    #     DataQuality = BAD
    
    pt_id_pool = set()
    if number_to_create > 80000:
        raise ValueError("Cannot Create More than 800,000 Patients At One Time")
    while len(pt_id_pool) <= number_to_create:
        num = random.randint(100000,999999)
        pt_id_pool.add(num)    

    current_year = datetime.now().year
    clinic_opened_year = current_year - 28

    p_list = []
    counter = 0

    # Generates the synthetic information, then creates the unique Patient
    while counter < number_to_create:   
        patient_id = f"{random.randint(clinic_opened_year, current_year)}{pt_id_pool.pop()}"
        first_name = fake.first_name()
        family_name = fake.last_name()
        dob = fake.date_of_birth(minimum_age=2, maximum_age=105)
        address = fake.address()
        health_card = f"{random.randint(1000,9999)}-{random.randint(100,999)}-{random.randint(100,999)}"
        # version_code = f"{(random.choices(string.ascii_uppercase, k=2))}"
        version_code = ''.join(random.choices(string.ascii_uppercase, k=2))

        p = Patient(patient_id=patient_id, first_name = first_name, family_name = family_name, dob = dob,health_card=health_card, version_code=version_code, address=address)
        p_list.append(p)
        counter += 1     
    return p_list



def create_visit(patient_list: list, number_of_visits: int) -> list:
    ''''This will return a list of visits, diagnois, procedure, insurance code'''
      
    if number_of_visits > 900000:
        raise IndexError("Unable to generate more than 900,000 unique visits")

    visit_pool = set()
    while len(visit_pool) < number_of_visits:
        num = random.randint(1000000, 9999999)
        visit_pool.add(num)
    
   
    current_date = datetime.now()
    v_list = []
    counter = 0
    while counter < number_of_visits:
        p = random.choice(patient_list)
        date_of_visit = fake.date_between_dates(datetime(2009,1,1), current_date)
        visit_id = f"{date_of_visit.year}{visit_pool.pop()}"
        patient_id = p.patient_id
        procedure_1 = ""
        procedure_2 = ""
        attending_physician = random.choice(physician_list)
        vitals_bp =""
        vitals_hr =""
        vitals_temp =""
        notes = ""

        v = Visit(visit_id, patient_id, date_of_visit, procedure_1, procedure_2, attending_physician, vitals_bp, vitals_hr, vitals_temp, notes)
        v_list.append(v)
        counter += 1
    return v_list



def create_csv(list, patient=True):
    dict_ls = []    
    for pt in list:
        p = vars(pt)
        dict_ls.append(p)
    if patient:
        file_name = "patient_list.csv"
        fieldnames = ["patient_id", "first_name", "family_name", "dob", "health_card", "version_code", "address"]
    elif not patient:
        file_name = "visit_list.csv"
        fieldnames = ["visit_id", "patient_id", "date_of_visit", "procedure_1", "procedure_2", "attending_physician", "vitals_bp", "vitals_hr", "vitals_temp", "notes"] 
    with open(file_name, "w", newline="") as f:
        try:
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            for row in dict_ls:
                writer.writerow(row)
        except FileNotFoundError:
            print("Error")
            
def main():
    ''''''
    patient_list = create_patient(10000)
    create_csv(patient_list)
    visit_list = create_visit(patient_list, 100000)
    create_csv(visit_list, False)
main()  
