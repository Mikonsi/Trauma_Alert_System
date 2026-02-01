from time import CLOCK_PROCESS_CPUTIME_ID
from faker import Faker
from datetime import date
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import csv
import random
import string

fake = Faker('en_CA')


@dataclass
class Paramedic:
    last_name:str
    first_name:str
    moh_id:int
    level:Enum
    # Could add date_of_level_change for validation if dirty data is created
   
class Paramedic_Level(Enum):
    ACP="ACP"
    PCP="PCP"

@dataclass
class Shift:
    shift_length: int = 12
    left_early: int | None = None
    start_time: datetime
    end_time: datetime
    paramedic_1: Paramedic
    paramedic_2: Paramedic | None = None
    paramedic_3_or_student: Paramedic | None = None 
    
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
class Ambulance_Call:
    call_id:str
    patient: Patient    
    date_of_call: datetime
    procedure_1: str | None = None
    procedure_2: str | None = None
    attending_paramedic: Paramedic | None = None
    paramedic_2: Paramedic | None = None
    paramedic_3: Paramedic | None = None
    problem_code: float
    ctas: int 
    vitals_bp: str | None = None
    vitals_hr: str | None = None
    vitals_temp: str | None = None
    notes: str | None = None
 

def create_paramedic(number_to_create:int) -> list:
    '''This will create and return a list of Paramedics objects'''
    # Currently, moh_id unique number generator runs between 1900-35999 which is 16999 possible numbers, but as their randomly drawn it will take an extremely long time to generate new random numbers as the max is approached
    if number_to_create >= 10000:
        raise IndexError("Max number of unique MOH ID's that can be created is 10,000")
    counter = 0
    paramedic_list = []

    # Whileloop repeatedly creates Paramedic objects with unique values, then adds them to the paramedic_list and increments the counter
    while counter < number_to_create:
        last_name = fake.last_name()
        first_name = fake.first_name()
        # In real world, ~75% of paramedics are PCP. Assigning levels appripriately 
        rand_level_assigner = random.randint(0,99)
        if rand_level_assigner <= 75:
            level=Paramedic_Level.PCP
        else:
            level=Paramedic_Level.ACP
        # Creating and assigning unique Ministry of Health ID (moh_id)
        id_pool = set()
        while len(id_pool) > number_to_create:
            next_unique_id = random.randint(19000,35999)
            id_pool.add(next_unique_id)
        moh_id = id_pool.pop()

        medic = Paramedic(last_name=last_name, first_name = first_name, moh_id = moh_id, level = level)

        paramedic_list.append(medic)
        counter+=1

    return paramedic_list


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
