# The generator can take in either no input or a single
# tuple of inputs

def task():
    state = 0

    while True:

        if state == 0:
            #Run state 0
            if count >= 3:
                count = 0
                state = 1       # Choose next state to un
            pass

        elif state == 1:
            # Run state 1
            pass

        elif state == 2:
            #Run state 2
            pass

        yield state


# Add the generator to the task list (see cotask.py docs)