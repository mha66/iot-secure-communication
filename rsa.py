import random 

def gcd_extended_euclidean(a, b, x, y):

    # Base Case 
    if a == 0: 
        x[0] = 0
        y[0] = 1
        return b 

    x1, y1 = [0], [0]
    gcd = gcd_extended_euclidean(b % a, a, x1, y1)

    # Update x and y using results of 
    # recursive call 
    x[0] = y1[0] - (b // a) * x1[0] 
    y[0] = x1[0] 
    return gcd 

def find_gcd_extended(a, b):
    x, y = [1], [1]
    gcd = gcd_extended_euclidean(a, b, x, y)
    return gcd, x[0], y[0]

# A pre-computed list of the first few primes
FIRST_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 
                61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 
                131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 
                193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 
                263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337]

def generate_prime_candidate(length):
    # Generate random bits
    p = random.getrandbits(length)
    
    # Apply Bitwise Masks:
    # Set the Lowest Significant Bit to 1 (ensures the number is odd)
    # Set the Most Significant Bit to 1 (ensures it is exactly 'length' bits long)
    p |= (1 << length - 1) | 1
    return p

def miller_rabin(n, k=40):
    # Handle base cases
    if n == 2 or n == 3: return True
    if n <= 1 or n % 2 == 0: return False

    # Find r and d such that n - 1 = 2^r * d (where d is odd)
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Run the test k times
    for _ in range(k):
        # Pick a random base 'a'
        a = random.randrange(2, n - 1)
        
        # x = a^d % n 
        x = modular_pow(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
            
        # Inner loop: square x continuously
        for _ in range(r - 1):
            x = modular_pow(x, 2, n)
            if x == n - 1:
                break
        else:
            # If the inner loop is completed and x never hit n - 1, it's composite (not prime)
            return False
            
    return True

def generate_rsa_prime(bits):
    while True:
        # Step 1: Get a random odd number of the right size
        candidate = generate_prime_candidate(bits)
        
        # Step 2: Quick low-level division check
        is_composite = False
        for prime in FIRST_PRIMES:
            if candidate % prime == 0:
                is_composite = True
                break
                
        if is_composite:
            continue # Throw it out and try a new number
            
        # Step 3: The rigorous Miller-Rabin test
        if miller_rabin(candidate, 40):
            return candidate # We found a prime!
        
# Example: base=7, exponent=5, modulus=13 --> 7^5 % 13
# 5 --> 101
# [(7^1) % 13 * (7^4) % 13] % 13
def modular_pow(base, exponent, modulus):
    result = 1
    base = base % modulus
    
    while exponent > 0:
        # If the current bit of the exponent is 1 (odd), multiply the result
        if (exponent % 2) == 1:
            result = (result * base) % modulus
            
        # Shift exponent right by 1 bit (divide by 2)
        exponent = exponent >> 1
        
        # Square the base
        base = (base * base) % modulus
        
    return result

class RSA:
    def __init__(self, p=None, q=None, e=None, n=None):
        if n is not None and e is not None:
            self.n = n
            self.e = e
            return
        
        while True:
            self.p = generate_rsa_prime(1024) if p is None else p
            self.q = generate_rsa_prime(1024) if q is None else q
            while self.q == self.p:
                self.q = generate_rsa_prime(1024)
            self.n = self.p * self.q  #n is 2048 bits long
            self.phi = (self.p - 1) * (self.q - 1)

            self.e = 65537 if e is None else e # 65537 --> 10000000000000001 in binary, so it has only 2 bits set to 1, which makes it efficient for encryption
            gcd, _, self.d = find_gcd_extended(self.phi, self.e)
            if gcd == 1:
                if self.d < 0:
                    self.d += self.phi
                break
    
    def __str__(self):
        return f"p={self.p}, q={self.q}\nn={self.n}, Ø(n)={self.phi}\ne={self.e}, d={self.d}" +\
                f"\npublic key: {{{self.e}, {self.n}}}\nprivate key: {{{self.d}, {self.n}}}"
    
    def encrypt(self, plaintext: int):
        return modular_pow(plaintext, self.e, self.n)
    
    def decrypt(self, ciphertext: int):
        return modular_pow(ciphertext, self.d, self.n)
                
        


def main():
    rsa = RSA()
    print(rsa)
    encr = rsa.encrypt(12)
    decr = rsa.decrypt(encr)

    print(f"encrypted: {encr}")
    print(f"decrypted: {decr}")

if __name__ == "__main__":
    main()