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



    