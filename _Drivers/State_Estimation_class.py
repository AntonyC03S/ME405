import numpy as np
from numpy import array, arange, zeros, transpose, cos, sin, arange
from matplotlib import rc
import matplotlib.pyplot as plt
from math import pi, sin, cos

class State_Estimation:

    def __init__(self,K = 250*2*pi/60/4.5, tau = 0.1, l = 0.141, r = 0.035):
        # Electromechanical properties
        self._K   = K         # Motor Gain [rad/(V*s)]
        self._tau = tau       # Motor Time Constant [s]
        self._r   = r         # Wheel radius [m] 
        self._l   = l         # Track Width (Wheel Center to Wheel Center) [m]

    def system_eqn_CL(self, t, x):
        '''!@brief      Implements both state equations and output equations for
                        the closed loop system
            @param t    The value of time for a given simulation step
            @param x    The value of the state vector for a given simulation step
            @return     A tuple containing both the derivative of the state vector
                        and the output vector for a given simulation step
        '''
        Kp = 3.25
        r_circle = 0.2
        vel_ref = 2
        omega_ref = vel_ref/r_circle
        omega_ref_L = (vel_ref - (omega_ref*self._l/2))/self._r
        omega_ref_R = (vel_ref + (omega_ref*self._l/2))/self._r
        err_L = omega_ref_L - x[4,0]
        err_R = omega_ref_R - x[5,0]

        # Closed-loop inputs
        u = array([ [ Kp * err_L ], 
                    [ Kp * err_R ] ])       
        
        # State equations
        xd =  array( [[ (1/self._tau)     * (self._K*u[0,0] - x[0,0]) ],    #Ω L
                    [   (1/self._tau)     * (self._K*u[1,0] - x[1,0]) ],    #Ω S
                    [   (self._r/2)       * ( x[1,0]        + x[0,0]) ],    #S
                    [   (self._r/self._l) * ( x[1,0]        - x[0,0]) ]])   #Ψ
        
        # Output Equations
        y  =  array( [ [ x[2,0] - (x[3,0] * (self._l/2))       ]     #S_L
                    [    x[2,0] + (x[3,0] * (self._l/2))       ],    #S_R
                    [    x[3,0]                                ],    #Ψ
                    [   (self._r/self._l) * ( x[1,0] - x[0,0]) ]])  #Ψ_dot
        
        return xd, y


    def RK4_solver(fcn, x_0, tspan, tstep):
        '''!@brief        Implements a fourth-order forward Runge-Kutta solver
            @param fcn    A function handle to the function to solve
            @param x_0    The initial value of the state vector
            @param tspan  A span of time over which to solve the system specified
                        as a list with two elements representing initial and
                        final time values
            @param tstep  The step size to use for the integration algorithm
            @return       A tuple containing both an array of time values and an
                        array of output values
        '''
        # Define a column of time values
        tout = arange(tspan[0], tspan[1]+tstep, tstep)

        # Preallocate an array of zeros to store state values
        xout = zeros([len(tout)+1,len(x_0)])
        
        # Determine the dimension of the output vector
        r = len(fcn(0,x_0)[1])
        
        # Preallocate an array of zeros to store output values
        yout = zeros([len(tout),r])

        # Initialize output array with intial state vector
        xout[0][:] = x_0.T

        # Iterate through the algorithm but stop one cycle early because
        # the algorithm predicts one cycle into the future
        for n in range(len(tout)):
            
            # Pull out a row from the solution array and transpose to get
            # the state vector as a column
            x = xout[[n]].T
            
            # Pull out the present value of time
            t = tout[n]
            
            # Evaluate the function handle at the present time with the
            # present value of the state vector to compute the derivative
            k1, y1 = fcn(t               , x                  )
            k2, _  = fcn(t + 0.5 * tstep , x + 0.5 * k1 * tstep)
            k3, _  = fcn(t + 0.5 * tstep , x + 0.5 * k2 * tstep)
            k4, _  = fcn(t +       tstep , x       + k3 * tstep)
            
            # Apply the update rule for Runge-Kutta's method. The derivative value
            # must be transposed back to a row here for the dimensions to line up.
            xout[n+1] = xout[n] + (1/6) * (k1 + 2*k2 + 2*k3 + k4 ).T * tstep
            yout[n] = y1.T
        
        return tout, yout


# The following initial conditions will be used by both the open-loop and
# closed-loop simulations
# x_0 = array([ [0],
#               [0],
#               [0],
#               [0],
#               [0],
#               [0] ])

# # Solve the closed loop system over a 0.1 second time window with 1 us steps
# t_CL, y_CL = RK4_solver(system_eqn_CL, x_0, [0, 1], 5e-3)



# fig, axes = plt.subplots(2, 3, figsize=(12, 6)) 
# fig.suptitle("Closed Loop", fontsize=16)
# axes[0,0].plot(t_CL, y_CL[:,0])
# axes[0,0].set_xlabel('Time (s)')
# axes[0,0].set_ylabel(self._r'X Position ($X_R$) [m]')

# axes[0,1].plot(t_CL, y_CL[:,1])
# axes[0,1].set_xlabel('Time (s)')
# axes[0,1].set_ylabel(self._r'Y Position ($Y_R$) [m]')

# axes[0,2].plot(t_CL, y_CL[:,2])
# axes[0,2].set_xlabel('Time (s)')
# axes[0,2].set_ylabel(self._r'Yaw rate ($\psi_R$) [m]')

# axes[1,0].plot(t_CL, y_CL[:,3])
# axes[1,0].set_xlabel('Time (s)')
# axes[1,0].set_ylabel('Arc-length (s) [m]')

# axes[1,1].plot(t_CL, y_CL[:,4])
# axes[1,1].set_xlabel('Time (s)')
# axes[1,1].set_ylabel('Velocity (v) [m]')

# axes[1,2].plot(t_CL, y_CL[:,5])
# axes[1,2].set_xlabel('Time (s)')
# axes[1,2].set_ylabel(self._r'Angular Velocity ($\omega$) [m]')
# plt.figure(figsize=(8,6))
# plt.plot(y_CL[:,0], y_CL[:,1])
# plt.xlabel(self._r'X Position ($X_R$) [m]')
# plt.ylabel(self._r'Y Position ($Y_R$) [m]')
# plt.axis('equal')
# plt.grid()
# plt.tight_layout()







