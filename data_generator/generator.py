from faker import Faker
from datetime import date, timedelta
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import csv 
import random

fake = Faker('en_CA')

paramedic_problem_codes = {

1 : {"VSA" : "Cardiac/Medical"},
2 : {"VSA" : "Traumatic"},
11 : {"Airway" : "Obstruction (Partical/Complete)"},
21 : {"Breathing": "Dyspnea"},
24 : {"Breathing" : "Respiratory Arrest"},
31 : {"Circulation": "Hemorrhage"},
32 : {"Circulation" : "Hypertension"},
33 : {"Circulation" : "Hypotension"},
34 : {"Circulation" :"Suspected Sepsis"},
40 : {"Neurological": "Traumatic Brain Injury" },
41 : {"Neurological": "Stroke/TIA"},
42 : {"Neurological": "Temp. Loss of Consciousness"},
43 : {"Neurological": "Altered Level of Consciousness"},
44 : {"Neurological": "Headache"},
45 : {"Neurological": "Behaviour/Psychiatric"},
45.01 : {"Neurological": "Excited Delirium"},
46 : {"Neurological": "Active Seizure"},
47 : {"Paralysis/Spinal Trauma"},
48 : {"Neurological": "Confusion/Disorientation"},
49 : {"Neurological": "Unconscious"},
50 : {"Neurological": "Post-ictal"},
51 : {"Cardiac" : "Ischemic"},
53 : {"Cardiac" : "Palpitations"},
54 : {"Cardiac" : "Pulmonary Edema"},
55 : {"Cardiac" : "Post Arrest"},
56 : {"Cardiac" : "Cardiogenic Shock"},
57 : {"Cardiac" : "STEMI"},
58 : {"Cardiac" : "Hyperkalemia"},
60 : {"Non-Traumatic" : "Non Ischemic Chest Pain"},
61 : {"Non-Traumatic" : "Abdominal / Pelvic / Perineal / Rectal Pain"},
61.1 : {"Non-Traumatic" : "Renal Colic"},
61.2 : {"Non-Traumatic" : "Suspected UTI"},
62 : {"Non-Traumatic" : "Back Pain"},
63 : {"Gastrointestinal" : "Nausea / Vomiting / Diarrhea"},
65 : {"Integumentary" : "Integumentary"},
65.1 : {"Integumentary" : "Skin Tear"},
66 : {"Musculoskeltal/Trauma" : "Musculosketal"},
67 : {"Musculoskeltal/Trauma" : "Trauma / Injury"},
71 : {"Obstetrical/Gynecological" : "Obstetrical Emergency"},
72 : {"Obstetrical/Gynecological" : "Gynecological Emergency"},
73 : {"Obstetrical/Gynecological" : "Newborn / Neonatal"},
81 : {"Endocrine/Toxicological" : "Drug Alcohol Overdose"},
81.1 : {"Endocrine/Toxicological" : "Suspected Opioid Overdose"},
82 : {"Endocrine/Toxicological" :  "Poisoning / Toxic Exposure"},
83 : {"Endocrine/Toxicological" :  "Diabetic Emergency"},
84 : {"Endocrine/Toxicological" :  "Allergic Reaction"},
85 : {"Endocrine/Toxicological" :  "Anaphylaxis"},
86 : {"Endocrine/Toxicological" : "Adrenal Crisis"},
87 : {"General and Minor" : "Novel Medications"},
88 : {"General and Minor" : "Home Medical Technology"},
89 : {"General and Minor" : "Lift Assist"},
90 : {"General and Minor" : "Inter-facility Transfer"},
91 : {"General and Minor" : "Environmental Emergency"},
92 : {"General and Minor" : "Weakness / Dizziness / Unwell"},
93 : {"General and Minor" : "Treatment / Diagnosis & Return"},
94 : {"General and Minor" : "Convalescent / Invalid / Return Home"},
95 : {"General and Minor" : "Infectious Disease"},
96 : {"General and Minor" : "Organ Retrieval / Transfer"},
98 : {"General and Minor" : "Organ Recipient"},
99 : {"General and Minor" : "Other Medical / Trauma (see remarks)"},
99.15 : {"General and Minor" : "No Complaint"}
}

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

# @dataclass
# class Shift:
#     shift_length: int = 12
#     left_early: int | None = None
#     start_time: datetime
#     end_time: datetime
#     paramedic_1: Paramedic
#     paramedic_2: Paramedic | None = None
#     paramedic_3_or_student: Paramedic | None = None 
    
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
    patient: str 
    date_of_birth: date    
    date_of_call: datetime
    problem_code: float
    ctas: int 
    vitals_bp: str | None = None
    vitals_hr: str | None = None
    vitals_temp: str | None = None
    procedure_1: str | None = None
    procedure_2: str | None = None
    attending_paramedic_id: int | None = None
    paramedic_2_id: int| None = None
    paramedic_3_id: int | None = None

    # notes: str | None = None
 

def create_paramedic(number_to_create:int) -> list:
    '''This will create and return a list of Paramedics objects'''
    # Currently, moh_id unique number generator runs between 1900-35999 which is 16999 possible numbers, but as their randomly drawn it will take an extremely long time to generate new random numbers as the max is approached
    if number_to_create >= 8500:
        raise IndexError("Max number of unique MOH ID's that can be created is 8500")
    counter = 0
    paramedic_list = []
    id_pool = set()
    while len(id_pool) < number_to_create:
        next_unique_id = random.randint(19000,35999)
        id_pool.add(next_unique_id)

    # Whileloop repeatedly creates Paramedic objects with unique values, then adds them to the paramedic_list and increments the counter
    while counter < number_to_create:
        last_name = fake.last_name()
        first_name = fake.first_name()
        # In real world, ~75% of paramedics are PCP. Assigning levels appropriately 
        rand_level_assigner = random.randint(0,99)
        if rand_level_assigner <= 75:
            level=Paramedic_Level.PCP
        else:
            level=Paramedic_Level.ACP
        # Creating and assigning unique Ministry of Health ID (moh_id)
        moh_id = id_pool.pop()
        medic = Paramedic(last_name=last_name,
                          first_name = first_name,
                          moh_id = moh_id,
                          level = level)

        paramedic_list.append(medic)
        counter+=1

    return paramedic_list

#TODO: Create shifts so paramedics are realistically assigned calls while on shift according to datetime of call occuring.

def create_ambulance_calls(staff_list: list, number_of_calls: int, range_start: datetime, range_end: datetime) -> list:
    '''This accept list of paramedics, a date range, and a number of calls to create for those paramedics within that daterange, and will return a list of calls complete with Patient and Paramedic objects included.'''
      
    if number_of_calls > 999999:
        raise IndexError("Unable to generate more than 450,000 unique visits")
    current_date = datetime.now()
    call_id_pool = set()
    call_id = int(f"{current_date.year}{current_date.month:02d}{current_date.day:02d}1000000")
    while len(call_id_pool) < number_of_calls:
        num = call_id + 1
        call_id_pool.add(num)
        call_id +=1 
    c_list = []
    counter = 0
    while counter < number_of_calls:
        # Add random generation if hit add 3rd paramedic to crew (sometimes student who is not in staff list)
        p1, p2=random.sample(staff_list,2)
        attending_paramedic_id = p1.moh_id
        paramedic_2_id = p2.moh_id
        paramedic_3_id = None
        date_of_call = fake.date_time_between_dates(range_start, range_end)
        call_id = call_id_pool.pop()
        patient = f"{fake.first_name()}, {fake.last_name()}"
        date_of_birth = fake.date_of_birth(minimum_age=0, maximum_age=110)
        procedure_1 = ""
        procedure_2 = ""
        vitals_bp =""
        vitals_hr =""
        vitals_temp =""

        problem = random.choice(list(paramedic_problem_codes.keys()))
        problem_code = float(problem)
        # notes = ""
        ctas_predictor = random.randint(0,100)
        if ctas_predictor > 60:
            ctas = random.randint(3,4)
        else:
            rare_ctas = [1,2,5]
            ctas = random.choice(rare_ctas)
    
        ac = Ambulance_Call(call_id=call_id,
                            patient=patient,
                            date_of_birth=date_of_birth,
                            date_of_call=date_of_call,
                            problem_code=problem_code,
                            ctas=ctas,
                            vitals_bp=vitals_bp,
                            vitals_hr=vitals_hr,
                            vitals_temp=vitals_temp,
                            procedure_1=procedure_1,
                            procedure_2=procedure_2,
                            attending_paramedic_id=attending_paramedic_id, paramedic_2_id=paramedic_2_id,
                            paramedic_3_id=paramedic_3_id)
        c_list.append(ac)
        counter += 1
    return c_list


class Csv_Type(Enum):
    PARAMEDIC = "paramedic"
    AMBULANCE_CALL = "ambulance_call"

def create_csv(item_list: list, csv_type: Csv_Type):
    
    dict_ls = []    
    if csv_type == Csv_Type.PARAMEDIC:
        file_name = "staff_list.csv"
        fieldnames = ["last_name","first_name","moh_id","level"]
        for field in item_list:
            row = asdict(field)
            if isinstance(row.get('level'), Enum):
                row['level'] = row['level'].value
            dict_ls.append(row)

        
    elif csv_type == Csv_Type.AMBULANCE_CALL:
        file_name = "call_list.csv"
        fieldnames = ["call_id",
            "patient",
            "date_of_birth",
            "date_of_call",
            "problem_code",
            "ctas",
            "vitals_bp",
            "vitals_hr",
            "vitals_temp",
            "procedure_1",
            "procedure_2",
            "attending_paramedic_id",
            "paramedic_2_id",
            "paramedic_3_id",]
        for field in item_list:
            row = asdict(field)
            if isinstance(row['date_of_call'], datetime):
                row['date_of_call'] = row['date_of_call'].isoformat()
            dict_ls.append(row)
        
    else:
        raise ValueError(f"Unsupported csv_type: {csv_type}")

    with open(file_name, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames, extrasaction='ignore')
        writer.writeheader()
        for row in dict_ls:
            writer.writerow(row)

    


            
def main():
    ''''''
    paramedic_list = create_paramedic(500)
    create_csv(paramedic_list, Csv_Type.PARAMEDIC)
    today=datetime.now()
    yesterday = today - timedelta(days=1)
    # last_year was used to populate the db on the first run only and daily updates contine from there
    # last_year = today - timedelta(days=365) 
    call_list = create_ambulance_calls(paramedic_list, 5000,
yesterday, yesterday)
    create_csv(call_list, Csv_Type.AMBULANCE_CALL)

main()  
