# Module 1 - Create a Blockchain
import datetime
import hashlib
import json
from flask import Flask, jsonify

#Part 1 - Building a blockchain

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')
        
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain)+1, 
                 'timestamp': str(datetime.datetime.now()), 
                 'proof': proof, 
                 'previous hash': previous_hash}
        self.chain.append(block)
        return block
    
    