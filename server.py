from uuid import uuid4

import sys

from blockchain import Blockchain

from flask import Flask, jsonify, request, render_template

import ast

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-','')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/', methods=['GET'])
def index():
    numberBlock = len(blockchain.chain)
    numberNode = len(blockchain.nodes)+1
    return render_template('./index.html', numberBlock=numberBlock, numberNode=numberNode)

# Mine
@app.route('/mine', methods=['GET'])
def mine():
    # Run proof of work algorithm to get the next proof
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is '0' to signify that this node has mined a new coin
    blockchain.new_transaction(
        sender='0',
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    block = blockchain.new_block(proof)
    print (block)
    return render_template('mine.html', block = block)


# New transaction
@app.route('/transactions/new', methods=['GET'])
def new_transaction_get():
    return render_template('./transaction_new.html', flag=0)


@app.route('/transactions/new', methods=['POST'])
def new_transaction_post():
    values = {
        'sender' : request.form['sender'],
        'recipient' : request.form['recipient'],
        'amount' : request.form['amount'],
    }

    # Crate a new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    return render_template('./transaction_new.html', flag=1, index=index)


# All block
@app.route('/chain', methods=['GET'])
def full_chain():
    return render_template('./chain.html', chain=blockchain.chain, flag=0)


# Add nodes
@app.route('/nodes/register', methods=['GET'])
def register_get():
    return render_template('./register.html', flag = 0)


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    node = request.form['node']
    if (not blockchain.register_node(node)):
        ms = 'Can not add nodes. A node e.g: http://192.168.0.2:5000'
    else:
        ms = 'New nodes have been added'
    print (ms)
    return render_template('./register.html', flag=1, ms=ms)


@app.route('/nodes/all', methods=['GET'])
def all_nodes():
    print (blockchain.nodes )
    return render_template('./all_nodes.html', nodes=blockchain.nodes)

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        ms = 'Our chain was replaced'
    else:
        ms = 'Our chain is authoritative'

    return render_template('./chain.html', chain=blockchain.chain, flag=1, ms=ms)


@app.route('/chain_json', methods=['GET'])
def full_chain_json():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port listening')
    args = parser.parse_args()
    port = args.port
    app.debug = True
    app.run(host='0.0.0.0', port=port)
