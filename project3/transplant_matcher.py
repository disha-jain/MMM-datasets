
import numpy as np
import copy

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
    return is_blood_compatible(receiver_type=receiver['ReceiverBloodType'], donor_type=donor['DonorBloodType']) \
        and is_tissue_compatible(recv_pra=receiver['ReceiverPRA'], recv_id=receiver['ReceiverID'], don_id=donor['DonorID'])


def find_sum(num, my_c):
    return np.sum(my_c[num])
         
def find_all_sum(n, my_c, all_sums):
    for i in range (0, n):
        all_sums[i] = find_sum(i, my_c)
    return all_sums

def find_min(n, all_sums):
    mini = n
    mindex = -1
    for i in range (0, n):
        if mini >= all_sums[i] and all_sums[i] > 0:
            mini = all_sums[i]
            mindex = i
    return mindex

def find_first(num, n, my_c, all_sums):
    minimum = n
    mindex = -1
    for j in range (0, n):
        if my_c[num][j] == 1.0 and my_c[j][num] == 1.0 and minimum > all_sums[j]:
            minimum = all_sums[j]
            mindex = j
    return mindex
    
def set_zero(num, n, my_c):
    for i in range(0, n):
        my_c[num][i] = 0
        my_c[i][num] = 0

def not_all_zero(n, all_sums):
    for i in range (0, n):
        if all_sums[i] != 0:
            return True
    return False


def compute_indegrees(indegrees, n, new_C):
    for receiver in range(0,n):
        for donor in range(0,n):
            indegrees[donor] += new_C[receiver][donor]
        return indegrees

def compute_comp_donor(receiver):
    sum = 0
    for cell in receiver:
        sum += cell
    return sum

def compute_comp_donors(comp_donors, n, new_C):
    for receiver in range(0,n):
        comp_donors[receiver] = compute_comp_donor(new_C[receiver])
    return comp_donors
        
def min_index_of_array(num_array, found_no_matches):
    min_value = float('inf')
    mindex = []
    for i in range(0,len(num_array)):
        if num_array[i] <= min_value and num_array[i] > 0 and found_no_matches[i] == 0:
            if num_array[i] < min_value:
                mindex = []
                min_value = num_array[i]
            mindex.append(i)
    return mindex

def comp_donors_present(comp_donors):
    for comp_donor in comp_donors:
        if comp_donor > 0:
            return True
    return False

def update_matrix(removed_pairs, new_C, n):
    for pair in removed_pairs:
        for i in range(0,n):
            new_C[pair][i] = 0
            new_C[i][pair] = 0

def get_compat_donors(receiver_index, n, new_C):
    donors = []
    for i in range(n):
        if new_C[receiver_index][i] == 1:
            donors.append(i)
    return donors

def get_optimal_cycle(cycles, comp_donors, comp_receivers):
    if len(cycles) == 1:
        return cycles[0]
    min_matches = float('inf')
    min_matches_index = 0
    sum_of_donor_matches = np.zeros(len(cycles))
    for i in range(len(cycles)):
        for d in range(1,len(cycles[i])):
            sum_of_donor_matches[i] += comp_receivers[cycles[i][d]]
        if sum_of_donor_matches[i] < min_matches:
            min_matches = sum_of_donor_matches[i]
            min_matches_index = i
    return cycles[i]
        
def calculate_k_cycles(new_C, n, found_no_matches):
    comp_donors = np.zeros(n)
    comp_receivers = np.zeros(n)
    matched_pairs = 0
    matches = []
    # Calc the number of compatible donors for each receiver
    comp_donors = compute_comp_donors(comp_donors, n, new_C)
    comp_receivers = compute_indegrees(comp_receivers, n, new_C)
    # Find the receivers with the fewest numbers of compatible donors
    mindecies = min_index_of_array(comp_donors, found_no_matches)
    while mindecies:
        # print(mindecies)
        # get first receiver in mindecies
        mindex = mindecies[0]
        # get all immediate matching donors for receiver
        possible_donors = get_compat_donors(mindex, n, new_C)
        if possible_donors:
            cycles = []
            # for each immediate matching donor
            for donor in possible_donors:
                # if receiver's donor is not a match for donor's reciver, look another level down
                # get compatible donors for donor's receiver, add all cycles where 2nd donor's 
                # patient is a match for first receiver's donor
                possible_donors_2 = get_compat_donors(donor, n, new_C)
                if possible_donors_2:
                    for donor_2 in possible_donors_2:
                        if new_C[donor_2][mindex] == 1:
                            cycles.append((mindex, donor, donor_2))
                else:
                    found_no_matches[mindex] = 1
            if cycles:
                optimal_cycle = get_optimal_cycle(cycles, comp_donors, comp_receivers)
                matches.append(optimal_cycle)
                update_matrix(optimal_cycle, new_C, n)
                matched_pairs += len(optimal_cycle)
            else:
                found_no_matches[mindex] = 1
        else:
            found_no_matches[mindex] = 1

        comp_donors = compute_comp_donors(comp_donors, n, new_C)
        comp_receivers = compute_indegrees(comp_receivers, n, new_C)
        mindecies = min_index_of_array(comp_donors, found_no_matches)
    return matched_pairs, matches
import heapq 
def match_kidneys(patients, timeleft):
    final_cycles = []
    for t in range(timeleft):
        print(t)
        n = len(patients)

        C = np.zeros((n,n))

        for i in range (0, n):
            for j in range (i, n):
                if is_pair_compatible(patients[i], patients[j]) and is_pair_compatible(patients[j], patients[i]):
                    C[i][j] = 1
                    C[j][i] = 1
        n = len(patients)

        all_sums = np.zeros(n)

        my_c = C

        match_amt = 0
        match = []

        all_sums = find_all_sum(n, my_c, all_sums)
        pair_one = find_min(n, all_sums)
        while not_all_zero(n, all_sums):
            pair_two = find_first(pair_one, n, my_c, all_sums)
            match.append((pair_one, pair_two))
            match_amt += 2
            set_zero(pair_two, n, my_c)
            set_zero(pair_one, n, my_c)
            all_sums = find_all_sum(n, my_c, all_sums)
            pair_one = find_min(n, all_sums)


        new_C = np.zeros((n,n))

        for i in range (0, n):
            for j in range (0, n):
                if is_pair_compatible(patients[i], patients[j]):
                    new_C[i][j] = 1

        found_no_matches = np.zeros(n)
        C = copy.deepcopy(new_C)
        matched_pairs, matches = calculate_k_cycles(C, n, found_no_matches)
        final_pairs = []
        final_pairs_num = 0
        for cycle2 in match:
            pair1 = cycle2[0]
            pair2 = cycle2[1]
            cycle_needing_p1 = -1
            cycle_needing_p2 = -1
            for i in range(len(matches)):
                cycle3 = matches[i]
                if pair1 in cycle3:
                    cycle_needing_p1 = i
                elif pair2 in cycle3:
                    cycle_needing_p2 = i
            if cycle_needing_p2 != -1 and cycle_needing_p1 != -1 and cycle_needing_p2 != cycle_needing_p1:
                match.remove(cycle2)
                final_pairs.append(matches[cycle_needing_p1])
                final_pairs.append(matches[cycle_needing_p2])
            else:
                final_pairs.append(cycle2)
        for cycle in final_pairs:
            final_pairs_num += len(cycle)
        print(new_C)
        pairs = []
        for cycle in final_pairs:
            for pair in cycle:
                pairs.append(pair)
        pairs.sort(reverse=true)
        for pair in pairs:
            patients.pop(pair)
        final_cycles.extend(final_pairs)
    final_pairs = []
    print(final_cycles)
    for cycle in range(final_cycles):
        if len(cycle) == 2:
            final_pairs.append((cycle[0], cycle[1]))
            final_pairs.append((cycle[1], cycle[0]))
        if len(cycle) == 3:
            final_pairs.append((cycle[0], cycle[1]))
            final_pairs.append((cycle[1], cycle[2]))
            final_pairs.append((cycle[2], cycle[0]))
    print(final_pairs)
    return final_pairs

