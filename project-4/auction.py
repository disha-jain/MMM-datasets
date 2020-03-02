###
### auction.py - code for simulating user clicks and running the auction
###
### Project 4
### Markets, Mechanisms, and Machines
### University of Virginia
### Spring 2020
### https://uvammm.github.io/
###
### Originally created for Spring 2019 MMM course by 
### Mainuddin Ahmad Jonas
###

import redis
import json
import random
from threading import Timer

N_BIDS = 2500   # total number of bidding rounds
MIN_BID = 0.25 # minimum bid amount required to win a slot

def load_teams(r):
    """
    Load all team ids from the redis database, and 
    return as a list of team_ids
    """

    team_ids = r.get('teams')
    if not team_ids:
        return []
    team_ids = json.loads(team_ids)
    return team_ids

def load_team_info(r, team_id):
    """
    Given a team_id, load the information for that team
    from the database and return it
    """

    team_info = r.get(team_id)
    if not team_info:
        return None
    team_info = json.loads(team_info)
    return team_info

def set_message(r, team_id, message):
    """ 
    Appends message to team_id's message list in the db
    """

    team_info = load_team_info(r, team_id)
    if not team_info:
        return
    team_info['messages'].append(message)
    r.set(team_id, json.dumps(team_info))

def reduce_budget(r, team_id, amount):
    """
    Reduces team_id's budget by amount
    """

    team_info = load_team_info(r, team_id)
    if not team_info:
        return
    team_info['budget_left'] -= amount
    r.set(team_id, json.dumps(team_info))

def run_auction(r, auction_id):
    """
    Returns top 3 winning slots for the round auction_id. 
    If there were fewer than 3 bids of at least 
    MIN_BID amount, then returns fewer than 3 slots.
    """

    team_ids = load_teams(r)
    if not team_ids:
        return []

    bids = {}
    for team_id in team_ids:
        team_info = load_team_info(r, team_id)
        if not team_info:
            bids[team_id] = 0.0
            continue
        if not auction_id in team_info['bids']:
            bids[team_id] = random.random()
            # bids[team_id] = 0.0
            continue
        if team_info['bids'][auction_id] >= MIN_BID:
            bids[team_id] = team_info['bids'][auction_id]


    bids_lst = [(bids[k], random.random(), k) for k in bids]
    bids_lst.sort(reverse=True)

    winning_slots = [MIN_BID, MIN_BID, MIN_BID]
    slots = []
    if len(bids_lst) > 0:
        slots.append((bids_lst[0][2], bids_lst[0][0]))
        winning_slots[0] = max(bids_lst[0][0], MIN_BID)
    if len(bids_lst) > 1:
        slots.append((bids_lst[1][2], bids_lst[1][0]))
        winning_slots[1] = max(bids_lst[1][0], MIN_BID)
    if len(bids_lst) > 2:
        slots.append((bids_lst[2][2], bids_lst[2][0]))
        winning_slots[2] = max(bids_lst[2][0], MIN_BID)
    if len(bids_lst) > 3:
        slots.append((bids_lst[3][2], bids_lst[3][0]))

    wb = r.get('winning_bids')
    if wb:
        wb = json.loads(wb)
        wb.append(winning_slots)
        r.set('winning_bids', json.dumps(wb))

    return slots

def simulate_click(r):
    """
    First, determines the top 3 slots for current round of 
    bidding. Then simulates the process of user clicking on 
    one of the 3 slots (or none). Reduces the winning team's 
    budget, and stores results for all teams.
    """

    auction_id = r.get('current_auction_id')
    if not auction_id:
        return
    auction_id = auction_id.decode()
    slots = run_auction(r, auction_id)
    team_ids = load_teams(r)

    t = random.random()
    if t < 0.9:
        winner = None
    elif t < 0.96:
        winner = None
        if len(slots) >= 1:
            winner = slots[0][0]
            if len(slots) >= 2:
                price = max(MIN_BID, slots[1][1])
            else:
                price = MIN_BID

            reduce_budget(r, winner, price)
            msg = {'auction_id': auction_id,
                   'info': 'slot 1',
                   'price': price }
            set_message(r, winner, msg)
    elif t < 0.99:
        winner = None
        if len(slots) >= 2:
            winner = slots[1][0]
            if len(slots) >= 3:
                price = max(MIN_BID, slots[2][1])
            else:
                price = MIN_BID

            reduce_budget(r, winner, price)
            msg = {'auction_id': auction_id,
                   'info': 'slot 2',
                   'price': price }
            set_message(r, winner, msg)
        for team_id in team_ids:
            if team_id == winner:
                continue
            msg = {'auction_id': auction_id,
                    'info': 'user did not click on your ad',
                    'price': 0.0 }
            set_message(r, team_id, msg)
    else:
        winner = None
        if len(slots) >= 3:
            winner = slots[2][0]
            if len(slots) >= 4:
                price = max(MIN_BID, slots[3][1])
            else:
                price = MIN_BID

            reduce_budget(r, winner, price)
            msg = {'auction_id': auction_id,
                   'info': 'slot 3',
                   'price': price }
            set_message(r, winner, msg)

    for team_id in team_ids:
        if team_id == winner:
            continue
        msg = {'auction_id': auction_id,
                'info': 'user did not click on your ad',
                'price': 0.0 }
        set_message(r, team_id, msg)

    r.set('current_auction_id', int(auction_id) + 1)

def main():
    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    i = 0
    while i < N_BIDS:
        # Runs every 1 second till N_BIDS number of rounds is conducted
        t = Timer(1, simulate_click, args=[r])
        t.start()
        t.join()
        i += 1

if __name__ == '__main__':
    main()

