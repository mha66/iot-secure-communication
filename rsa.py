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
        x = (a ** d) % n
        
        if x == 1 or x == n - 1:
            continue
            
        # Inner loop: square x continuously
        for _ in range(r - 1):
            x = (x * x) % n
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

    