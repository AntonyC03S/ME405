S0_INIT = 0
S1_LOOP = 1
S2_STUF = 2


class task1:

    #Class initializer can take in any number of parmaters 
    def __init__(self):
        self.state = 0
        self.count = 0



    # The generator can take in either no input or a single
    # tuple of inputs

    def task(self):

        while True:

            if self.state == S0_INIT:
                #Run state 0
                if self.count >= 3:
                    self.count = 0
                    self.state = 1       # Choose next state to un
                pass

            elif self.state == S1_LOOP:
                # Run state 1
                pass

            elif self.state == S2_STUF:
                #Run state 2
                pass

            else:
                raise ValueError("Invalid States")
            yield self.state


# Add the generator to the task list (see cotask.py docs)