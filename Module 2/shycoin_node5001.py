import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Building the cryptocurrency
class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, prev_hash = '0')
        self.nodes = set()
        
    # Create block function is called after the mine_block function has
    # completed solving the cryptographic puzzle, and the proof of work has
    # been obtained. This function basically creates an instance of the block
    # to be added in the chain variable
    def create_block(self, proof, prev_hash):
        block = {'block_number': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'nonce': proof,
                 'transactions': self.transactions,
                 'prev_block_hash': prev_hash}
        self.transactions = []
        self.chain.append(block)
        return block
    
    def get_prev_block(self):
        return self.chain[-1]
    
    # In our cryptographic problem, we also take into account the proof of work
    # of the privious block
    # We define the cryptographic problem using the SHA-256 hash function, and 
    # restrincting the hash to have exactly [leading_zeros] leading zeros
    # The function we are using to calculate the hash has to be unsymytric
    # Also, currently, as the block contains no data, we have not used it in 
    # generating the hash
    def get_proof_of_work(self, previous_nonce):
        nonce = 1
        solved = False;
        while solved is False:
            block_hash = hashlib.sha256(str(nonce**2 - previous_nonce**2).encode()).hexdigest()
            if block_hash[:4] == '0000':
                solved = True
            else:
                nonce += 1
        return nonce
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def verify_chain(self, chain):
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            current_block = chain[block_index]
            if current_block['prev_block_hash'] != self.hash(prev_block):
                return False
            previous_proof = prev_block['nonce']
            current_proof = current_block['nonce']
            hash_operation = hashlib.sha256(str(current_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            prev_block = current_block
            block_index += 1
        return True
    
    def add_transactions(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        prev_block = self.get_prev_block()
        return prev_block['index'] + 1
    
    def add_nodes(self, node_address):
        url = urlparse(node_address)
        self.nodes.add(url.netloc)
        
    def replace_chain(self):
        all_nodes = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in all_nodes:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length_of_chain = response.json()['length of chain']
                chain = response.json()['chain']
                if length_of_chain > max_length and self.is_chain_valid(chain):
                    max_length = length_of_chain
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
    
    

# Creating a Web server with Flask
app = Flask(__name__)
node_address = str(uuid4()).replace('-', '')
blockchain = Blockchain()

# Mining the blockchain
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    prev_block = blockchain.get_prev_block()
    proof_of_work = blockchain.get_proof_of_work(prev_block['nonce'])
    blockchain.add_transactions(sender = node_address, receiver = 'Aashay', amount = 1)
    prev_hash = blockchain.hash(prev_block)
    new_block = blockchain.create_block(proof_of_work, prev_hash)
    response = {'message': 'We mined a new block',
                'block_number': new_block['block_number'],
                 'timestamp': new_block['timestamp'],
                 'nonce': new_block['nonce'],
                 'transactions': new_block['transactions'],
                 'prev_block_hash': new_block['prev_block_hash']}
    return jsonify(response), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length of chain': len(blockchain.chain)}
    return jsonify(response), 200

# Adding new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in keys):
        return 'Malformed request syntax', 400
    index = blockchain.add_transactions(sender = json['sender'], receiver = json['receiver'], amount = json['amount'])
    response = {'message': f'This transaction is added to block {index}'}
    return jsonify(response), 201

# Connecting new nodes
@app.route('/connect_nodes', methods = ['POST'])
def connect_nodes():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "Bad Request", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'Nodes added',
                'total nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by longest chain
@app.route('/longest_chain', methods = ['GET'])
def longest_chain():
    validity = blockchain.verify_chain(blockchain.chain)
    if validity == True:
        response = {"message": "The chain is valid"}
    else:
        response = {"message": "The chain is invalid"}
    return jsonify(response), 200
    

# Checking if the blockchain is valid
@app.route('/check_validity', methods = ['GET'])
def check_validity():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced == True:
        response = {"message": "The chain is replaced",
                    'new_chain': blockchain.chain}
    else:
        response = {"message": "The chain was the longest beforehand",
                    'chain': blockchain.chain}
    return jsonify(response), 200

# Decentralising the blockchain


app.run(host = '0.0.0.0', port = 5001)