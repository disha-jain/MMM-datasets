


import csv
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


# In[2]:


pairs = read_dataset('patients.csv')
print ("Number of patients: " + str(len(pairs)))
print ("blood type of patient in the 37th friend-pair: " + pairs[37]['ReceiverBloodType'])
print ("donorID of the 598th friend-pair: " + str(pairs[598]['DonorID']))


# 
# We have provided two functions that you can use to test for blood type, `is_blood_compatible`, and tissue type `is_tissue_compatible` compatibility.

# In[3]:


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
    Modeling actual tissue compatibility is complex, and depends on                                                                          
    properties of different HLA markers and various other complications.                                                                     
    Instead of dealing with the medical complexities, we use a simple                                                                        
    model that produces a uniformly-distributed value that is dependent                                                                      
    on the two inputs, and outputs a discretized probability.                                                                                
                                                                                                                                             
    It's not important to understand the following code. But you should                                                                      
    call this function with the receiver's PRA-type, receiver's tissue ID,                                                                   
    and the donor's ID to check if their tissues are compatible or not.                                                               
                                                                                                                                             
    Example usage: is_tissue_compatible('Low', 4474, 3587)                                                                                   
    """
    import hashlib
    
    # This code is a convoluted way to approximate a random oracle on the tissue ids (so the                                                 
    # output is uniformly random in [0, 1), but for a given tissue pair, the same output is always                                           
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
    return is_blood_compatible(receiver_type=receiver['ReceiverBloodType'], donor_type=donor['DonorBloodType'])         and is_tissue_compatible(recv_pra=receiver['ReceiverPRA'], recv_id=receiver['ReceiverID'], don_id=donor['DonorID'])


# In[4]:
import numpy as np


pairs = read_dataset('patients.csv')

# for i in range(50):
#     if is_pair_compatible(pairs[0], pairs[i]):
#         print("pair 0 is compatible with pair", i)
# is_pair_compatible(pairs[0], pairs[12])


# In[5]:


is_pair_compatible(pairs[37], pairs[37])


# ## Warm-up: Static Two-Way Exchange
# 
# In the first part of the assignment, you will clear the kidney exchange market using only two-way exchanges. The steps below will guide you through the process of computing a solution to the matching problem.
# 
# We will take the given data as static, ignoring the `TimePeriod` and assuming all pairs are present and ready to be matched. Since the matching will occur over a single period, we will also ignore the `ReceiverSurvivalPrb`. Therefore, we will have a market with 599 pairs of agents.

#    <div class="alert alert-block alert-warning">
#     <b>Problem 1.</b> Compute the mutual compatibility matrix, $\textbf{C}$, for time period 1, where $c_{i,j}=1$ if recipient $i$ is compatible with donor $j$ and zero otherwise. You need to account for blood type and tissue type compatilbility when determining overall compatilbility of two agents. 
#     </div>

# In[106]:

n = len(pairs)
# Write your code here
C = np.zeros((n,n))

for i in range (0, n):
    for j in range (i, n):
        if is_pair_compatible(pairs[i], pairs[j]) and is_pair_compatible(pairs[j], pairs[i]):
            C[i][j] = 1
            C[j][i] = 1


#    <div class="alert alert-block alert-warning">
# 
# <b>Problem 2.</b> Find the maximum matching given $\textbf{C}$ if only two-way exchanges are allowed. For this, you may find the [_Top Trading Cycles algorithm_](https://people.cs.umass.edu/~sheldon/teaching/mhc/cs312/2014sp/Slides/top-trading-cycles.pdf) helpful. Your code should report total number of matched pairs. The target number of matched pairs should be around 320.
#     </div>

# In[93]:


# Write your code here
# This is not the "maximum", it is simply one possibility
# matched = []
# matches = 0

# for i in range(0, len(pairs)):
#     if i not in matched:
#         for j in range(i+1, len(pairs)):
#             if j not in matched:
#                 if C[i][j] == 1 and C[j][i] == 1:
#                     matches += 1
#                     matched.append(i)
#                     matched.append(j)
#                     break
# print(matches)


# # In[104]:


# import numpy as np
# import copy


# # In[107]:


# #greedy algorithm choice --> start with (rec, donor) pair with least number of both-way matches
# n = len(pairs)

# all_sums = np.zeros(n)

# my_c = copy.deepcopy(C)

# def find_sum(num):
#     return np.sum(my_c[num])
         
# def find_all_sum():
#     for i in range (0, n):
#         all_sums[i] = find_sum(i)
#     return all_sums

# def find_min():
#     mini = n
#     mindex = -1
#     for i in range (0, n):
#         if mini >= all_sums[i] and all_sums[i] > 0:
#             mini = all_sums[i]
#             mindex = i
#     return mindex

# def find_first(num):
#     minimum = n
#     mindex = -1
#     for j in range (0, n):
#         if my_c[num][j] == 1.0 and my_c[j][num] == 1.0 and minimum > all_sums[j]:
#             minimum = all_sums[j]
#             mindex = j
#     return mindex
    
# def set_zero(num):
#     for i in range(0, n):
#         my_c[num][i] = 0
#         my_c[i][num] = 0

# def not_all_zero():
#     for i in range (0, n):
#         if all_sums[i] != 0:
#             return True
#     return False
        
# matches = 0
# match = []

# all_sums = find_all_sum()
# pair_one = find_min()
# while not_all_zero():
#     pair_two = find_first(pair_one)
#     match.append((pair_one, pair_two))
#     matches += 2
#     set_zero(pair_two)
#     set_zero(pair_one)
#     all_sums = find_all_sum()
#     pair_one = find_min()

# print(matches)
# print (match)
# done = []

# my_bool = True
# for pair in match:
#     i, j = pair
#     my_bool = my_bool and is_pair_compatible(pairs[i], pairs[j]) and is_pair_compatible(pairs[j], pairs[i]) and i not in done and j not in done
#     done.append(i)
#     done.append(j)
    
# print(my_bool)


#    <div class="alert alert-block alert-warning">
# 
# <b>Problem 3.</b> Analyze the execution cost of your matching algorithm (for Problem 2). A good answer will include both 
# an asymptotic analysis, and a concrete discussion of how large an exchange problem it could reasonably scale to support.
# 
# </div>

# _Write your analysis here_
# 
# Asymptotic Analysis:
# 
# How large can n get without breaking the strongest computer in the world?
# 
# 

# ## Three-Way Exchange
# 
# For the second part of the assignment, you will extend your matching algorithm to allow both two- and three-way exchanges. You may also use $k$-way exchanges where $k\geq4$. 
# For this question, you will continue to use $\textbf{C}$ from problem 1 in order to compare your results from both parts. (We will again take the given data as static, ignoring the `TimePeriod` and assuming all pairs are present and ready to be matched, just as in problem 1.)
# 
# <div class="alert alert-block alert-warning">
# 
# <b>Problem 4.</b> Find the maximum matching given $\textbf{C}$ from Problem 1 and using two- and three-way exchanges (and optionally, support exchanges up to higher $k$. You will need to modify your code from the previous part to allow for cycles of up to 3 (or more) pairs. Your code should report the total number of matched pairs (not the number of cycles). You should see an increase of about 10% from your earlier two-way exchange.
# </div>

# In[43]:


# Write your code here
new_C = np.zeros((n,n))

for i in range (0, n):
    for j in range (0, n):
        if is_pair_compatible(pairs[i], pairs[j]):
            new_C[i][j] = 1
print(new_C)


# In[ ]:


indegrees = np.zeros(n)

def compute_indegree(receiver):
    sum = 0
    for cell in receiver:
        sum += cell
    return sum

def compute_indegrees(indegrees):
    for receiver in range(0,n):
        indegrees[receiver] = compute_indegree(new_C[receiver])
    return indegrees
        
def min_index_of_array(num_array):
    min = float('inf')
    mindex = []
    for i in range(0,len(num_array)):
        if num_array[i] <= min:
            if num_array[i] < min:
                mindex = []
                min = num_array[i]
            mindex.append(i)
    return mindex

def indegrees_present(indegrees):
    for indegree in indegrees:
        if indegree > 0:
            return True
    return False

import copy

def find_cycle(start_index, current_index, k):
    donor_matches = []
    if k == 0 and current_index == start_index:
        donor_matches.append(current_index)
        return donor_matches
    if k == 0:
        return []
    donors = new_C[current_index]
    for donor_index in range(0, n):
        if donors[donor_index] == 1:
            matches = find_cycle(start_index, donor_index, k - 1)
            matches = [donor_index].extend(matches)
            if matches and len(matches) > len(donor_matches):
                donor_matches = copy.deepcopy(matches)
    return donor_matches

indegrees = compute_indegrees(indegrees)
while indegrees_present:
    mindecies = min_index_of_array(indegrees)
    for mindex in mindecies:
        donor_matches = find_cycle(mindex, mindex, 3)
        if donor_matches:
            print(mindex, ': ', donor_matches)
# print(indegrees)

# *Explain your answer here*

# ## Efficiency in Two and Three-Way Exchanges
# [_Efficient Kidney Exchange: Coincidence of Wants in Markets with Compatibility-Based Preferences_](http://uvammm.github.io/docs/kidneyexchange.pdf) by Alvin E. Roth, Tayfun Sönmez and M. Utku Ünver provides the bound on the number of two-way and three-way matches.
# 
# <div class="alert alert-block alert-warning">
# 
# <b>Problem 5.</b>
# How does the number of matches provided by your algorithm compare with the bound in the paper? If there is a discrepency, explain why.
# 
# </div>
# 

# _Explain your answer here_

# ## Dynamic Exchange
# 
# For the final part of the assignment, we will now take the market to be dynamic: instead of having a fixed set of patients and donors, new patients arrive over time (and old patients die if they do not receive a donor kidney). This is a more realistic model of the actual kidney exchange problem. The overall goal is to maximize the overall survival of the population.
# 
# We have provided a function that simulates patient survival with a simple random draw. For each unmatch patient at the end of a time period, their probability of surviving to the next time period is given by the `ReceiverSurvivalPrb` field in the data. (We don't attempt to model patients getting sicker over time; the survival probability for each time period is independent and given by the patient's `ReceiverSurvivalPrb` field.)

# In[16]:


# This function returns True if an unmatched receiver survives until the next time period
def survival(survivalprob):
    import random
    draw = random.random()
    return draw <= survivalprob


# Devlop a matching procedure that can maximize the number of matches over the six time periods in the simulated dataset accounting for patient survival.
# 
# Explain your procedure and why you think each element will help maximize the number of matches. The process is explained below:   
# 
# 1. Start in TimePeriod $t$. You will implement a matching procedure and record the total number of matched agents. Those who are matched will be removed from the pool. 
# 
# 2. Use the provided function `survival()` to evaluate each of the unmatched agents. If the function returns False, the agent perishes and cannot be carried over into the next month. Record the number of agents who perish and the number of agents who survive. (Note: If a patient dies, her donor is no longer willing to donate, so both the patient and donor are eliminated.)
# 
# 3. Add the surviving pairs of agents to the stock for TimePeriod $t+1$
# 
# 4. Repeat (1)-(4) for all time periods
# 
# We have provided a `run_simulation` function that simulates this process, given an input a matching function that implements the `match_kidneys` interface below.
# 
# Your goal is to find matches at each time period that maximize overall survival for this model. For this problem, you will want to divide your code into several functions. You should integrate your code and explanations in a way that makes it easy for a reader to understand your approach, see how you evaluate it, and connect your description to the code.
# 
# For your implementation to work in the in-class competition, it must provide this interface. Do not change function signature.
# 
# You should submit a python file (`<name>_matcher.py`) which contains this function (and any other functions you call from it). If you import libraries, please provide a `requirements.txt` with everything we will need to configure our environment to run your code.

# In[5]:


def match_kidneys(patients, timeleft):
    """
    patients is a list of tuples like the records in patients.csv:
         (ReceiverID,ReceiverBloodType,ReceiverPRA,ReceiverSurvivalPrb,DonorID,DonorBloodType) 
    (there is no TimePeriod field). Each entry represents a patient and their (incompatible) donor-friend.
    
    timeleft is a positive integer representing the number of time periods remaining (that is, 
       when timeleft = 1, this is the final time period)
    
    The output is a list of (ReceiverID, DonorID) matches. (List of tuples)
    More specifically, the ReceiverID is from one friend-pair and the DonorID is from another friend-pair. 
    These two ID's form a transplant match, and their corresponding Donor/Patient friends they entered the pool with must
    also be a part of the exchange in the same round. 
    
    For example:
        Pretend we have two pairs of friends: (PatientAva, DonorAndy) who were not compatible, 
        and (PatientBrady, DonorBrandon) who also were not compatible. These two sets of friends enter the exchange
        because the donor of each pair can't donate to their friend.

        If PatientAva is compatible with DonorBrandon AND PatientBrady is Compatible with DonorAndy, we can form a
        two-way exchange. We would add the tuples (PatientAva, DonorBrandon) and (PatientBrady, DonorBrandon)
        to the list of matches.
        
    
    To be a valid output, all of these properties must hold:
        - No donor or recipient can appear more than once. (Donors only have one kidney to donate, recipients can only receive one)

        - A DonorID appears in the output list if only if their patient friend they volunteered for (ReceiverID) 
          that is in their patient record appears in the output list as a recipient.  
        - All (ReceiverID, DonorID) pairs in the output must be both blood and tissue compatible.
    """
    
    return [] 


# Note that the `match_kidneys` function is stateless. The simulation engine will maintain a list of unmatched patients that are still alive, and update the input patients to the call to `match_kidneys` for each time period to reflect the patients who survived the previous time period (either by receiving a match, which we unrealistically assume means they survive permanently!) or by not receivng a match but passing `surivial()` test, as well as newly arriving patients.

# <div class="alert alert-block alert-warning">
# 
# <b>Problem 6.</b> Develop a matching algorithm that maximizes overall survival in the model where new pairs arrive each time period, and unmatched patients die with the given probability. Your code should provide clear outputs that report both the number of matches and the survival rate for each time period. You should not use any of the data from future time periods in determining what to do for the current time period.
# </div>
# 
# <b>Hints</b>: Since each time period has a smaller market than the previous problems, you may want to develop strategies to thicken the market in order to increase the expected number of compatible pairs. The most obvious strategies greedily find all available matches in each time period, but better strategies may sometimes delay matches. You may be it useful to predict the likelihood that a useful donor kidney arrives in the next time period by estimating the probability a random kidney is compatible.

# *Explain your answer here*

# In[ ]:





# ## Price-based Market For Kidney Transplantations
# 
# [_Efficient Kidney Exchange: Coincidence of Wants in Markets with Compatibility-Based Preferences_](http://uvammm.github.io/docs/kidneyexchange.pdf) discusses the design of a hypothetical competitive market for kidney transplants and derives the properties of market equilibrium. 
# 
# <div class="alert alert-block alert-warning">
#     <b>Problem 7.</b> Discuss your intuition of how the prices for donors of different types should compare and how the properties of competitive prices described in the paper compares with your intuition (ideally, informed by the results of your simulations in the earlier problems).    </div>

# _your answer here_

# <div class="alert alert-block alert-danger">
#     
# Submit your Project 3 notebook by **Tuesday, 18 February 2020, 9:59pm** by creating a slack group (click “Direct Messages”) containing you and all of your teammates and the four course staff: `@cam` `@Dave` `@Denis Nekipelov` `@Kyeongtak Do`.
# 
# Submit your project to that group chat by attaching your jupyter notebook to a message (use the “+” at the left of the message entry field to attach a file).
# </div>

# In[ ]:




