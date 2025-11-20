from ulab.numpy import array, arange, zeros, transpose, cos, sin # type: ignore
import matplotlib.pyplot as plt
from math import pi

class State_Estimation:

    def __init__(self,K = 250*2*pi/60/4.5, tau = 0.1, l = 0.141, r = 0.035):
        # Electromechanical properties
        self._K   = K         # Motor Gain [rad/(V*s)]
        self._tau = tau       # Motor Time Constant [s]
        self._r   = r         # Wheel radius [m] 
        self._l   = l         # Track Width (Wheel Center to Wheel Center) [m]
        self.xout = array([ [0],
                        [0],
                        [0],
                        [0],
                        [0],
                        [0] ])
        
        # Define a column of time values
        self.tout = [0]
        self.yout = []

    def system_eqn_CL_xd(self, x, err_L, err_R):
        u = array([ [ err_L ], 
                    [ err_R ] ])       
        
        # State equations
        xd =  array( [[ (1/self._tau)     * (self._K*u[0,0] - x[0,0]) ],    #Ω L
                    [   (1/self._tau)     * (self._K*u[1,0] - x[1,0]) ],    #Ω S
                    [   (self._r/2)       * ( x[1,0]        + x[0,0]) ],    #S
                    [   (self._r/self._l) * ( x[1,0]        - x[0,0]) ]])   #Ψ
        return xd, 

    def system_eqn_CL_y(self, x):
        y  =  array( [ [ x[2,0] - (x[3,0] * (self._l/2))       ]     #S_L
                    [    x[2,0] + (x[3,0] * (self._l/2))       ],    #S_R
                    [    x[3,0]                                ],    #Ψ
                    [   (self._r/self._l) * ( x[1,0] - x[0,0]) ]])   #Ψ_dot
        
        return y


    def RK4_solver(self, tstep):
            
        # Pull out a row from the solution array and transpose to get
        # the state vector as a column
        x = self.xout[[-1]].T
        
        # Pull out the present value of time
        t = self.tout[-1]
        
        # Evaluate the function handle at the present time with the
        # present value of the state vector to compute the derivative
        k1 = self.system_eqn_CL_xd(t               , x                  )
        k2 = self.system_eqn_CL_xd(t + 0.5 * tstep , x + 0.5 * k1 * tstep)
        k3 = self.system_eqn_CL_xd(t + 0.5 * tstep , x + 0.5 * k2 * tstep)
        k4 = self.system_eqn_CL_xd(t +       tstep , x       + k3 * tstep)
        y1 = self.system_eqn_CL_y(x)
        
        # Apply the update rule for Runge-Kutta's method. The derivative value
        # must be transposed back to a row here for the dimensions to line up.
        self.xout.append(self.xout[-1] + (1/6) * (k1 + 2*k2 + 2*k3 + k4 ).T * tstep)
        self.yout.append(y1.T)
        return 



