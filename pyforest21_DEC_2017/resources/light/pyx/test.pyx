

def myfun(n):
    '''This is very intresting test function.
    '''
    cdef double res = 0.0
    cdef int i = 0
    for i in range(n):
        res = res + i
    return res
    
    
    
