import struct
import hashlib # To compare results

# SHA-256 Constants as per FIPS PUB 180-4

# Initial hash values (first 32 bits of the fractional parts of the square roots of the first 8 primes 2..19)
H_INITIAL = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
]

# Round constants (first 32 bits of the fractional parts of the cube roots of the first 64 primes 2..311)
K_CONSTANTS = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
]

# Helper functions for SHA-256 (all operations on 32-bit words)
# Modulo 2^32 is implicitly handled by Python's bitwise operations when results are masked with 0xFFFFFFFF.

def _rotr(x, n):
    """Right rotate x by n bits."""
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

def _shr(x, n):
    """Right shift x by n bits."""
    return (x >> n) & 0xFFFFFFFF

# Logical functions
def _ch(x, y, z):
    """Choose: (x AND y) XOR ((NOT x) AND z)"""
    return ((x & y) ^ (~x & z)) & 0xFFFFFFFF

def _maj(x, y, z):
    """Majority: (x AND y) XOR (x AND z) XOR (y AND z)"""
    return ((x & y) ^ (x & z) ^ (y & z)) & 0xFFFFFFFF

def _Sigma0(x): # Uppercase Sigma_0
    """ROTR(x, 2) XOR ROTR(x, 13) XOR ROTR(x, 22)"""
    return (_rotr(x, 2) ^ _rotr(x, 13) ^ _rotr(x, 22)) & 0xFFFFFFFF

def _Sigma1(x): # Uppercase Sigma_1
    """ROTR(x, 6) XOR ROTR(x, 11) XOR ROTR(x, 25)"""
    return (_rotr(x, 6) ^ _rotr(x, 11) ^ _rotr(x, 25)) & 0xFFFFFFFF

def _sigma0(x): # Lowercase sigma_0
    """ROTR(x, 7) XOR ROTR(x, 18) XOR SHR(x, 3)"""
    return (_rotr(x, 7) ^ _rotr(x, 18) ^ _shr(x, 3)) & 0xFFFFFFFF

def _sigma1(x): # Lowercase sigma_1
    """ROTR(x, 17) XOR ROTR(x, 19) XOR SHR(x, 10)"""
    return (_rotr(x, 17) ^ _rotr(x, 19) ^ _shr(x, 10)) & 0xFFFFFFFF


def _pad_message(message_bytes: bytes) -> bytes:
    """Pads the message according to SHA-256 specification."""
    original_length_bits = len(message_bytes) * 8
    
    # Append a single '1' bit (which is byte 0x80)
    padded_message = message_bytes + b'\x80'
    
    # Append '0' bits (0x00 bytes) until message length in bytes is 56 (mod 64)
    # This means len(padded_message) % 64 == 56
    # which is equivalent to (len(padded_message) * 8) % 512 == 448
    while len(padded_message) % 64 != 56:
        padded_message += b'\x00'
        
    # Append original length in bits as a 64-bit big-endian integer (8 bytes)
    # struct.pack('>Q') packs into big-endian unsigned long long (64-bit)
    padded_message += struct.pack('>Q', original_length_bits)
    
    return padded_message

def sha256(message_input) -> bytes:
    """
    Computes the SHA-256 hash of the input message using a raw implementation.
    Input can be a string (will be UTF-8 encoded) or bytes.
    Returns the hash as a bytes object (32 bytes).
    """
    if isinstance(message_input, str):
        message_bytes = message_input.encode('utf-8')
    elif isinstance(message_input, bytes):
        message_bytes = message_input
    else:
        raise TypeError("Input must be a string or bytes.")

    # 1. Preprocessing: Pad the message
    padded_message = _pad_message(message_bytes)
    
    # 2. Initialize hash values (H_0 to H_7)
    # These are the working hash states, make a mutable copy
    h_states = list(H_INITIAL)

    # 3. Process the message in 512-bit (64-byte) chunks
    for i in range(0, len(padded_message), 64):
        chunk = padded_message[i:i+64]
        
        # a. Create message schedule W (array of 64 32-bit words)
        W = [0] * 64
        # First 16 words (W_0 to W_15) are from the chunk directly (big-endian)
        for t in range(16):
            # struct.unpack('>I') unpacks 4 bytes big-endian into an unsigned int (32-bit)
            W[t] = struct.unpack('>I', chunk[t*4 : t*4+4])[0]
            
        # Extend the first 16 words into the remaining 48 words (W_16 to W_63)
        for t in range(16, 64):
            s0 = _sigma0(W[t-15])
            s1 = _sigma1(W[t-2])
            W[t] = (W[t-16] + s0 + W[t-7] + s1) & 0xFFFFFFFF # Modulo 2^32
            
        # b. Initialize working variables (a, b, c, d, e, f, g, h) with current hash values
        a, b, c, d, e, f, g, h_var = h_states # h_var is the working variable 'h'
        
        # c. Compression function main loop (64 rounds)
        for t in range(64):
            S1 = _Sigma1(e)
            ch_val = _ch(e, f, g) # 'ch' is already a function name
            temp1 = (h_var + S1 + ch_val + K_CONSTANTS[t] + W[t]) & 0xFFFFFFFF # Modulo 2^32
            
            S0 = _Sigma0(a)
            maj_val = _maj(a, b, c) # 'maj' is already a function name
            temp2 = (S0 + maj_val) & 0xFFFFFFFF # Modulo 2^32
            
            # Update working variables
            h_var = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF # Modulo 2^32
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF # Modulo 2^32
            
        # d. Update hash states (add compressed chunk to current hash values)
        h_states[0] = (h_states[0] + a) & 0xFFFFFFFF
        h_states[1] = (h_states[1] + b) & 0xFFFFFFFF
        h_states[2] = (h_states[2] + c) & 0xFFFFFFFF
        h_states[3] = (h_states[3] + d) & 0xFFFFFFFF
        h_states[4] = (h_states[4] + e) & 0xFFFFFFFF
        h_states[5] = (h_states[5] + f) & 0xFFFFFFFF
        h_states[6] = (h_states[6] + g) & 0xFFFFFFFF
        h_states[7] = (h_states[7] + h_var) & 0xFFFFFFFF

    # 4. Produce final hash value (concatenate h0, h1, ..., h7)
    # Each h_state value is a 32-bit integer, pack it as 4 bytes big-endian
    final_hash_bytes = b''
    for val in h_states:
        final_hash_bytes += struct.pack('>I', val)
        
    return final_hash_bytes