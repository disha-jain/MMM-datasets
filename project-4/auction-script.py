
# w we provide some skeleton code for this task

import requests
import json
import time
import random

team_id = "9" # change it to the team ID we'll provide you through slack
key = "d0bb78146802430fa6a3f65094958d25"  # change it to the key we'll provide you through slack
url = 'http://ec2-18-218-112-198.us-east-2.compute.amazonaws.com:8080'
MAX_AUCTION_ID = 2500   # this may change; you should use it as a parameter in your algorithm to adjust your strategy


def bid_algorithm(budget_left, auction_id, last_bid, won, price_paid, last_two_aves,high_bid_warning, high_bid_count ):
    """
    this is your bidding algorithm
    """
    
    if high_bid_warning:
        if high_bid_count < 10:
            high_bid_count+=1
            return 0
        else:
            high_bid_count = 0
            high_bid_warning = False
    random_seed= random.random()
    if random_seed < 0.06 and random_seed > 0:
        bid_amount = random.random() * 200 + 400
        if bid_amount < budget_left:
            return bid_amount
    bid_amount = 0
    if not won:
        diff_slot_1 = last_two_aves[0][0] - last_two_aves[1][0]
        diff_slot_2 = last_two_aves[0][1] - last_two_aves[1][1]
        diff_slot_3 = last_two_aves[0][2] - last_two_aves[1][2]
        if diff_slot_1 <= 0 and last_two_aves[0][0] + 2 < budget_left:
            bid_amount = last_two_aves[0][0] + 1 + random.random()
        elif diff_slot_2 <= 0 and last_two_aves[0][1] + 2 < budget_left:
            bid_amount = last_two_aves[0][1] + 1 + random.random()
        elif diff_slot_3 <= 0 and last_two_aves[0][2] + 2 < budget_left:
            bid_amount = last_two_aves[0][2] + 1 + random.random()
        else:
            if diff_slot_1 >= 2* last_two_aves[1][0]:
                high_bid_warning = True
                return 0
            if last_two_aves[0][2] < budget_left:
                bid_amount = last_two_aves[0][2]
                # print(bid_algorithm)
            else:
                bid_amount = 0
    elif won and price_paid + 2 < budget_left:
        bid_amount = price_paid + 1 + random.random()
    elif auction_id in range(auction_id- (int) (auction_id/4), auction_id +1):
        bid_amount = budget_left/5
    else:
        bid_amount = budget_left
#     print(bid_amount)
    return bid_amount

def main():
    count_won = 0
    num = 0
    auction_id = 0
    last_bid = 1
    high_bid_warning = False
    high_bid_count = 0
    last_winning_price = -1
    last_two_aves = [[0,0,0],[0,0,0]]
    count = 2
#    print("outside while")
    while True:
#         print("isnide while")
        num += 1
        body = {'team_id': team_id,
                'key': key,
                'count': 1
               }
        r = requests.post(url + '/results', json=body)
        if r and r.json() and 'current_auction_id' in r.json():
            print(r.json())
            t = int(r.json()['current_auction_id'])
            if t > int(auction_id):  # new auction_id found. send new bid
                print("pls")
                auction_id = t
                
                # you could potentially call the /stats API here if your algorithm uses that 
                # create the body for the /bid request
                stats_body = {'team_id': team_id,
                        'key': key }
                s = requests.post(url + '/stats', json=stats_body) 
                print(s.json())
                if 'stats' in s.json():
                    last_two_aves[1] = last_two_aves[0]
                    last_two_aves[0] = s.json().get('stats')
                res_body = {'team_id': team_id,
                        'key': key,
                        'count': count }

                res = requests.post(url + '/results', json=res_body) 
                res_json = res.json()
#                 if last_winning_price is not -1:
#                     print(res_json) 
                print(res_json) 
                budget_left = res_json.get('budget_left')
                try:
                    price_paid = res_json.get('results')[count-1]['price']
                except:
                    price_paid = 0
                won = price_paid > 0
                if won:
                    last_winning_price = price_paid
                    count_won +=1
                else:
                    last_winning_price = -1
                if budget_left <= 0:
                    break

                # information to determine the bid amount
                bid_amount = bid_algorithm(budget_left, auction_id, last_bid, won, last_winning_price, last_two_aves, high_bid_warning, high_bid_count) # call your algorithm to determine how much to bid
                last_bid = bid_amount
                # create the body for the /bid request
                body = {'team_id': team_id,
                        'key': key,
                        'auction_id': auction_id,
                        'bid_amount': bid_amount }
                r = requests.post(url + '/bid', json=body) 
#                 print(r.json()) 


        time.sleep(0.1) # please do this to avoid flooding the server
        
        if int(auction_id) == MAX_AUCTION_ID:
            break
    print("rounds: ", num, "won: ", count_won, "percentage: ", count_won/num)

if __name__ == "__main__":
    main()
