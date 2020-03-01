###
### app.py - Auction Server 
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

# This is the server app for handling client requests. 
# It supports 3 API endpoints: /bid, /results, and /stats

# Documentation for each of the API endpoints is provided in the 
# notebook for the project.

import redis
import json
import uuid
from flask import Flask, jsonify, abort, request, make_response

MAX_BUDGET = 10000.0  # starting budget for each team

app = Flask(__name__, static_url_path = "")
r = redis.StrictRedis(host='localhost', port=6379, db=0)

def create_keys(n_teams):
    """
    Creates a secret key for each of the n_teams,
    and stores them in the 'keys.json' file.
    """

    team_ids = [str(i) for i in range(1, n_teams+1)]
    hmap = {}
    for team_id in team_ids:
        secret = uuid.uuid4().hex
        hmap[team_id] = secret
    with open('keys.json', 'w') as outfile:
        json.dump(hmap, outfile)

def init_db():
    """
    Initializes ther redis database
    """

    global r

    with open('keys.json') as key_file:    
        teams = json.load(key_file)
    r.set('teams', json.dumps([team_id for team_id in teams]))
    for team_id in teams:
        obj = {'key': teams[team_id], 'budget_left': MAX_BUDGET, 'bids': {}, 'messages': [] }
        r.set(team_id, json.dumps(obj))
    r.set('current_auction_id', '1')
    winning_bids = []
    r.set('winning_bids', json.dumps(winning_bids))
        

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.route('/bid', methods = ['POST'])
def post_bid():
    """
    Hanldes /bid requests
    """

    global r

    if not request.json:
        abort(400)
    if not 'team_id' in request.json or not 'key' in request.json or\
            not 'auction_id' in request.json or not 'bid_amount' in request.json:
                return jsonify({ 'error': 'Invalid request' }), 400

    team_id = str(request.json['team_id'])
    key = str(request.json['key'])
    auction_id = str(request.json['auction_id'])
    amount = str(request.json['bid_amount'])

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({ 'error': 'Invalid amount format' }), 400

    try:
        auction_id = int(auction_id)
    except ValueError:
        return jsonify({ 'error': 'Invalid auction_id' }), 400

    cur_auction_id = r.get('current_auction_id')
    if not cur_auction_id:
        return jsonify({ 'error': 'Server encountered an issue' }), 500
    cur_auction_id = cur_auction_id.decode()


    team_info = r.get(team_id)
    if not team_info:
        return jsonify({ 'error': 'Invalid team_id' }), 400

    team_info = json.loads(team_info)
    if not key == team_info['key']:
        return jsonify({ 'error': 'Invalid key' }), 400

    if auction_id < int(cur_auction_id):
        return jsonify({ 'error': 'auction_id too old' }), 400

    if amount < 0.0 or amount > team_info['budget_left']:
        return jsonify({ 'error': 'Invalid bid amount' }), 400

    team_info['bids'][auction_id] = amount
    r.set(team_id, json.dumps(team_info))

    return jsonify({ 'message': 'Successfully submitted the bid' }), 200

@app.route('/results', methods = ['POST'])
def get_info():
    """
    Hanldes /results requests
    """

    global r

    if not request.json:
        abort(400)
    if not 'team_id' in request.json or not 'key' in request.json or\
            not 'count' in request.json:
                return jsonify({ 'error': 'Invalid request' }), 400

    team_id = str(request.json['team_id'])
    key = str(request.json['key'])
    count = str(request.json['count'])


    team_info = r.get(team_id)
    if not team_info:
        return jsonify({ 'error': 'Invalid team_id' }), 400

    team_info = json.loads(team_info)
    if not key == team_info['key']:
        return jsonify({ 'error': 'Invalid key' }), 400

    try:
        count = int(count)
    except ValueError:
        return jsonify({ 'error': 'Count should be an integer' }), 400

    cur_auction_id = r.get('current_auction_id')
    if not cur_auction_id:
        return jsonify({ 'error': 'Server encountered an issue' }), 500
    cur_auction_id = cur_auction_id.decode()

    results = team_info['messages'][-count:]
    budget_left = team_info['budget_left']

    return jsonify({ 'results': results, 'budget_left': budget_left, 'current_auction_id': cur_auction_id }), 200

@app.route('/stats', methods = ['POST'])
def get_stats():
    """
    Handles /stats requests
    """

    global r

    if not request.json:
        abort(400)
    if not 'team_id' in request.json or not 'key' in request.json:
        return jsonify({ 'error': 'Invalid request' }), 400

    team_id = str(request.json['team_id'])
    key = str(request.json['key'])

    team_info = r.get(team_id)
    if not team_info:
        return jsonify({ 'error': 'Invalid team_id' }), 400

    team_info = json.loads(team_info)
    if not key == team_info['key']:
        return jsonify({ 'error': 'Invalid key' }), 400

    winning_bids = r.get('winning_bids')
    if not winning_bids:
        return jsonify({ 'error': 'Server encountered an error' }), 500

    winning_bids = json.loads(winning_bids)
    COUNT = 10
    if len(winning_bids) < COUNT:
        return jsonify({ 'error': 'Stats not yet available, try again later' }), 500
    winning_bids = winning_bids[-COUNT:]

    slots_avg = []
    slots_avg.append(sum([t[0] for t in winning_bids]) / COUNT)
    slots_avg.append(sum([t[1] for t in winning_bids]) / COUNT)
    slots_avg.append(sum([t[2] for t in winning_bids]) / COUNT)

    return jsonify({ 'stats': slots_avg }), 200
    
if __name__ == '__main__':
    # create_keys(10)
    init_db()
    app.run(debug=True)
