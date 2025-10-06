def collatz(n):

    # For the see case just yield n 
    yield n

    # For the general case check th stop
    # condition then process the value
    while n != 1:
        # Case where n is even
        if n % 2 == 0:
            n //= 2
        # Case where n is odd 
        else:
            n = 3 * n + 1
        # Yield the general case
        yield n 

# Create a generator object
my_seq = collatz(42)

# Run a single iteration of the generator
print("Signle Iteration:")
print(next(my_seq))
# print(next(my_seq))

# Create a generator objects and iternate throught it 
print("for() Loop:")
for num in collatz(42):
    print(num)

# Create a generator then process it and
# store the output sequence in a list 
my_list = list(collatz(13)) 
print("List:")
print(my_list)