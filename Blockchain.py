from Functions import *


class Blockchain( object ):
    def __init__(self):
        self.difficulty = 0
        self.coinbase = 1000

        nonce = 0
        while True:
            block = {
                'index': 0,
                'timestamp': timestamp(),
                'transactions': [],
                'nonce': nonce,
                'previous_block_hash': 0,
            }
            hash = block_hash(block)
            if hash[:self.difficulty] == '0' * self.difficulty:
                break

        self.blockchain = [block]
        self.current_transactions = []

    def mine(self, miner_address):
        """Create a new block"""

        # Verify the transactions
        self.verify_transactions()

        # Reward the miner
        coinbase = {
            'sender': -1,
            'receiver': miner_address,
            'amount': self.coinbase,
        }
        transactions_verified = [coinbase] + self.current_transactions

        # Find a nonce that verify the Proof of Work
        nonce = 0
        while True:
            block = {
                'index': len( self.blockchain ),
                'timestamp': timestamp(),
                'transactions': transactions_verified,
                'nonce': nonce,
                'previous_block_hash': self.last_block_hash,
            }
            hash = block_hash(block)
            if hash[:self.difficulty] == '0' * self.difficulty:
                break

        # Propose new block to the blockchain
        self.blockchain.append( block )
        self.clear_transactions()
        print( self.last_block )
        print( self.verify_chain())
        print( self.last_block_hash)
        return block

    def transfer(self, sender_address, receiver_address, amount):
        """Create a new transaction"""
        self.current_transactions.append( {
            'sender': sender_address,
            'receiver': receiver_address,
            'amount': amount,
        } )
        return self.current_transactions

    def balance(self, address, block_number=-1):
        if block_number == -1:
            block_number = len( self.blockchain )
        else:
            block_number += 1

        def amounts():
            for block in self.blockchain[0:block_number]:
                for transaction in block['transactions']:
                    if transaction['receiver'] == address:
                        yield transaction['amount']
                    elif transaction['sender'] == address:
                        yield -transaction['amount']

        balance = 0
        for amount in amounts():
            balance += amount
        return balance

    def all_balances(self, block_number=-1):
        if block_number == -1:
            block_number = len( self.blockchain )
        else:
            block_number += 1

        account_balances = {}
        for block in self.blockchain[0:block_number]:
            for transaction in block['transactions']:
                sender = transaction['sender']
                receiver = transaction['receiver']
                amount = transaction['amount']

                if sender not in account_balances:
                    account_balances[sender] = - amount
                else:
                    account_balances[sender] -= amount

                if receiver not in account_balances:
                    account_balances[receiver] = amount
                else:
                    account_balances[receiver] += amount
        return account_balances

    def clear_transactions(self):
        self.current_transactions = []

    def verify_transactions(self, block=-1, clear_current_tx = True ):
        # Check if transactions are allowed
        if -1 == block:
            transactions_to_verify = self.current_transactions
        else :
            transactions_to_verify = self.blockchain[block]['transactions']

        account_balances = {}
        transactions_verified = []
        false_tx = False
        for transaction in transactions_to_verify:
            sender = transaction['sender']
            receiver = transaction['receiver']
            amount = transaction['amount']

            if sender not in account_balances:
                account_balances[sender] = self.balance( sender, block )

            # If transaction is OK then it will be added to the block
            if account_balances[sender] >= amount:
                account_balances[sender] -= amount
                if receiver not in account_balances:
                    account_balances[receiver] = self.balance( sender, block )
                account_balances[receiver] += amount
                transactions_verified.append( transaction )
            elif sender != -1:
                false_tx = True

        if clear_current_tx:
            self.current_transactions = transactions_verified

        return false_tx

    def verify_chain(self):
        first_block = self.blockchain[0]
        first_block_tx = first_block['transactions']

        false_tx = False
        if len(first_block_tx) > 0:
            amount = first_block_tx[0]['amount']
            if len( first_block_tx ) > 1 or amount > self.coinbase:
                false_tx = True

        previous_block_hash = block_hash(first_block)
        for i, block in enumerate(self.blockchain[1:-1]):
            if self.verify_transactions(i, False):
                false_tx = True
            if block['previous_block_hash'] != previous_block_hash:
                false_tx = True
            previous_block_hash = block_hash(block)
        return false_tx

    @property
    def last_block(self):
        """Last block"""
        return self.blockchain[-1]

    @property
    def last_block_hash(self):
        block = self.last_block
        return block_hash( block )
