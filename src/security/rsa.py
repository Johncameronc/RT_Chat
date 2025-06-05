import random
import time
import os
from pathlib import Path
from .sha256 import sha256

def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    # Miller-Rabin primality test
    # Find r, d such that n-1 = 2^r * d
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1

    bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    if n < 40: # For small n, only test bases smaller than n
        bases = [b for b in bases if b < n]


    for a in bases:
        if a >= n: # Base must be < n
            continue
        
        # x = a^d % n
        x = pow(a, d, n) 
        if x == 1 or x == n - 1:
            continue

        is_composite = True
        for _ in range(r - 1):
            x = pow(x, 2, n) # x = x^2 % n
            if x == n - 1:
                is_composite = False
                break
        
        if is_composite:
            return False
    return True

def generate_prime_number(min_val: int, max_val: int) -> int:
    num = random.randrange(min_val, max_val + 1) # range is exclusive for the end
    
    # Ensure the number is odd
    if num % 2 == 0:
        num += 1
        if num > max_val: # Adjust if it goes out of bounds
             num -=2 # Pick previous odd if possible or re-evaluate range logic

    while not is_prime(num):
        num += 2
        if num > max_val: # If we exceed max, wrap around or pick a new random start
            num = random.randrange(min_val, max_val + 1)
            if num % 2 == 0:
                num +=1
                if num > max_val and min_val % 2 == 1:
                    num = min_val
                elif num > max_val:
                    num = min_val + 1


    return num

# Function to calculate modular inverse using extended Euclidean algorithm
def mod_inverse(a: int, m: int) -> int | None:
    m0, x0, x1 = m, 0, 1
    
    if m == 1:
        return 0
        
    while a > 1:
        if m == 0: # No inverse if m is 0 (or if a became 0 during process, though gcd check handles this)
            return None
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
        
    if x1 < 0:
        x1 += m0
        
    if a != 1: # after loop a is gcd(original_a, m0)
        return None

    return x1

def generate_keys() -> tuple[int, int, int]:
    time_start = time.perf_counter()

    # aumentando o intervalo para números maiores
    p = generate_prime_number(10**50, 10**51)
    q = generate_prime_number(10**50, 10**51)
    
    # ensure p and q are different
    while p == q:
        q = generate_prime_number(10**50, 10**51)

    n = p * q
    phi_n = (p - 1) * (q - 1)

    # usando 65537 como valor de e (comum em rsa)
    e = 65537
    
    # ensure gcd(e, phi_n) == 1
    d = mod_inverse(e, phi_n)
    while d is None:
        e = 65537  # mantém e fixo em 65537
        d = mod_inverse(e, phi_n)

    time_end = time.perf_counter()
    time_elapsed = time_end - time_start

    print(f"key generation time: {time_elapsed:.4f} seconds")
    
    return e, d, n

def encrypt(message_bytes: bytes, public_key: int, n: int) -> list[int]:
    encrypted_message = []
    # Go through each byte (number between 0 and 255) in the original message
    for byte_val in message_bytes:
        # Encrypt the byte using RSA formula: (byte_val ^ public_key) % n
        encrypted_value = pow(byte_val, public_key, n)
        encrypted_message.append(encrypted_value)
    return encrypted_message

def decrypt(encrypted_data: list[int], private_key: int, n: int) -> bytes:
    original_bytes_list = []
    # Go through each encrypted number
    for value in encrypted_data:
        # Decrypt using RSA formula: (value ^ private_key) % n
        original_byte = pow(value, private_key, n)
        original_bytes_list.append(original_byte)
    return bytes(original_bytes_list)

def sign_message(message_text: str, private_key_d: int, n_modulus: int) -> int:
    # 1. encode the message string to bytes
    message_bytes = message_text.encode('utf-8')

    # 2. hash the bytes usando sha256_raw
    hashed_message_digest = sha256(message_bytes)

    # 3. convert the hash digest (bytes) to an integer
    hash_integer = int.from_bytes(hashed_message_digest, byteorder='big')

    # 4. apply padding to ensure hash_integer < n_modulus
    # usando um padding simples: hash_integer % n_modulus
    padded_hash = hash_integer % n_modulus

    # 5. perform the rsa signature operation
    signature_integer = pow(padded_hash, private_key_d, n_modulus)
    
    return signature_integer

def verify_signature(message_text: str, signature_integer: int, public_key_e: int, n_modulus: int) -> bool:
    # 1. encode the message string to bytes
    message_bytes = message_text.encode('utf-8')

    # 2. hash the bytes usando sha256_raw
    original_hashed_message_digest = sha256(message_bytes)

    # 3. convert the original hash digest (bytes) to an integer
    original_hash_integer = int.from_bytes(original_hashed_message_digest, byteorder='big')

    # 4. apply the same padding
    padded_hash = original_hash_integer % n_modulus

    # 5. "decrypt" the signature using the public key
    decrypted_hash_integer = pow(signature_integer, public_key_e, n_modulus)

    # 6. compare the decrypted hash with the original padded hash
    return decrypted_hash_integer == padded_hash