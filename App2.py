from web3 import Web3
from time import perf_counter
import gzip
import json
import os

# Connect to Ganache
ganache_url = "HTTP://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Check connection
assert web3.is_connected(), "Failed to connect to Ethereum node!"

# Load contract details
contract_address = "0xab10d99ef72dc79E00B77d54Df57B79aFfA94966"
with open("GasOptimization_abi.json") as f:
    contract_abi = json.load(f)
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Wallet setup
private_key = "0x933be872cda50429a4e7f9106536817c4ed7aa14653d0467d93d44ed1209aacc"
sender_address = "0x90908E94ddC71E8dC6bd086F5e25dD413d75e06D"

# Function to calculate gas and transaction cost
def calculate_costs(transaction_receipt):
    gas_used = transaction_receipt['gasUsed']
    gas_price = web3.eth.gas_price
    transaction_cost = gas_used * gas_price
    return gas_used, transaction_cost

# Function to compress and store data
def compress_and_store(file_path, id):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found!")

    # Read dataset
    with open(file_path, "r") as f:
        data = f.read()

    # Print uncompressed data size
    uncompressed_size = len(data.encode())
    print(f"Uncompressed Data Size: {uncompressed_size} bytes")

    # Compress data with gzip and measure time
    start_time = perf_counter()  # Start timing
    compressed_data = gzip.compress(data.encode())
    end_time = perf_counter()  # End timing
    compression_time = end_time - start_time

    # Print compression results
    compressed_size = len(compressed_data)
    print(f"Compressed Data Size: {compressed_size} bytes")
    print(f"Compression Time: {compression_time:.6f} seconds")

    # Build and send transaction for uncompressed data
    nonce = web3.eth.get_transaction_count(sender_address)
    transaction_uncompressed = contract.functions.storeData(id, data.encode()).build_transaction({
        'from': sender_address,
        'nonce': nonce,
        'gas': 12000000,
        'gasPrice': web3.eth.gas_price
    })
    signed_txn_uncompressed = web3.eth.account.sign_transaction(transaction_uncompressed, private_key)
    txn_hash_uncompressed = web3.eth.send_raw_transaction(signed_txn_uncompressed.raw_transaction)
    receipt_uncompressed = web3.eth.wait_for_transaction_receipt(txn_hash_uncompressed)

    gas_used_uncompressed, transaction_cost_uncompressed = calculate_costs(receipt_uncompressed)
    print(f"Gas Used for Uncompressed Data: {gas_used_uncompressed}")
    print(f"Transaction Cost for Uncompressed Data: {web3.from_wei(transaction_cost_uncompressed, 'ether')} ETH")

    # Build and send transaction for compressed data
    transaction_compressed = contract.functions.storeData(id + 1, compressed_data).build_transaction({
        'from': sender_address,
        'nonce': nonce + 1,
        'gas': 12000000,
        'gasPrice': web3.eth.gas_price
    })
    signed_txn_compressed = web3.eth.account.sign_transaction(transaction_compressed, private_key)
    txn_hash_compressed = web3.eth.send_raw_transaction(signed_txn_compressed.raw_transaction)
    receipt_compressed = web3.eth.wait_for_transaction_receipt(txn_hash_compressed)

    gas_used_compressed, transaction_cost_compressed = calculate_costs(receipt_compressed)
    print(f"Gas Used for Compressed Data: {gas_used_compressed}")
    print(f"Transaction Cost for Compressed Data: {web3.from_wei(transaction_cost_compressed, 'ether')} ETH")

    # Verify stored data
    verify_data(id)
    verify_data(id + 1)

# Function to verify stored data
def verify_data(id):
    stored_data = contract.functions.getData(id).call()
    print(f"Retrieved Data for ID {id}: {stored_data}")

# Main function
if _name_ == "_main_":
    file_path = input("Enter the path to your dataset file (e.g., .txt, .csv): ").strip()
    try:
        compress_and_store(file_path, id=1)
    except Exception as e:
        print(f"Error: {e}")
