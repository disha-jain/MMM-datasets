###
### simulator.py
###
### Kidney Exchange simulator for UVA cs4501/econ4730 course (Project 3)
### https://uvammm.github.io/project3
###
### It should go without saying that no one should use code written for 
### a course project by people with no medical expertise to actually match
### kidneys (or to arrange dates, for that matter). 
###

import random
from datetime import datetime
import csv
from os import listdir
from os.path import isfile, join
 

# These functions retrieve all python files with 'matcher' in the name in the working directory.
# If you need to include/exclude submissions from simulation, rename them to 
# include/exclude 'matcher'. 

def is_matcher_file(filename):
    f = filename
    return all([
        isfile(join('./', f)), 
        'matcher' in f,
        f.endswith('.py'),
        '~' not in f,
    ])

def retrieve_matchers():
    files = list(filter(is_matcher_file, listdir('./')))
    matchers = []

    for f in files:
        print("running ", f)
        try:
            module = __import__(f[:-3])
            matchers.append(module)
        except ImportError:
            raise("import error trying to import" + f)
    return matchers


# This function generates a random blood type
def rand_blood():
    b = random.random()
    if b < 0.45:
        return 'O'
    elif b < 0.85:
        return 'A'
    elif b < 0.95:
        return 'B'
    else:
        return 'AB'
 
# This function generates a random PRA type
def rand_pra():
    b = random.random()
    if b < 0.70:  # low PRA
        return 'Low'
    elif b < 0.90: # medium PRA
        return 'Medium'
    else: # high PRA
        return 'High'
 
def is_blood_compatible(receiver_type, donor_type):
    """
    Returns True iff a receiver with blood time receiver_type can receive blood
    from a donor with blood type donor_type.
    """
    if donor_type == 'O':
        return True
    elif donor_type == 'A':
        return receiver_type in ('A', 'AB')
    elif donor_type == 'B':
        return receiver_type in ('B', 'AB')
    elif donor_type == 'AB':
        return receiver_type == 'AB'
    else:
        raise InvalidParameterException("Invalid blood type: " + donor_type)
 
def is_tissue_compatible(recv_pra, recv_id, don_id):
    """
    Modeling actual  compatibility is complex, and depends on
    properties of different HLA markers and various other complications.
    Instead of dealing with the medical complexities, we use a simple 
    model that produces a uniformly-distributed value that is dependent
    on the two inputs, and outputs a discretized probability.
     
    It's not important to understand the following code. But you should 
    call this function with the receiver's PRA-type, receiver's ID, 
    and the donor's  ID to check if their tissues are compatible or not.
     
    Example usage: is_tissue_compatible('Low', 4474, 3587)
    """
    import hashlib
     
    # This code is a convoluted way to approximate a random oracle on the ids (so the
    # output is uniformly random in [0, 1), but for a given ID pair, the same output is always
    # produced). 
     
    hexval = hashlib.md5((str(recv_id) + str(don_id)).encode()).hexdigest()
    intval = int(hexval, 16)
    b = intval / (1 << 129 - 1)  # md5 generates 128-bit number; we normalize it to [0, 1]
 
    if recv_pra == 'Low':
        return b <= 0.95
    elif recv_pra == 'Medium':
        return b <= 0.45
    else:  # high pra
        assert recv_pra == 'High'
        return b <= 0.10
 
def is_pair_compatible(receiver, donor):
    """
    This function returns True if the receiver from the receiver pair is compatible with 
    the donor from the donor pair, otherwise it returns False.
    """
    return is_blood_compatible(receiver_type=receiver['ReceiverBloodType'], donor_type=donor['DonorBloodType']) \
        and is_tissue_compatible(recv_pra=receiver['ReceiverPRA'], recv_id=receiver['ReceiverID'], don_id=donor['DonorID'])
 
def rand_pair():
    """
    Randomly generates a (Receiver, Donor) pair (that must be incompatible).
    """
    recv_id = random.randint(0, 1000000)
    recv_blood = rand_blood()
    recv_pra = rand_pra()
    recv_survprb = round(max(min(random.gauss(0.8, 0.5), 0.99), 0.01), 2)
 
    while True:
        don_id = random.randint(0, 1000000)
        while don_id == recv_id:
            don_id = random.randint(0, 1000000)
        don_blood = rand_blood()
        if not is_blood_compatible(recv_blood, don_blood) or not is_tissue_compatible(recv_pra, recv_id, don_id):
            break # keep drawing until an incompatible donor is selected
 
    pair_dict = {'ReceiverID': recv_id,
                 'ReceiverBloodType': recv_blood,
                 'ReceiverPRA': recv_pra,
                 'ReceiverSurvivalPrb': recv_survprb,
                 'DonorID': don_id,
                 'DonorBloodType': don_blood,
                 }

    assert not is_pair_compatible(receiver=pair_dict, donor=pair_dict)
    return pair_dict
 
def generate_dataset(ntimeperiods, npatients):
    random.seed(45014730)
    patients = []
    keys = ['TimePeriod', 'ReceiverID', 'ReceiverBloodType', 'ReceiverPRA', 
            'ReceiverSurvivalPrb', 'DonorID', 'DonorBloodType']
    idsused = []
    #print(','.join(keys))
    for t in range(ntimeperiods):
        for i in range(npatients):
            pair_dict = rand_pair()
            while pair_dict['ReceiverID'] in idsused or pair_dict['DonorID'] in idsused:
                pair_dict = rand_pair() # redraw
            #print(','.join([str(t)] + [str(pair_dict[k]) for k in keys[1:]]))
            pair_dict['TimePeriod'] = t
            patients.append(pair_dict)
            idsused += [pair_dict['ReceiverID'], pair_dict['DonorID']]

    return patients

def read_dataset(f):
    """
    Reads a csv file of patient records, and returns that dataset as a list.
    This is very fragile (non-defensive) code that assumes the csv is correct,
    and converts to the appropriate types.
    """
    patients = [] # list of (patient, donor) pairs
    with open(f, newline='') as csvfile:
        simreader = csv.reader(csvfile, delimiter=',')
        headers = next(simreader)
        print(str(headers))
        for row in simreader:
            readline = {key: value for key, value in zip(headers, row)}
            patients.append({'TimePeriod': int(readline['TimePeriod']),
                             'ReceiverID': int(readline['ReceiverID']),
                             'ReceiverBloodType': readline['ReceiverBloodType'],
                             'ReceiverPRA': readline['ReceiverPRA'],
                             'ReceiverSurvivalPrb': float(readline['ReceiverSurvivalPrb']),
                             'DonorID': int(readline['DonorID']),
                             'DonorBloodType': readline['DonorBloodType']})

    return patients

def survival(survivalprob):
    import random
    draw = random.random()
    return draw <= survivalprob

def match_kidneys(patients, timeleft):
    """
    Please do not change the signature of this function.

    patients is a list of tuples like the records in patients.csv:
         (ReceiverID,ReceiverBloodType,ReceiverPRA,ReceiverSurvivalPrb,DonorID,DonorBloodType) 
    (there is no TimePeriod field). Each entry represents a patient and their (incompatible) donor.
    
    timeleft is a positive integer representing the number of time periods remaining (that is, 
       when timeleft = 1, this is the final time period)
    
    The output is a list of (ReceiverID, DonorID) pairs.
    
    To be a valid output, all of these properties must hold:
        - All the recipient ReceiverID in the output list pairs must be in the input patients, and each can 
          appear at most once.
        - A DonorID appears in the output list only if the patient they volunteered for (ReceiverID) 
          that is in their patient record appears in the output list as a recipient.  
        - All (ReceiverID, DonorID) pairs in the output must be both blood and tissue compatible.
    """
    pairs = []

    assert isinstance(pairs, list) 
    return pairs


def run_simulation(matcher, patients, ntimeperiods):
    """
    Simluate patient survival for ntimeperiods.

    The output is a score representing the number of patients still alive after the end of the last time period.
    """

    matched = [] # patients that have received a donor kidney
    atrisk = [] # patients that are waiting for a matching donor
    dead = [] # patients who have died

    for timeperiod in range(ntimeperiods):
        # new patients arrive for this timeperiod
        newpatients = [patient for patient in patients if patient['TimePeriod'] == timeperiod]
        atrisk += newpatients

        # wrap in try catch since this will be student's code called
        matches = matcher(atrisk, ntimeperiods - timeperiod)

        # print("Time period " + str(timeperiod) + ", " + str(len(atrisk)) + " patients needing donors")

        for match in matches:
            recipient = match[0]
            donor = match[1]
            
            # all the checks here use assert for simplicity now, but will need
            # to be done more resiliently for the scoring tests...

            # verify that the donor's patient-friend is receiving a match. (who they entered exchange with)
            donorrecords = [patient for patient in atrisk if patient['DonorID'] == donor]
            assert len(donorrecords) == 1

            #this is the donor's friend they were incompatible with.
            patientid = donorrecords[0]['ReceiverID']

            # verify that patientid of donor's friend is matched with a different donor
            matches_with_patient = [p for p in matches if p[0] == patientid]
            #print('matches_with_patient', matches_with_patient)
            assert len(matches_with_patient) == 1

            # get full info of recipient in the match to check compatibility with donor 
            recipient_record = [patient for patient in atrisk if patient['ReceiverID'] == recipient]
            assert is_pair_compatible(receiver=recipient_record[0], donor=donorrecords[0])
            #print("Saved patient: " + str(patientid))
            matched += [patientid] # yeah! patientid is saved
            # don't remove from atrisk yet, since donor may not have matched yet
    
        nbefore = len(atrisk)
        atrisk = [patient for patient in atrisk if patient['ReceiverID'] not in matched]
        assert len(atrisk) == nbefore - len(matches)

        # now, see who survives
        died = [patient for patient in atrisk if not survival(patient['ReceiverSurvivalPrb'])]
        # print("Survival: " + str(len(died)) + " patients died.")
        atrisk = [patient for patient in atrisk if patient not in died]
        dead += died
        print("After %d rounds, %d patients matched, %s patients still alive, %s patients died" % (timeperiod + 1, len(matched), len(atrisk), len(dead)))
 
    return len(atrisk) + len(matched)

if __name__ == "__main__":
    # this generated the patients.csv file: 
    generate_dataset(10, 100)
    
    #exit()
    ## patients = read_dataset('patients.csv')
    patients = generate_dataset(10, 1000)
    olen = len(patients)
    ntimeperiods = max([patient['TimePeriod'] for patient in patients]) + 1
    print (str(ntimeperiods))
    print(patients)
    # average score over 10 trials
    ntrials = 2
    scores = []
    # for _ in range(ntrials):
    #     score = run_simulation(match_kidneys, patients, ntimeperiods) 
    #     print ("Survival score: " + str(score))
    #     scores += [score]

    # assert len(patients) == olen
    # print ("Survival score: " + str(sum(scores) / ntrials))

    students_scores = {}

    for matcher in retrieve_matchers():
        matcher_scores = []
        print("Running simulation with ", matcher.__name__, "submission")
        for _ in range(ntrials):
            matcher_score = run_simulation(matcher.match_kidneys, patients, ntimeperiods)
            #print("Survivor score: " + str(matcher_score))
            matcher_scores += [matcher_score]
        assert len(patients) == olen
        print("Survival score for group " + matcher.__name__ + " is: ", str(sum(matcher_scores) / ntrials))

