import datetime
import hashlib
import json
from flask import Flask, jsonify

# Building the blockchain
class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, prev_hash = '0')
        
    # Create block function is called after the mine_block function has
    # completed solving the cryptographic puzzle, and the proof of work has
    # been obtained. This function basically creates an instance of the block
    # to be added in the chain variable
    def create_block(self, proof, prev_hash):
        block = {'block_number': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'nonce': proof,
                 'prev_block_hash': prev_hash}
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
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            current_block = chain[block_index]
            if current_block['prev_block_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['nonce']
            current_proof = current_block['nonce']
            hash_operation = hashlib.sha256(str(current_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = current_block
            block_index += 1
        return True

# Creating a Web server with Flask
app = Flask(__name__)
blockchain = Blockchain()

# Mining the blockchain
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    prev_block = blockchain.get_prev_block()
    proof_of_work = blockchain.get_proof_of_work(prev_block['nonce'])
    prev_hash = blockchain.hash(prev_block)
    new_block = blockchain.create_block(proof_of_work, prev_hash)
    response = {'message': 'We mined a new block',
                'block_number': new_block['block_number'],
                 'timestamp': new_block['timestamp'],
                 'nonce': new_block['nonce'],
                 'prev_block_hash': new_block['prev_block_hash']}
    return jsonify(response), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length of chain': len(blockchain.chain)}
    return jsonify(response), 200

app.run(host = '0.0.0.0', port = 5000)