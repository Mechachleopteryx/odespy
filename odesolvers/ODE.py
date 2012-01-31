# Author: Liwei Wang, Hans Petter Langtangen

"""
This module contains tools for solving ordinary differential
equations (ODEs). Both scalar ODEs and systems of ODEs are supported.
A wide range of numerical methods for ODEs are offered.

The typical use of the tools goes as follows. Given some ordinary
differential equations written on the generic form u' = f(u, t),
the user carries out three steps.

##############################################################
#                  Part 1    Introduction                    #
##############################################################

All ODE problems in a general form of the initial value problem:
(1)  u'(t) = f(u,t)
  where u can be defined either as a scalar, or as a vector.
  f is a given function which specify the right side of equations.
(2)  U(0) = u0
  where u0 is the initial value to start with.
(3 ) time_points = [t0,t1,t2,...]
  which is the desired time points for the numerical iteration

The module provides an unified interface to solving ODEs. Some classes
in this module implement algorithms in Python, while others are
wrappers of Python wrappers of compiled ODE solvers (from scipy, for
instance).

Including following subclasses:

  1. Euler             : Forward Euler
  2. MidpointIter      : Iterated Midpoint strategy
  3. RK2               : 2nd-order Runge-Kutta
  4. RK3               : 3rd-order Runge-Kutta method
  5. RK4               : 4th-order Runge-Kutta method
  6. Heun              : Heun's method
  7. Leapfrog          : Plain Leapfrog method
  8. LeapfrogFiltered  : Filtered Leapfrog method
  9. AdamsBashforth2   : 2nd-order Adams-Bashforth method
 10. AdamsBashforth3   : 3rd-order Adams-Bashforth method
 11. AdamsBashforth4   : 4th-order Adams-Bashforth method
 12. AdamsBashMoulton2 : 2-step Adams-Bash-Moulton method
 13. AdamsBashMoulton3 : 3-step Adams-Bash-Moulton method
 14. MySolver          : User-defined method
 15. Vode_PyDS         : Wrapper for VODE_ODESystem in package PyDSTool.
 16. Sympy_odefun      : Wrapper for sympy.mpmath.odefun, which uses a
                         high-order Taylor series method.
SolverImplicit:
Implicit ODE solvers within either Newton or Picard nonlinear iteration.
 17. BackwardEuler     : Backward Euler method
 18. ThetaRule         : Theta rule method
 19. Backward2step     : Three-level backward scheme
 20. MidpointImplicit  : Implicit Midpoint method.

Adaptive:
 21. RKFehlberg        : 4-5-th order Runge-Kutta-Fehlberg
 22. AdaptiveResidual  : Accept a specified solver, calculate residual
                         as the error-check criteria.
 23. Rkc               : Wrapper for rkc.f.
 24. Rkf45             : Wrapper for Rkf45.f.

ODEPACK:  Collection for solvers in ODEPACK.
 25. Lsode             : Basic solver dlsode().
 26. Lsodes            : dlsodes() for ODE problems with Jacobian matrix
                         in general sparse form.
 27. Lsoda             : dlsoda(), which automatically selects between
                         nonstiff (Adams) and stiff (BDF) methods.
 28. Lsodar            : dlsodar(), dlsoda with a rootfinding capability
                         added.
 29. Lsodi             : dlsodi(), which solves linearly implicit systems.
 30. Lsoibt            : dlsoibt(), which solves linearly implicit systems
                         in which the matrices involved are assumed to be
                         block-tridiagonal.
 31. Lsodis            : dlsodis(), which solves linearly implicit systems
                         in which the matrices involved are assumed to be
                         sparse.

RungeKutta: Collection for explicit Rungekutta methods.
 32. RungeKutta2       : Standard RungeKutta2
 33. RungeKutta3       : Standard RungeKutta3
 34. RungeKutta4       : Standard RungeKutta4
 35. ForwardEuler      : Forward Euler
 36. DormandPrince     : Dormand & Prince method
 37. Fehlberg          : RungeKutta Fehlberg method
 38. CashKarp          : Case Karp method
 39. BogackiShampine   : Bogacki Shampine method
 40. MyRungeKutta      : Specially for user-defined methods.

Ode_scipy:   Wrapper for scipy.integrate.ode
 41. Vode              : vode.f
 42. Dopri             : Dormand&Prince order 5
 43. Dop853            : Dormand&Prince order 8(5,3).


############################################################
#                    Part 2   Usage                        #
############################################################

Corresponding to the three components for an ODE problem ,
(u' = f(u,t), U(0) = u0, time_points = [...]), we have 3 corresponding key
methods to define the problem in this interface:

1. Solver definition: u' = f(u,t)
  ODE users can call the constructor __init__(f,**keyword-arguments)
  for desired solver class to define equation u' = f(u,t), where f
  is a user-defined Python function. Legal arguments can be attached
  as keyword-arguments in the argument list.
2. Initial value: u(0) = u0
  Users can set up the initial value U(0) = u0 with method
  set_initial_condition(u0).
3. Solve the problem in desired range: time_points = [...]
  Finally users can get the solution with method solve(time_list,...).

Associate Methods for users:

4. switch_to(self, solver_target, printInfo=False,**kwargs):
  Switch to a new subclass with same settings of all useful attributes in
  current solver. This function is intended to switch easily between subclasses
  without restart from initialization in new subclass with same or almost same
  values.
  A new solver instance in the new subclass that is specified by the first
  argument 'solver_target', will be returned. Optional parameters can be reset
  or supplemented in variable-length argument list 'kwargs'.

5. set(self, strict=False, **kwargs)
  Reset or supplement the values of optional parameters.

6. get(self, parameter_name=None, printInfo=False)
  Return value of a specified input parameter.
  If there is no input for 'parameter_name', a dictionary including values of
  all the specified input parameters will be returned.

7. get_parameter_info(self, printInfo=False)   :
  Return a dictionary containing information (name, type, range, etc..) for
  all the legal input parameters in current solver.

8. odesolvers.list_all_solvers() :
 Return string list for all solvers in this module.

9. odesolvers.list_available_solvers() :
 Return string list for available solvers.

#############################################################
#            Part 3  For Future Developers                  #
#############################################################

As an unified interface, common attributes and methods are defined in the
superclass Solver,  and hence hold a unified form and features in the whole
hierarchy. In this way, we can avoid duplicated attributes with different names
(like 'atol','abstol','tol') in different solvers. With unified names in all
subclasses, attributes can be recognized when switched to another solver. .

Class attributes:
1.  t            : array to hold time values
2.  u            : array to hold solution values corresponding to points in t
3.  f            : callable function to implement the right side of
                   equations, i.e. f(u,t) = u'(t).
4.  n            : time step number for current step
5. _optional_parameters : list to hold names of all the optional parameters.
6. _required_parameters : list to hold names of all the mandatory parameters.
7. f_args        : extra arguments for user-defined function f if desired
8. f_kwargs      : extra arguments with keyword for user-defined f if desired
9. complex_valued: flag for complex data type

General routine for future developers to integrate a new solver into this
interface:

1. Dependency preparation.

This step is involved only when developers intend to wrap an existing
package into odesolvers.

If the original package is not written in Python language, developers
need to apply some specific tools (like F2PY or SWIG) to create an
extension module to make the package accessible from our Python
code.

Otherwise, if the original package is also a Python software, developers
 need to install and import the desired package as a Python module.

By an attempt to import these necessary modules (often set in method
initialize()), we can check whether the necessary dependencies are
installed properly.

2. Definition of legal parameters and their properties

Each solver has a set of specific parameters depending on its
underlying method. For example, adaptive solvers will be more
likely to apply attributes for step control, like first_step, min_step,
max_step. And a collection of methods probably need to provide a
parameter for users to make method choice, like ode_method.

Developers should try to search in dictionary _parameters for suitable
 items to represent the desired parameters. If there is no
suitable items found in this dictionary, developer need to supplement
 new items in it.

There is no need to define input parameters one by one. With the help
of variable _optional_parameters and _required_parameters,
all parameters with names in these two name lists would be consid-
ered as legal in new solver.

Furthermore, if a parameter in new solver has some properties
different from general settings in _parameters, developers can reset(or
supplement) these properties in function adjust_parameters().

3. Special check in validate_data()

For some complicated solvers with many relevant input parameters,
there are possibly special relationship requirements inbetween some
specific input parameters.

For example, in class odesolvers.Lsodes, there are special require-
ments for the values of two input integer arrays ia and ja:
 I.   ia and ja must be input simultaneously.
 II.  len(ia) == neq + 1
 III. ia[neq] = len(ja)

Most of the automatic checking are taken in initialization step. We
need to take extra check for the above requirements after all the
inputs are initialized. Thus a new function check_iaja() is defined
in odesolvers.Lsodes, and injected into function validate_data().

4. Internal settings in set_internal_parameters()

When I tried to wrap some complicated ODE software, some param-
eters are found to be dependent on values of other parameters,
although they are required as inputs for these underlying ODE
software.

For example, as an input parameter for rkc.f, info[1] is an integer
 flag to indicate whether function spcrad is supplied by users.
This kind of parameters are required by underlying software, but
unnecessary to be valued from user's input. This is why I called them
as internal parameters.

Function set_internal_parameters() is used to initialize this kind of
parameters before they are passed to the underlying software.

5. Step forward in advance()

In function advance(), solution value for next time point should be
returned. This is the only mandatory step to implement a new solver.

For simple numerical methods (like ForwardEuler method), numerical
 scheme is implemented directly in this function. If the new solver
is a wrapper to another module(either Python module, or extension
module), iteration in underlying package will be ready to start if
Python code pass all the necessary parameters to the underlying
module according to its user interface.

In the user interfaces of some ODE software, like sympy.mpamath.odeint,
solving procedure is started directly with the whole sequence of time
points, but not step by step. Then developers should turn to start
iteration directly in function solve().

##############################################################
#                 Part 4    Examples                         #
##############################################################

>>> # Example 1:  Scalar ODE problem : Exponential
>>> # u'=-u, --> u = exp(-t)
>>> import odesolvers
>>> name = odesolvers.RK4  # example solver
>>> def f(u, t):
...     return -u   # right-hand side of ODE
>>> method = name(f)
>>> method.set_initial_condition(1.)
>>> import numpy as np
>>> time_points = np.linspace(0, 3, 11)
>>> u, t = method.solve(time_points)
>>> u
array([ 1.        ,  0.7408375 ,  0.5488402 ,  0.4066014 ,  0.30122557,
        0.2231592 ,  0.1653247 ,  0.12247874,  0.09073684,  0.06722126,
        0.04980003])
>>> t
array([ 0. ,  0.3,  0.6,  0.9,  1.2,  1.5,  1.8,  2.1,  2.4,  2.7,  3. ])
>>> max_error = max(abs(np.exp(-t) - u))
>>> max_error
3.1742968703674102e-05

>>> # Example 2: ODE systems with 2 equations: Sine
>>> # u'' = -u    -->   u = sin(t)
>>> name = odesolvers.RK4  # example
>>> def f(u, t):
...     return [u[1], -u[0]]
>>> method = name(f)
>>> method.set_initial_condition([0., 1.])
>>> import numpy as np
>>> time_points = np.linspace(0, 2*np.pi, 11)
>>> u, t = method.solve(time_points)
>>> u
array([[ 0.        ,  1.        ],
       [ 0.58697683,  0.80910185],
       [ 0.94984808,  0.31010401],
       [ 0.95054771, -0.30663308],
       [ 0.58910339, -0.80604687],
       [ 0.00351381, -0.99796406],
       [-0.58293875, -0.80951709],
       [-0.9468246 , -0.31281024],
       [-0.9496899 ,  0.30266876],
       [-0.59073631,  0.80233581],
       [-0.00701331,  0.99591992]])
>>> t
array([ 0.        ,  0.62831853,  1.25663706,  1.88495559,  2.51327412,
        3.14159265,  3.76991118,  4.39822972,  5.02654825,  5.65486678,
        6.28318531])
>>> max_err = max(abs(u[:,0] - np.sin(t)))
>>> max_err
0.0070133088801554774

>>> # Example 3: A loop to make a comparison among solvers
>>> # u'' = -u    -->    u = sin(t)
>>> def f(u, t):
...     return [u[1], -u[0]]
>>> time_points = np.linspace(0, 2*np.pi, 11)
>>> exact_u = np.sin(time_points)
>>> from odesolvers import Vode, RKFehlberg, RK4
>>> for solver in [Vode, RKFehlberg, RK4]:
...     method = solver(f)
...     method.set_initial_condition([0.,1.])
...     u,t = method.solve(time_points)
...     max_err = max(u[:,0] - exact_u)
...     print 'Maximum error for %s is %g.' % (solver.__name__, max_error)
Maximum error for Vode is 3.1743e-05.
Maximum error for RKFehlberg is 3.1743e-05.
Maximum error for RK4 is 3.1743e-05.

>>> # Example 4: Extra parameter for function f(u,t,a)
>>> # u' = -a*u   -->   u = exp(-a*t)
>>> name = odesolvers.RK4  # example solver
>>> def f_with_a(u, t, a):    # extra parameter 'a'
...     return -a*u   # right-hand side of ODE
>>> method = name(f_with_a, f_args=(2.,))      # set 'a' as 2.0
>>> method.set_initial_condition(1.)
>>> time_points = np.linspace(0, 3, 11)
>>> u, t = method.solve(time_points)
>>> u
array([ 1.        ,  0.5494    ,  0.30184036,  0.16583109,  0.0911076 ,
        0.05005452,  0.02749995,  0.01510847,  0.0083006 ,  0.00456035,
        0.00250545])

>>> # Example 5: Stop events for logistic population model
>>> # u' = 1.2*u*(1-u) , stop when u exceed 0.9
>>> name = odesolvers.RK4
>>> def termin(u,t,step_no):    # return a boolean value for stop event
...     return u[step_no]>0.9
>>> def f_logistic(u,t):
...     return 1.2*u*(1 - u)
>>> method = name(f_logistic)
>>> method.set_initial_condition(.5)
>>> time_points = np.linspace(0, 2, 201)
>>> u, t = method.solve(time_points,terminate=termin)
RK4 terminated at t=1.84
"""

import pprint, sys, os, inspect
import numpy as np

# Collection of all possible parameters in all solvers in this package
_parameters = dict(

    f = dict(
        help='Right-hand side f(u,t) defining the ODE',
        type=callable),

    f_args = dict(
        help='Extra positional arguments to f: f(u, t, *f_args, **f_kwargs)',
        type=(tuple, list, np.ndarray),
        default=()),

    f_kwargs = dict(
        help='Extra keyword arguments to f: f(u, t, *f_args, **f_kwargs)',
        type=dict,
        default={}),

    complex_valued = dict(
        help='True if f is complex valued',
        default=False,
        type=bool),

    jac = dict(
        help='Jacobian of right-hand side function f (df/du)',
        default=None,
        type=callable),

    jac_args = dict(
        help='Extra positional arguments to jac: jac(u, t, *jac_args,'\
             '**jac_kwargs)',
        type=(tuple,list),
        default=()),

    jac_kwargs = dict(
        help='Extra keyword arguments to jac: jac(u, t, *jac_args,'\
             '**jac_kwargs)',
        type=dict,
        default={}),

    h_in_fd_jac = dict(
        help='h in finite difference approximation of the Jacobian',
        default=1E-4,
        type=float),

    start_method = dict(
        help='Method for the first steps in multi-step solvers',
        default='RK2',
        type=str),

    nonlinear_solver = dict(
        help='Newton or Picard nonlinear solver',
        default='Picard',
        type=str,
        range=('Newton', 'Picard')),

    eps_iter = dict(
        help='Max error measure in nonlinear solver',
        default=1E-4,
        type=float),

    max_iter = dict(
        help='Max no of iterations in nonlinear solver',
        default=25,
        type=int),

    g = dict(
        help='Constraint function of (u, t) in differential-algebraic systems.',
        type=callable),

    ng = dict(
        help='No of components in constraint function g.',
        type=int),

    theta = dict(
        help='Weight in [0,1] used for "theta-rule" finite difference approx.',
        default=0.5,
        type=(int,float),
        range=[0, 1]),

    spcrad = dict(
        help='Function of (u, t) to estimate spectral radius of Jacobian '\
             'matrix in the rkc.f solver.',
        type=callable),

    # Parameters for adaptive methods

    atol = dict(
        help='absolute tolerance for solution',
        type=(float,list,tuple,np.ndarray),
        default=1E-8),

    rtol = dict(
        help='relative tolerance for solution',
        type=(list,tuple,np.ndarray,float),
        default=1E-6),

    min_step = dict(
        help='Minimum step size for an adaptive algorithm',
        type=float),

    max_step = dict(
        help='Maximum step size for an adaptive algorithm',
        type=float),

    first_step = dict(
        help='Suggested first time step size for an adaptive algorithm',
        type=float),

    solver = dict(
        help='Name of solver class in solvers that need an extra solver '\
             '(e.g., AdaptiveResidual)',
        default='RK4',
        type=str),

    butcher_tableau = dict(
        help='2d-array which contains the butcher table for user-supplied '\
             'Runge-Kutta method. (n,n) array for 1-level Runge-Kutta '\
             'methods.(n+1,n) array for 2-level Runge-Kutta methods.',
        type=np.ndarray),

    # vode parameters
    adams_or_bdf = dict(
        help='Method in vode or solvers in odepack: "adams" or "bdf"',
        type=str,
        default='adams',
        range=['adams', 'bdf']),

    nsteps = dict(
        help='Max no of internal solver steps per time step',
        type=int,
        default=1000),

    order = dict(
        help='Maximum order used by the integrator '\
             '(<= 12 for "adams", <= 5 for "bdf")',
        type=int,
        default=4),

    # beta, ifactor and dfactor are intended for adaptive Dormand&Prince
    # methods like dopri5 or dop853 in scipy
    beta = dict(
        help='Beta argument for stabilized step size control in '\
             'Dormand&Prince methods from scipy',
        type=float),

    ifactor = dict(
        help='Maximum factor for increasing the step size',
        type=float,
        default=2),

    dfactor = dict(
        help='Maximum factor for decreasing the step size',
        type=float,
        default=0.5),

    safety = dict(
        help='Safety factor on new step selection',
        default=0.9,
        type=float),

    # Vode_PyDS parameters
    init_step = dict(
        help='Fixed step size for time mesh.',
        type=float),

    strictdt = dict(
        help='Uniform time mesh vs exact dt spacings',
        type=bool,
        default=True),

    stiff = dict(
        help='Boolean flag to indicate stiffness.',
        type=bool),

    use_special = dict(
        help='Switch for using special times',
        type=bool),

    specialtimes = dict(
        help='List of special times to use during iteration',
        type=lambda float_seq: np.asarray(map(lambda x: \
                     isinstance(x, float),float_seq)).all()),

    ode_method = dict(
        help='solver type: "adams" or "bdf"',
        alias='method',   # Different name in scipy.ode.vode
        type=str, default='adams',
        range=('adams','bdf')),

    relaxation = dict(
        help='relaxation argument (r): new_solution = r*solution + '\
             '(1-r)*old_solution',
        default=1.0, type=float),


    # parameters for Jacobian
    jac_banded = dict(
        help='Banded Jacobian (df/du) of right-hand side'\
             'function f. Arguments: u, t, ml, mu. '\
             'Used in Lsode, Lsoda, Lsodar.',
        type=callable),

    jac_column = dict(
        help='A column of the Jacobian (df/du) matrix.'\
             'Arguments: u, t, ia, ja. Used in Lsodes.',
        type=callable),

    jac_constant = dict(
        help='Flag to show whether Jacobian is constant, 0 (false) or 1 (true)',
        default=0,
        type=int),

    # parameters for linearly implicit ODE solvers: Lsodi, Lsoibt, Lsodis
    res = dict(
        help='User-supplied function to calculate the residual vector,'\
             'defined by   r = g(t,y) - A(t,y) * s.'\
             'Used in Lsodi, Lsoibt, Lsodis',
        type=callable),

    ydoti = dict(
        help='Real array for the initial value of dy/dt.',
        type=(list,tuple,np.ndarray),
        extra_check=lambda float_seq: np.asarray(map(lambda x: \
             isinstance(x, float),float_seq)).all(),
        default = []),

    jac_lsodi = dict(
        help='Callable object to define the full Jacobian matrix dr/du'\
             'where r = g - A*s.',
        type=callable),

    jac_banded_lsodi = dict(
        help='Callable object to define the banded Jacobian matrix dr/du'\
             'where r = g - A*s.',
        type=callable),

    adda_lsodi = dict(
        help='Callable object to add the matrix A = A(u,t) to another '\
             'matrix p stored in the same form as A.',
        type=callable),

    adda_banded_lsodi = dict(
        help='Callable object to add the banded matrix A = A(u,t) to another'\
             'matrix P stored in the same form.',
        type=callable),

    jac_lsodis = dict(
        help='Callable object to supply the jth column of the sparse '\
             'Jacobian matrix dr/du where r = g - A*s.',
        type=callable),

    adda_lsodis = dict(
        help='Callable object to add j-th column of matrix A = A(u,t) to '\
             'another matrix stored in sparse from.',
        type=callable),

    jac_lsoibt = dict(
        help='Callable object to supply the jth column of the Jacobian'\
             'matrix dr/du where r= g-A*s, stored in block-tridiagonal form. ',
        type=callable),

    adda_lsoibt = dict(
        help='Callable object to add matrix A = A(u,t) to another matrix P'\
             ',stored in block-tridiagonal form.',
        type=callable),

    # ja, ia, jc & ic are used to describe the sparse structure
    # of matrices in Lsodes and Lsodis
    ja = dict(
        help='Integer array containing the row indices of sparse matrix' \
             'where nonzero elements occur, reading in columnwise order. '\
             'Used in Lsodes and Lsodis.',
        type=(list,tuple,np.ndarray)),

    ia = dict(
        help='Integer Array with length neq+1 which contains starting'\
             'locations in ja of the descriptions of columns 1...neq. '\
             ' Used in Lsodes and Lsodis.',
        type=(list,tuple,np.ndarray)),

    jc = dict(
        help='Integer Array with length neq+1 which contains starting'\
             'locations in jc of the descriptions of columns 1...neq. '\
             ' Used in Lsodis.',
        type=(list,tuple,np.ndarray)),

    ic = dict(
        help='Array which contains starting locations in jc. Used in Lsodis',
        type=(list,tuple,np.ndarray)),

    # ml, mu describe banded Jacobian matrix.
    ml = dict(
        help='Lower half-bandwidth of banded jacobian matrix',
        type=int),

    mu = dict(
        help='Upper half-bandwidth of banded jacobian matrix',
        type=int),

    # mb, nb describe the block-tridiagonal form of matrix.
    # Used in Lsoibt.
    mb = dict(
        help='Block size,  mb>=1, mb*nb = neq (number of equations).',
        type=int,
        extra_check=lambda x: x>=1),

    nb = dict(
        help='Number of blocks in the main diagonal. nb>=4',
        type=int,
        extra_check=lambda x:x>=4),

    # Odepack parameters
    seth = dict(
        help='Element threshhold for sparsity determination.',
        default=0,
        type=int),

    iter_method = dict(
        help='Corrector iteration method choice',
        type=int),

    lrw = dict(
        help='Length of real work array.',
        type=int),

    liw = dict(
        help='Length of integer work array, similiar as <lrw>.',
        type=int),

    method_order = dict(
        help='Method order for user-defined method if known.'\
             'A integer for 1-level methods, or a pair of   '\
             'integer for 2-levels methods.',
        type=(int,tuple,list,np.ndarray)),

    moss = dict(
        help=' Method to obtain sparse structure of Jacobian.',
        type=int),

    max_hnil = dict(
        help='Maximum no of warning messages to be printed.',
        type=int),

    max_ordn = dict(
        help='Maximum order in nonstiff methods. ',
        type=int),

    max_ords = dict(
        help='Maximum order in stiff methods. ',
        type=int),

   # Fortran versions of f, jac, g (can be used when solver is in Fortran)
    f_f77 = dict(
        help='Intended to supply a user-supplied Fortran subroutine as f.',
        type=callable),

    g_f77 = dict(
        help='Intend to supply a Fortran subroutine as g.',
        type=callable),

    jac_f77 = dict(
        help='Intend to supply a Fortran subroutine as jac.',
        type=callable),

    jac_banded_f77 = dict(
        help='Intend to supply a Fortran subroutine as jac_banded.',
        type=callable),

    jac_column_f77 = dict(
        help='Intend to supply a Fortran subroutine as jac_column.',
        type=callable),

    jac_lsodi_f77 = dict(
        help='Intend to supply a Fortran subroutine as jac_lsodi.',
        type=callable),

    jac_banded_lsodi_f77 = dict(
        help='Intend to supply a Fortran subroutine as jac_banded_lsodi.',
        type=callable),

    adda_lsodi_f77 = dict(
        help='Intend to supply a Fortran subroutine as adda_lsodi.',
        type=callable),

    adda_banded_lsodi_f77 = dict(
        help='Intend to supplied a Fortran subroutine as adda_banded_lsodi. ',
        type=callable),

    res_f77 = dict(
        help='Intend to supplied a Fortran subroutine as res. ',
        type=callable),

    spcrad_f77 = dict(
        help='''Intend for user-supplied Fortran subroutine.
        Similar as spcrad, a callable object to estimate the
        spectral radius of the Jacobian matrix. In rkc.f, its
        parameter list should in form of (neq,t,u).
        It is encouraged that users provide a F2PY-compiled
        Fortran subroutine or a multi-line string in Fortran
        code to define this function. This would help to
        improve efficiency.
        This subroutine should be defined in form:
        double precision function spcrad_f77(neq,t,u)
  Cf2py intent(hide)     neq
        integer          neq
        double precision t,u(neq)
        spcrad_f77 =
        return
        end
        ''',
        type=callable),

    myadvance = dict(
        help='User supplied function to advance current solution'\
             ' one step forward. See documents of class MySolver.',
        type=callable),

    )


def format_parameters_table(parameter_names, fixed_width=None):
    """
    Make a table of parameter names and their descriptions.
    The parameter_names list contains the names and the
    descriptions are taken from _parameters[name]['help'].
    max_name_length is the width of the first column, taken
    as the longest name in parameter_names if not specified.

    The table is formatted as a simple reST table with headings
    ("Name" and "Description") and three horizontal lines.
    """
    import textwrap
    max_line_width = 71

    if fixed_width is None:
        max_name_length = max([len(name) \
                               for name in parameter_names + ['Name']])
        c1 = max_name_length + 1     # width of column 1
        c2 = (max_line_width - c1)   # width of column 2
    else:
        c1, c2 = fixed_width

    s = ''  # string to be returned (table)
    hrule = '='*c1 + ' ' + '='*c2 + '\n'
    heading = 'Name' + ' '*(c1-3) + 'Description\n'
    s += hrule + heading + hrule

    for name in parameter_names:
        s += '%%-%ds' % (c1+1) % name
        if name in _parameters:
            text = _parameters[name]['help']
            if 'default' in _parameters[name]:
                text += ' (default: %s)' % str(_parameters[name]['default'])
            if fixed_width is not None:
                line_no = len(text)/c2 if len(text) % c2 == 0 \
                    else len(text)/c2 + 1
                # Spilt text with fixed width
                text = [text[i*49:(i+1)*49] for i in range(line_no)]
            else:
                text = textwrap.wrap(text, c2)    # list of wrapped lines
            for i in range(1, len(text)):   # add initial space for line 2, ...
                text[i] = ' '*(c1+1) + text[i]
            text = '\n'.join(text)
            s += text
        s += '\n'

    s += hrule
    return s

def doc_string_table_of_parameters(classname, fixed_width=None):
    """
    Return a table (in reST format) of the required parameters
    in a class and a table of the optional parameters.
    The returned string is typially appended to the doc string of
    a solver class so that the user can easily see which parameters
    that must and can be provided.
    """
    req_prm = getattr(classname, '_required_parameters')
    opt_prm = getattr(classname, '_optional_parameters')
    for name in opt_prm:
        if not name in _parameters:
            print 'Parameter "%s" used in class %s is not registered in _parameters.' % (name, classname.__name__)
            print 'Do that before proceeding.'
            sys.exit(1)

    s = """
Required input arguments:

""" + format_parameters_table(req_prm, fixed_width=fixed_width) + \
"""
Optional input arguments:

""" + format_parameters_table(opt_prm, fixed_width=fixed_width)
    # Add indent:
    indent = 4
    newlines = [' '*indent + line for line in s.splitlines()]
    s = '\n'.join(newlines)
    return s

class Solver:
    """
    Superclass for numerical methods solving ODE problem

      u'(t) = f(u, t),  u(0) = U0

    where u and U0 are scalars (for scalar ODEs) or vectors
    (for systems of ODEs).

    Attributes stored in this class:

    ====  =============================================================
    Name  Description
    ====  =============================================================
    u     array of point values of the solution function
    t     array of time values: u[i] corresponds to t[i]
    n     the most recently computed solution is u[n+1]
    f     callable object implementing the right-hand side f(u, t)
    ====  =============================================================


    """

    _required_parameters = ['f',]
    _optional_parameters = ['f_args', 'f_kwargs', 'complex_valued']

    def __init__(self, f, **kwargs):
        """
        ``f`` is the right-hand side function of the ODE u' = f(u,t).
        The legal keyword arguments (in ``kwargs``) are documented in
        the tables in the doc string of this class. The ``f`` function
        must return a ``float`` or ``complex`` object in case of a
        scalar ODE and a list or array of ``float`` or ``complex`` objects
        in case of a system of ODEs.

        This constructor makes a dictionary ``self._parameters``
        holding all the required and optional parameters for this solver
        (fetched from the global ``_parameters`` dictionary in this module).
        The method ``adjust_parameters`` (implemented in subclasses)
        is called to adjust default parameter settings if needed.
        Then all keys in ``self._parameters`` become class attributes,
        filled with default values. Thereafter, all keyword arguments
        (in ``kwargs``) with ``None`` as value are removed as keyword
        arguments. The next step is to call ``set(**kwargs)``, i.e.,
        use the keyword arguments to modify the values of the attributes
        that represent the parameters in this solver. Finally, the
        constructor calls the method ``initialize`` (to be implemeneted
        in subclasses, e.g., for importing necessary modules for the solver).

        Instead of supplying keyword arguments to this constructor, the
        user can at any time call the ``set`` method with keyword
        arguments in order to specify parameters.
        """

        # self._parameters is the union of optional and required parameters
        # for the class. self._parameters contains all the
        # legal parameters the user of the class can set.
        self._parameters = dict(
            (key, value.copy()) for key, value in _parameters.items()
            if key in self._optional_parameters or \
               key in self._required_parameters
            )

        # Compile user-supplied functions if they are supplied
        # as multi-line strings in Fortran code
        f, kwargs = self.compile_string_functions(f, **kwargs)

        # Adjust self._parameters
        self.adjust_parameters()

        # Set default values for all parameters, remove all parameters
        # with value None, and then apply set() to all the user-provided
        # parameters in kwargs

        for name in self._parameters:
            if 'default' in self._parameters[name]:
                setattr(self, name, self._parameters[name]['default'])

        nones = [name for name in kwargs.keys() if kwargs[name] is None]
        for name in nones:
            del kwargs[name]

        self.set(**kwargs)

        # Wrap user-supplied f with extra arguments
        if f is not None:
            self.users_f = f  # stored in case it is handy to have
            if not callable(f):
                raise TypeError('f is %s, not a callable function' % type(f))
            # For ODE systems, f will often return a list, but
            # arithmetic operations with f in numerical methods
            # require that f is an array. Let self.f be a function
            # that first calls f(u,t) and then ensures that the
            # result is an array (without imposing any type - if
            # U0 has integers it is detected and converted to floats
            # to ensure float results from f).
            if 'f_args' in self._optional_parameters:
                self.f = lambda u, t:  \
                    np.asarray(f(u, t, *self.f_args, **self.f_kwargs))
            else:
                self.f = lambda u, t: np.asarray(f(u,t))

        # Subclass-specific initialization
        self.initialize()


    def compile_string_functions(self, f, **kwargs):
        """
        Compile functions which are supplied as Fortran strings.
        """
        str_funcs = dict(
            (func,kwargs[func]) for func in kwargs
            if isinstance(kwargs[func], str) and \
               (func in _parameters) and \
               (_parameters[func]['type'] is callable))
        if isinstance(f, str):
            str_funcs['f'] = f

        try:
            os.remove('_callback.so')
        except:
            pass

        string_to_compile = '\n'.join(str_funcs.values())
        if string_to_compile is not '':
            try:
                # Compile these functions together into module callback
                from numpy import f2py
                f2py.compile(string_to_compile, modulename='_callback', \
                             verbose=False)
                import _callback
                for func in str_funcs.keys():
                    if func == 'f':
                        f = _callback.f
                    else:
                        kwargs[func] = getattr(_callback,func)
            except:
                raise ValueError, '''
           F2py failed to compile input string (=\n%s)
           to be callable functions (%s).''' \
                 % (string_to_compile, str_funcs.keys())
        return f, kwargs

    def adjust_parameters(self):
        '''
        This method allows subclasses to adjust (modify or add)
        entries in the self._parameters dictionary.
        The method is called from the constructor.

        Further adjustments of self._parameters can be done in
        set_internal_parameters when all data for the solver are available.
        '''
        # Define start_method and method here since the range depends
        # on return value of list_all_solvers().
        _parameters['start_method']['range'] = \
            _parameters['solver']['range'] = list_all_solvers()
        return None


    def initialize(self):
        """
        Subclass-specific initialization. Called from constructor.
        Typical use: import modules needed in methods in the class
        and provide error messages if modules are not installed.
        """
        return None


    def set(self, strict=False, **kwargs):
        """
        Assign values to one or more parameters, specified as keyword
        arguments.

        The legal parameters that can be set are contained in the dict
        self._parameters.

        If strict is true, only registered parameter names are accepted,
        otherwise unregistered parameters are ignored.

        The provided parameters (keyword arguments in kwargs) are
        first checked for legal type and legal range.

        Types and ranges of attributes are defined in self._parameters,
        which is initialized with default settings and optionally
        modified in the adjust_parameters method.
        """

        # if new string functions are supplemented
        f_dummy, kwargs = self.compile_string_functions(None, **kwargs)

        # Check for invalid names in kwargs
        kwargs_copy = kwargs.copy()
        for name in kwargs_copy:
            if name not in self._parameters:
                # invalid name
                if strict:
                    raise ValueError('set: parameter %s=%s has illegal name' % \
                                     (name, kwargs[name]))
                del kwargs[name]
            elif kwargs[name] is None:
                del kwargs[name]
                if hasattr(self, name):    # Remove this attribute
                    del self.__dict__[name]

        self.check_input_types(**kwargs)  # all values of right type?
        self.check_input_range(**kwargs)  # all values of right range?

        # Run extra check functions if specified
        self.check_extra(**kwargs)

        # Tests on right name/type/range were successful (if we come here)
        for name in kwargs:
            setattr(self, name, kwargs[name])

        # all conditional parameters are supplied?
        self.check_conditional_parameters()

    def check_input_types(self, **kwargs):
        """Check whether all existing inputs are of right specified type."""

        parameters = self._parameters
        arg_type_list = [(name,parameters[name]['type'],kwargs[name]) \
                           for name in parameters \
                           if name in kwargs and \
                              'type' in parameters[name]]
        # name in parameters -->  valid inputs in current class
        # name in kwargs       -->  existing inputs in current instance
        # 'type' in parameters[name]   --> type is specified to be checked

        for name, types, value in arg_type_list:
            #(Ex: types = (callable,int)
            if not isinstance(types, (list, tuple)):
                types = [types]  # make a type list
            checked_type = False
            for tp in types:
                if tp == callable and callable(value):
                    # value should be a callable object
                    checked_type = True
                else:
                    if isinstance(value, tp):
                        checked_type = True
            if not checked_type:
                raise TypeError('set: %s is %s, not %s' % \
                                (name, type(value), types))
        return True


    def check_input_range(self,**kwargs):
        """Check whether all existing inputs are in right specified range."""

        parameters = self._parameters
        arg_type_list = [(name,parameters[name]['range'],kwargs[name]) \
                           for name in parameters \
                           if name in kwargs and \
                              'range' in parameters[name]]
        # name in parameters -->  valid inputs in current class
        # name in kwargs       -->  existing inputs in current instance
        # 'range' in parameters[name]   --> range is specified to be checked

        for name, ranges, value in arg_type_list:
            if isinstance(value, (float, int, complex)):
               # value is a comargble number
                if len(ranges) == 2:  # ranges is an interval
                    low, high = ranges
                    if not ((low <= value <= high) or (low >= value >= high)):
                        raise ValueError('%s=%s is illegal - range=[%s, %s]' % \
                                         (name, value, low, high))
                else:    # range is a list of valid values
                    if not value in ranges:
                        raise ValueError('%s=%s is illegal - range=%s' % \
                                         (name, value, str(ranges)))
        return True

    def check_extra(self,**kwargs):
        """
        Run extra check functions if property 'extra_check' is specified
        for some parameters.
        """
        p = self._parameters
        prm_type_list = [(name, p[name]['extra_check'], kwargs[name]) \
                         for name in p \
                         if name in kwargs and \
                         'extra_check' in p[name]]
        # name in parameters -->  valid inputs in current class
        # name in kwargs       -->  existing inputs in current instance
        # 'extra_check' in parameters[name]
        #           --> extra functions is specified to check the value

        for name, check_funcs, value in prm_type_list:
            try:
                if not check_funcs(value):  # Return false
                    raise ValueError,'''
        Improper value (=%s) for parameter %s.
        Please check your input.''' % (str(value), name)
            except:     # cannot run check_function smoothly
                raise ValueError,'''
        Cannot run check function for %s=%s.
        Please check your input.''' % (name, str(value))
        return True

    def get(self, parameter_name=None, printInfo=False):
        """
        Return value of specified input parameters.
        If parameter_name is None, return dict of all inputs.
        """
        if parameter_name is None:
            # Python v2.7 dict comprehension
            # {name: getattr(self, name) for name in self._parameters}
            all_args = dict([(name, getattr(self, name, None)) \
                                 for name in self._parameters \
                                 if hasattr(self, name)])
            if printInfo:
                print pprint.pformat(all_args)
            return all_args
        else:
            if hasattr(self, parameter_name):
                value = getattr(self, parameter_name)
                if printInfo:
                    print "%s = %s" % (parameter_name, value)
                return value
            else:
                raise AttributeError('Parameter %s is not set' % parameter_name)

    def get_parameter_info(self,printInfo=False):
        '''
        Return a dictionary containing properties of legal parameters in
        current subclass, e.g. self._parameters.
        '''
        if printInfo:
            print 'Legal parameters for class %s are:' % self.__class__.__name__
            print pprint.pformat(self._parameters)
            return None
        else:
            return self._parameters

    def _print_method(self, with_f, default):
        """
        Return "classname(f=func, param1=..., param2=..., )".
        Skip f= if *with_f* is *False*.
        If *default* is False, skip param1= if the value equals
        the default value.
        (Helper method used by __str__ and __repr__.)
        """
        s = self.__class__.__name__
        args = []
        if with_f and hasattr(self, 'users_f'):
            if not hasattr(self.users_f, '__name__'):     # class instance?
                f_name = self.users_f.__class__.__name__
	    else:    # Ordinary functions
                f_name = self.users_f.__name__
	        if f_name == '<lambda>':   # lambda function
	  	    f_name = 'lambda u, t: ...'
            args.append('f=%s' % f_name)

        # form all parameters
        for name in self._parameters:
            if name != 'f' and hasattr(self, name):
                value = getattr(self, name)
                value_specified = True \
                    if 'default' not in self._parameters[name] \
                    else value != self._parameters[name]['default']
                if default or value_specified:
                    types = self._parameters[name]['type']
                    if types in (callable, (str, callable)):
                        value = getattr(value, '__name__', \
                                            value.__class__.__name__)
                    args.append('%s=%s' % (name, value))

        args = ', '.join(args)
        s += '(%s)' % args
        return s

    def __repr__(self):
        """Return solvername(f=..., param1=..., etc.)."""
        return self._print_method(with_f=True, default=True)

    def __str__(self):
        """
        Return solvername, plus parameters that are different from
        the default value.
        """
        return self._print_method(with_f=False, default=False)


    def set_initial_condition(self, U0):
        """
        Function set_initial_condition() is used to set initial value of
        independent variables.
        """
        # Test first if U0 is sequence (len(U0) possible),
        # and use that as indicator for system of ODEs.
        # The below code should work for U0 having
        # float,int,sympy.mpmath.mpi and other objects as elements.
        try:
            self.neq = len(U0)
            U0 = np.asarray(U0)          # (assume U0 is sequence)
        except TypeError:
            # U0 has no __len__ method, assume as a scalar
            self.neq = 1
            if isinstance(U0, int):
                U0 = float(U0)           # avoid integer division
        self.U0 = U0

    def solve(self, time_points, terminate=None):
        """
        Compute discrete solution u of the ODE problem at time points
        specified in the array time_points. An optional user-supplied
        function ``terminate(u, t, step_no)`` can be supplied to
        terminate the solution process (``terminate`` returns True
        or False) at some time earlier than ``time_points[-1]``.

        Most classes in this solver hierarchy inherit this ``solve``
        method and implement their special ``advance`` method to
        advance the solution one step.
        Some solver classes will implement their own ``solve``
        method, for instance if they wrap some underlying software
        that has a suitable ``solve`` functionality.

        The algorithm steps in this ``solve`` method goes as follows.
        The set_internal_parameters method is called to initialize
        various data needed in the solution process (self. u, for instance).
        Thereafter, ``validate_data`` is called to perform a consistency
        check on data. We are then ready for the core of the method:
        the time loop.

        Output:
           u            : array to hold solution values corresponding to points
           t            : array to hold time values.Usually same as time_points
        """
        if terminate is None:    # Default function
            terminate = lambda u, t, step_no: False

        self.t = np.asarray(time_points)
        self.set_internal_parameters()
        self.validate_data()

        # The time loop
        N = self.t.size - 1  # no of intervals
        for n in range(N):
            self.n = n
            self.u[n+1] = self.advance()   # new value
            if terminate(self.u, self.t, n+1):
                print self.__class__.__name__, \
                      'terminated at t=%g' % self.t[n+1]
                self.u, self.t = self.u[:n+2], self.t[:n+2]
                break  # terminate time loop over n
        return self.u, self.t


    def advance(self):
        """Advance solution one time step."""
        raise NotImplementedError


    def set_internal_parameters(self):
        """
        Setting values of internal attributes to be used in iteration.

        These internal attributes are ususally dependent on the values of
        other attributes. For example, for Rkc, self.itol should be
        initialized here as a flag to indicate whether self.atol is
        supplied as scalar or sequence.

        In subclasses, this function can be extended when required.
        """

        # Detect whether data type is in complex type or not.
        if hasattr(self, 'f'):
            value = np.array(self.f(self.U0, self.t[0]))
        else:
            value = np.asarray(self.U0)
        if value.dtype in (np.int32, np.int64, np.int):
            self.dtype = np.complex if self.complex_valued else np.float
        else:
            self.dtype = value.dtype
        self.complex_valued = (str(self.dtype)[:7] == 'complex')

        # Initialization of self.u
        N = self.t.size - 1  # no of intervals
        if self.neq == 1:  # scalar ODEs
            self.u = np.zeros(N+1, self.dtype)
        else:              # systems of ODEs
            self.u = np.zeros((N+1, self.neq), self.dtype)
        # Assume that self.t[0] corresponds to self.U0
        self.u[0] = self.U0

        return None


    def constant_time_step(self):
        """Check if self.t has a uniform partition."""
        return np.allclose(self.t,
                           np.linspace(self.t[0], self.t[-1], len(self.t)))


    def validate_data(self):
        """
        This function is used for extra check after all the attributes,
        (including inputs and internal parameters), have been
        initialized, e.g. control the specific relations among values of
        relative attributes.

        In subclasses, this function can be extended when required.
        For example, when banded Jacobian matrix is supplied in Lsode,
        lower/higher band ('ml' & 'mu') have to be provided by user.
        """
        # self.t should be a sequence of numbers
        if (not isinstance(self.t, (list, tuple, np.ndarray))) \
            or (not np.asarray(
            # all items in self.t should be numbers
            [isinstance(t, (int,float)) for t in self.t]).all()):
                raise TypeError, \
                    'solve: time_points(=%s) is not a proper '\
                    'sequence of real numbers' % str(self.t)

        # self.t should be supplied in an asscending/descending order
        t_sorted = sorted(self.t, reverse=self.t[0] > self.t[-1])
        if list(self.t) != list(t_sorted):
            raise ValueError, \
                'time_points(=%s) is not provided in an ascending/descending'\
                ' order!' % str(self.t)

        # Test whether all required parameters are provided
        for arg in self._required_parameters:
            if not hasattr(self, arg):
                raise ValueError,\
                    '"%s" has to be input as required parameter(s) for '\
                    'solver %s.' % (arg,self.__class__.__name__)
        return True

    def switch_to(self, solver_target, printInfo=False, **kwargs):
        """
        Create a new solver instance which switch to another subclass with
        same values of common attributes.

        Input:
            solver_target:   Either as a string(for class name) or
                             as a class, e.g. RK4 or 'RK4'
            kwargs       :   Optional inputs to reset/supplement values of
                             valid input argmenters in new solver.
        Output:
            A new instance in target solver class.

        Example:
        >>> import odesolvers
        >>> f = lambda u,t: -u
        >>> time_points = np.linspace(0.,2.,11)
        >>> exact_u = np.exp(-time_points)
        >>> m1 = odesolvers.RK2(f)
        >>> m1.set_initial_condition(1.)
        >>> u1, t = m1.solve(time_points)
        >>> print 'Normarized error with RK2 is %g' % np.linalg.norm(u1 - exact_u)
        Normarized error with RK2 is 0.0077317
        >>> m2 = m1.switch_to(odesolvers.RKFehlberg, rtol=1e-18)
        >>> u2, t = m2.solve(time_points)
        >>> print 'Normarized error with RKFehlberg is %g' % np.linalg.norm(u2 - exact_u)
        Normarized error with RKFehlberg is 8.55517e-08

        """
        # Extract name list of all the subclasses in this module
        solver_list = list_all_solvers()
        error_message = '''
        Input error! Your input %s is not a valid solver name!
        Valid names are %s ''' % (str(solver_target), str(solver_list))

        # Check whether input solver_target is a valid subclass of Solver
        try:
            if type(solver_target) is str:
                # Convert string to class name
                solver_target = eval(solver_target)
            if not issubclass(solver_target, Solver):
                raise ValueError, error_message
        except:
            raise ValueError, error_message

        # Neglect the attributes if they are illegal in target solver
        args_dict = {}
        # Extract all the existing attributes which are legal both in
        # current solver and the target solver
        common_attr = set(solver_target._optional_parameters) & \
                      set(self._optional_parameters)
        # Extract values of these common attributes
        args_dict = dict((name, getattr(self, name)) for name in common_attr \
                             if hasattr(self, name))

        # Exception: 'f' is to provided as 1st parameter to initialize
        # new instance in target solver
        if 'f' in kwargs:    # f is reset as a new parameter
            f = kwargs.pop('f')
        else:
            f = getattr(self, 'f', None)  # the wrapped general form f(u,t)
        for name in ('f_f77', 'f_args', 'f_kwargs', 'f'):
            if name in args_dict:
                del args_dict[name]

        # Union with new values in kwargs
        # Note: Old values for parameters in current solver are neglected
        #       if they are provided in kwargs.
        args_dict.update(kwargs)

        # Create new instance through normal constructor __init__().
        # It ensures all the necessary checking/setting in target solver.
        new = solver_target(f, **args_dict)

        # Set up initial value U0 if available
        if hasattr(self,'U0'):
            new.set_initial_condition(self.U0)

        # Print out information if desired
        if printInfo:
            # neglected attributes in new solver
            diff_args = set(self.__dict__.keys()) - set(new.__dict__.keys()) \
                - set(('u','t','n','dtype'))
            if diff_args:
                print 'These attributes are neglected in %s: %s\n' \
                    % (solver_target.__name__, str(diff_args)[5:-2])
            print 'Switched to solver %s' % str(solver_target.__name__)

        return new

    def check_conditional_parameters(self):
        """
        This function is used to check whether conditional parameters are
        provided when specified condition fulfilled.

        This function is not intended for simple solvers.
        So it is not called automatically in current ODE.py.
        But for some complicated solvers as ones in ODEPACK, they
        are very useful and convenient.

        Future developers can apply these functions at appropriate
        locations with corresponding property-setting in
        adjust_parameters().

        For example, in Lsode_ODEPACK, when iter_method is set to 4, it
        indicates that ODEPACK would apply user-supplied banded Jacoabian
        function in corrector iteration. Then we need to confirm either
        'jac_banded' or 'jac_fortran' is supplied. Besides, 'ml' & 'mu' are
        also necessary for iteration with banded Jacobian matrix.
        Thus in order to confirm sufficient conditional inputs, we set
        parameters['iter_method']['condition_list'] =
             {...,'4': (('jac_banded','jac_fortran'),ml,mu),...}

        In this function, we would check all the legal parameters with specified
        condition-list, and make sure all the conditional parameters with
        current value is supplied.

        """
        parameters = self._parameters
        # Parameters with condition-list settings
        with_condition_args = \
            [(name, parameters[name]['condition-list'], \
              str(getattr(self,name))) \
                 for name in parameters \
                    if name in self.__dict__ and
                       'condition-list' in parameters[name]]

        # name in parameters   -->  valid inputs for current class
        # name in self.__dict__ -->  existing inputs for curremt instance
        # 'condition-list' in parameters[name] -->
        #                       'condition-list' is specified to check

        for (name, conditions, value) in with_condition_args:
            # Ex: name = 'iter_method'
            #     conditions = {'1':(('jac','jac_f77'),), '4':.., '5':..})
            #     value = '1'
            if value in conditions:
                # There is conditional requirements for current value
                condition_args = conditions[value]
                # list/tuple for conditional parameters
                for arg in condition_args:
                    if not isinstance(arg, str):
                        # arg is a list for alternative parameters
                        # e.g. ('jac', 'jac_f77')
                        # Either 'jac' or 'jac_f77' should be supplied
                        found = bool([p_name for p_name in arg \
                                          if hasattr(self,p_name)])
                        arg_print = 'One of %s' % str(arg)
                    else:      # arg is a single parameter
                        found = hasattr(self, arg)
                        arg_print = arg
                    if not found:
                        raise ValueError,'''\
        Error! Unsufficient input!
        %s must be set when %s is %s!''' % (arg_print,name,value)
        return True


    def func_wrapper(self):
        '''
        This function is defined to wrap user-defined functions with new
        forms of parameter-list, or wrap the returned values as numpy arrays.

        Firstly, in odesolvers, all the user-supplied functions should have a
        parameter list starts with "u,t,...". But in some special subclasses,
        (like solvers in ODEPACK), all the parameter lists of user-defined
        functions start with "t,u,...". So we need this general function to
        wrap all these user-defined functions.

        Secondly, in some user-defined functions, according to the different
        start indices in Fortran and Python, we need to make special wrapping
        for these uncompability. For an example, in user-defined function
        "jac_column", column index is an internally valued parameter in
        Fortran code. In Python, it starts from 0 instead of 1 in Fortran.
        So we need to wrap the parameter list of user-defined "jac_column" from
        "u,t,j" to "t,u,j+1". That is, define the jacobian function as
        lambda t,u,j: jac_column(u,t,j-1).

        Furthermore, the return value of user-defined functions need to be
        wrapped to Numpy arrays with great numerical features, e.g.
        vectorization and array slicing. In order to avoid unnecessary array
        copy by F2PY, it is always recommended to explicitly transform all
        Numpy arrays to Fortran order in Python code.

        This functions is not intended for simple solvers. So it is not called
        automatically in current version. But for some complicated solvers as
        ones in ODEPACK, it is very useful and convenient.

        Future developers can call this functions with appropriate locations
        and corresponding property-setting in adjust_parameters().

        '''
        import numpy as np
        parameters = self._parameters
        # Extract function parameters that are required to be wrapped
        func_list = [[name,
                      parameters[name].get('returnArrayOrder', None),
                      parameters[name].get('paralist_old', None),
                      parameters[name].get('paralist_new', None),
                      parameters[name].get('name_wrapped', name)]
                     for name in parameters \
                         if name in self.__dict__ and \
                         'type' in parameters[name] and \
                         (parameters[name]['type'] is callable or \
                          parameters[name]['type'] is (callable, str)) and \
                         ('paralist_new' in parameters[name] or \
                          'returnArrayOrder' in parameters[name])]
        # name in self.__dict__  --> existing attributes in current instance
        # parameters[name]['type'] is callable or (callable, str)
        #             -->     callable objects
        # 'paralist_new' in parameters[name]
        #    --> new parameter-list is defined to be wrapped
        # 'returnArrayOrder' in parameters[name]
        #    --> this function return an array, and should be wrapped either in
        #    Fortran order or C (default) order.
        func_input = {}
        for name, order, arg_old, arg_new, name_new in func_list:
            # e.g. name     = 'jac'
            #      arg_old  = 'u,t'
            #      arg_new  = 't,u'
            #      order    = 'Fortran'
            #      name_new = 'jac_f77'
            #  Then:
            #  self.jac_f77 = lambda t,u: np.asarray(jac(u,t), order='Fortran')
            func_input[name] = getattr(self, name)
            wrap_string = 'lambda %s: ' % \
                (arg_new if arg_new is not None else arg_old)
            wrap_string += 'np.asarray(' if order is not None else ''
            wrap_string += 'func_input["%s"](%s)' % (name, arg_old)
            wrap_string += ', order="Fortran"' if order=='Fortran' else ''
            wrap_string += ')' if order is not None else ''
            setattr(self, name_new, eval(wrap_string, locals()))


class MySolver(Solver):
    """
    Users can define a solver with supplying a function
    myadvance(), and make use of all possible parameters
    in this module.

    myadvance(MySolver_instance)  -->  return unew

    Example:
    def myadvance_(ms):
        f, u, t, n, atol = ms.f, ms.u, ms.t, ms.n, ms.atol
        # All class attributes can be obtained
        unew = ...
        return unew

    def f(u,t):
        udot = ...
        return udot

    method = MySolver(f, myadvance=myadvance_)
    method.set_initial_condition(u0)
    u,t = method.solve(time_points)
    """
    _required_parameters = ['f', 'myadvance']
    _optional_parameters = _parameters.keys()
    # All arguments are valid and accessible for users.

    def advance(self):
        return self.myadvance(self)

### End of class Solver ###

class Euler(Solver):
    """
    Forward Euler scheme::

        u[n+1] = u[n] + dt*f(u[n], t[n])
    """
    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t
        dt = t[n+1] - t[n]
        unew = u[n] + dt*f(u[n], t[n])
        return unew



class Leapfrog(Solver):
    """
    Leapfrog scheme::

        u[n+1] = u[n-1] + dt2*f(u[n], t[n])

    with::
        dt2 = t[n+1] - t[n-1]

    Forward Euler is used for the first step.
    """

    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t

        if n >= 1:
            dt2 = t[n+1] - t[n-1]
            unew = u[n-1] + dt2*f(u[n], t[n])
        else:
            dt = t[n+1] - t[n]
            unew = u[n] + dt*f(u[n], t[n])
        return unew



class LeapfrogFiltered(Solver):
    """
    The standard Leapfrog scheme reads::

        u[n+1] = u[k-1] + dt2*f(u[n], t[n])

    with::

        dt2 = t[n+1] - t[k-1]

    Forward Euler is used for the first step.
    Since Leapfrog gives oscillatory solutions, this class
    applies a common filtering technique::

        u[n] = u[n] + gamma*(u[n-1] - 2*u[n] + u[n+1])

    with gamma=0.6 as in the NCAR Climate Model.
    """

    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t
        gamma = 0.6  # NCAR Climate Model

        if n >= 1:
            dt2 = t[n+1] - t[n-1]
            unew = u[n-1] + dt2*f(u[n], t[n])
            u[n] = u[n] + gamma*(u[n-1] - 2*u[n] + unew)
        else:
            dt = t[n+1] - t[n]
            unew = u[n] + dt*f(u[n], t[n])
        return unew



class Heun(Solver):
    """
    Heun's method, also known as an RungeKutta2 or Trapezoidal method.
    Basically, it is a central difference method, with one
    iteration and the Forward Euler scheme as start value.
    In this sense, it is a predictor-corrector method.

    Scheme::

        u[n+1] = u[n] + 0.5*dt*(f(u[n],t[n]) + f(u[n]+dt*f(u[n],t[n]),t[n+1]))
    """

    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t
        dt = t[n+1] - t[n]
        u_star = u[n] + dt*f(u[n], t[n])  # Forward Euler step
        unew = u[n] + 0.5*dt*(f(u[n], t[n]) + f(u_star, t[n+1]))
        return unew



Trapezoidal = Heun   # alias for solver Heun


class RK2(Solver):
    """
    Standard Runge-Kutta 2nd method::

        u[n+1] = u[n] + dt*f(u[n] + 0.5*(dt*f(u[n],t[n])),t[n] + 0.5*dt)
    """

    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t
        dt = t[n+1] - t[n]
        K1 = dt*f(u[n], t[n])
        K2 = dt*f(u[n] + 0.5*K1, t[n] + 0.5*dt)
	unew = u[n] + K2
        return unew



class RK4(Solver):
    """
    Standard RK4 method::

        u[n+1] = u[n] + (1/6.0)*(K1 + 2*K2 + 2*K3 + K4)

    where::

           K1 = dt*f(u[n], t[n])
           K2 = dt*f(u[n] + 0.5*K1, t[n] + 0.5*dt)
           K3 = dt*f(u[n] + 0.5*K2, t[n] + 0.5*dt)
           K4 = dt*f(u[n] + K3, t[n] + dt)
    """

    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t
        dt = t[n+1] - t[n]
        dt2 = dt/2.0
        K1 = dt*f(u[n], t[n])
        K2 = dt*f(u[n] + 0.5*K1, t[n] + dt2)
        K3 = dt*f(u[n] + 0.5*K2, t[n] + dt2)
        K4 = dt*f(u[n] + K3, t[n] + dt)
        unew = u[n] + (1/6.0)*(K1 + 2*K2 + 2*K3 + K4)
        return unew



class RK3(Solver):
    """
    RungeKutta3 method::

        u[n+1] = u[n] + (1/6.0)*(K1 + 4*K2 + K3)

    where::

        K1 = dt*f(u[n], t[n])
        K2 = dt*f(u[n] + 0.5*K1, t[n] + 0.5*dt)
        K3 = dt*f(u[n] - K1 + 2*K2, t[n] + dt)
    """

    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t
        dt = t[n+1] - t[n]
        dt2 = dt/2.0
        K1 = dt*f(u[n], t[n])
        K2 = dt*f(u[n] + 0.5*K1, t[n] + dt2)
        K3 = dt*f(u[n] - K1 + 2*K2, t[n] + dt)
        unew = u[n] + (1/6.0)*(K1 + 4*K2 + K3)
        return unew


class AdamsBashforth2(Solver):
    """
    Second-order Adams-Bashforth method::

        u[n+1] = u[n] + dt/2.*(3*f(u[n], t[n]) - f(u[n-1], t[n-1]))

    for constant time step dt.

    RK2 is used as default solver in first step.
    """

    _optional_parameters = Solver._optional_parameters + ['start_method',]

    def set_internal_parameters(self):
        # New solver instance for first steps
        self.starter = self.switch_to(self.start_method)
        # Create variables for f at previous time levels
        self.f_n_1 = None
        Solver.set_internal_parameters(self)

    def validate_data(self):
        if not self.constant_time_step():
            print '%s must have constant time step' % self.__name__
            return False
        else:
            return True

    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t

        if n >= 1:
            dt = t[n+1] - t[n]  # must be constant
            self.f_n = f(u[n], t[n])
            unew = u[n] + dt/2.*(3*self.f_n - self.f_n_1)
            self.f_n_1 = self.f_n

        else:
            # Start method
            self.starter.set_initial_condition(u[n])
            time_points = [t[n], t[n+1]]
            u_starter, t_starter = self.starter.solve(time_points)
            unew = u_starter[-1]
            self.f_n_1 = f(u[0], t[0])
        return unew


class AdamsBashforth3(Solver):
    """
    Third-order Adams-Bashforth method::

        u[n+1] = u[n] + dt/12.*(23*f(u[n], t[n]) - 16*f(u[n-1], t[n-1]) \
                                + 5*f(u[n-2], t[n-2]))

    for constant time step dt.

    RK2 is used as default solver for first steps.
    """
    _optional_parameters = Solver._optional_parameters + ['start_method',]

    def set_internal_parameters(self):
        # New solver instance for first steps
        self.starter = self.switch_to(self.start_method)
        # Create variables for f at previous time levels
        self.f_n_1 = None
        self.f_n_2 = None
        Solver.set_internal_parameters(self)

    def validate_data(self):
        if not self.constant_time_step():
            print '%s must have constant time step' % self.__name__
            return False
        else:
            return True

    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t

        if n >= 2:
            dt = t[n+1] - t[n]  # must be constant
            self.f_n = f(u[n], t[n])
            unew = u[n] + dt/12.*(23*self.f_n - 16*self.f_n_1 + 5*self.f_n_2)
            self.f_n_1, self.f_n_2, self.f_n = self.f_n, self.f_n_1, self.f_n_2

        else:
            # Start method
            self.starter.set_initial_condition(u[n])
            time_points = [t[n], t[n+1]]
            u_starter, t_starter = self.starter.solve(time_points)
            unew = u_starter[-1]
            if n == 0:
                self.f_n_2 = f(u[0], t[0])
            elif n == 1:
                self.f_n_1 = f(u[1], t[1])
        return unew


class AdamsBashMoulton2(Solver):
    """
    Two-step (3rd-order) Adams-Bashforth method::

        predictor = u[n] + dt/12.*(23.*f(u[n], t[n]) - 16*f(u[n-1], t[n-1]) +
                            5*f(u[n-2], t[n-2]))
        corrector = u[n] + dt/12.*(8.*f(u[n], t[n]) - f(u[n-1], t[n-1]) +
                            5*f(predictor, t[n+1]))

    for constant time step dt.

    RK2 is used as default solver for first steps.
    """
    _optional_parameters = Solver._optional_parameters + ['start_method',]

    def set_internal_parameters(self):
        # New solver instance for first steps
        self.starter = self.switch_to(self.start_method)
        # Create variables for f at previous time levels
        self.f_n_1, self.f_n_2 = None, None
        Solver.set_internal_parameters(self)

    def validate_data(self):
        if not self.constant_time_step():
            print '%s must have constant time step' % self.__name__
            return False
        else:
            return True

    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t

        if n >= 2:
            dt = t[n+1] - t[n]  # must be constant
            self.f_n = f(u[n], t[n])
            predictor = u[n] + dt/12.*(23.*self.f_n - 16*self.f_n_1 + \
                                  5*self.f_n_2)
            unew = u[n] + dt/12.*(8*self.f_n - self.f_n_1 + \
                                  5*f(predictor, t[n + 1]))
            self.f_n_1, self.f_n_2 = self.f_n, self.f_n_1
        else:
            # Start method
            self.starter.set_initial_condition(u[n])
            time_points = [t[n], t[n+1]]
            u_starter, t_starter = self.starter.solve(time_points)
            unew = u_starter[-1]
            if n == 0:
                self.f_n_2 = f(u[0], t[0])
            elif n == 1:
                self.f_n_1 = f(u[1], t[1])

        return unew


class AdamsBashforth4(Solver):
    """
    Fourth-order Adams-Bashforth method::

        u[n+1] = u[n] + dt/24.*(55.*f(u[n], t[n]) - 59*f(u[n-1], t[n-1]) +
                                37*f(u[n-2], t[n-2]) - 9*f(u[n-3], t[n-3]))

    for constant time step dt.

    RK2 is used as default solver for first steps.
    """
    _optional_parameters = Solver._optional_parameters + ['start_method',]

    def set_internal_parameters(self):
        # New solver instance for first steps
        self.starter = self.switch_to(self.start_method)
        # Create variables for f at previous time levels
        self.f_n_1, self.f_n_2, self.f_n_3 = None, None, None
        Solver.set_internal_parameters(self)

    def validate_data(self):
        if not self.constant_time_step():
            print '%s must have constant time step' % self.__name__
            return False
        else:
            return True

    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t

        if n >= 3:
            dt = t[n+1] - t[n]  # must be constant
            self.f_n = f(u[n], t[n])
            unew = u[n] + dt/24.*(55.*self.f_n - 59*self.f_n_1 + \
                                  37*self.f_n_2 - 9*self.f_n_3)
            self.f_n_1, self.f_n_2, self.f_n_3 = \
                self.f_n, self.f_n_1, self.f_n_2
        else:
            # Start method
            self.starter.set_initial_condition(u[n])
            time_points = [t[n], t[n+1]]
            u_starter, t_starter = self.starter.solve(time_points)
            unew = u_starter[-1]
            if n == 0:
                self.f_n_3 = f(u[0], t[0])
            elif n == 1:
                self.f_n_2 = f(u[1], t[1])
            elif n == 2:
                self.f_n_1 = f(u[2], t[2])

        return unew


class AdamsBashMoulton3(Solver):
    """
    Three-step (4th-order) Adams-Bashforth method::

        predictor = u[n] + dt/24.*(55.*f(u[n], t[n]) - 59*f(u[n-1], t[n-1]) +
                                   37*f(u[n-2], t[n-2]) - 9*f(u[n-3], t[n-3]))
        corrector = u[n] + dt/24.*(19.*f(u[n], t[n]) - 5*f(u[n-1], t[n-1]) +
                                   f(u[n-2], t[n-2]) + 9*f(predictor, t[n+1]))

    for constant time step dt.

    RK2 is used as default solver for first steps.
    """
    _optional_parameters = Solver._optional_parameters + ['start_method',]

    def set_internal_parameters(self):
        # New solver instance for first steps
        self.starter = self.switch_to(self.start_method)
        # Create variables for f at previous time levels
        self.f_n_1, self.f_n_2, self.f_n_3 = None, None, None
        Solver.set_internal_parameters(self)

    def validate_data(self):
        if not self.constant_time_step():
            print '%s must have constant time step' % self.__name__
            return False
        else:
            return True

    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t

        if n >= 3:
            dt = t[n+1] - t[n]  # must be constant
            self.f_n = f(u[n], t[n])
            predictor = u[n] + dt/24.*(55.*self.f_n - 59*self.f_n_1 + \
                                  37*self.f_n_2 - 9*self.f_n_3)
            unew = u[n] + dt/24.*(self.f_n_2 - 5*self.f_n_1 + 19*self.f_n + \
                                  9*f(predictor, t[n + 1]))
            self.f_n_1, self.f_n_2, self.f_n_3 = \
                self.f_n, self.f_n_1, self.f_n_2
        else:
            # Start method
            self.starter.set_initial_condition(u[n])
            time_points = [t[n], t[n+1]]
            u_starter, t_starter = self.starter.solve(time_points)
            unew = u_starter[-1]
            if n == 0:
                self.f_n_3 = f(u[0], t[0])
            elif n == 1:
                self.f_n_2 = f(u[1], t[1])
            elif n == 2:
                self.f_n_1 = f(u[2], t[2])

        return unew



class MidpointIter(Solver):
    """
    A midpoint/central difference method with max_iter fixed-point
    iterations to solve the nonlinear system.
    The Forward Euler scheme is recovered if max_iter=1 and f(u,t)
    is independent of t. For max_iter=2 we have the Heun/RK2 scheme.
    """
    _optional_parameters = Solver._optional_parameters + \
                           ['max_iter', 'eps_iter']

    def adjust_parameters(self):
        self._parameters['max_iter']['default'] = 3

    def advance(self):
        if not hasattr(self, 'v'):  # v is a help array needed in the method
            if self.neq == 1:
                self.v = np.zeros(self.max_iter+1, self.u.dtype)
            else:
                self.v = np.zeros((self.max_iter+1, self.neq), self.u.dtype)

        u, f, n, t, v = \
           self.u, self.f, self.n, self.t, self.v
        dt = t[n+1] - t[n]

        v[0] = u[n]
        q = 0
        v_finished = False   # |v[q]-v[q-1]| < eps
        while not v_finished and q < self.max_iter:
            q += 1
            v[q] = u[n] + 0.5*dt*(f(v[q-1], t[n+1]) + f(u[n], t[n]))
            if abs(v[q] - v[q-1]).max() < self.eps_iter:
                v_finished = True
                self.num_iterations = q

        unew = v[q]
        return unew


def approximate_Jacobian(f, u0, t0, h):
    """
    Compute approximate Jacobian of fucntion f at current point (u0,t0).
    Method: forward finite difference approximation with step
    size h.
    Output: a two-dimensional array holding the Jacobian matrix.
    """
    u0 = np.asarray(u0)
    f0 = np.asarray(f(u0, t0))
    neq = len(u0)
    J = np.zeros((neq, neq), float)
    for i in range(neq):
        u_new = u0.copy()
        u_new[i] += h
        J[i] = (np.asarray(f(u_new, t0)) - f0)/h
    return J.transpose()

class SymPy_odefun(Solver):
    """
    Wrapper for the sympy.mpmath.odefun method, which applies a high-order
    Taylor series method to solve ODEs.
    """

    def initialize(self):
        try:
            import sympy
            self.sympy = sympy
        except ImportError:
            raise ImportError,'sympy is not installed - needed for sympy_odefun'

    def set_internal_parameters(self):
        # sympy.odefun requires f(t, u), not f(u, t, *args, **kwargs)
        self.f4odefun = lambda t, u: self.f(u, t, *self.f_args, **self.f_kwargs)
        Solver.set_internal_parameters(self)

    def solve(self, time_points, terminate=None):
        """
        The complete solve method must be overridded in this class
        since sympy.mpmath.odefun is such a solve method.

        The class stores an attribute ufunc (return from odefun)
        which can be used to evaluate u at any time point (ufunc(t)).
        """
        if terminate is not None:
            print 'Warning: SymPy_odefun.solve ignores the terminate function!'
        self.t = np.asarray(time_points)
        self.set_internal_parameters()

        self.sympy.mpmath.mp.dps = 15  # accuracy
        self.ufunc = self.sympy.mpmath.odefun(
            self.f4odefun, time_points[0], self.U0)

        # u and t to be returned are now computed by sampling self.ufunc
        # at the specified time points
        self.u = np.array([self.ufunc(t) for t in time_points])
        self.t = np.asarray(time_points)
        return self.u, self.t



class SolverImplicit(Solver):
    """
    Super class for implicit methods for ODEs.
    Existing solvers are: BackwardEuler, Backward2Step, ThetaRule
    """

    _optional_parameters = Solver._optional_parameters + \
        ['jac', 'jac_args', 'jac_kwargs', 'h_in_fd_jac',
         'nonlinear_solver', 'max_iter', 'eps_iter', 'relaxation']

    def set_internal_parameters(self):
        # Set appropriate value of nonlinear_solver if undefined
        if getattr(self, 'jac', None) is None:   # no jac provided
            if getattr(self, 'nonlinear_solver', None) is None:
                self.nonlinear_solver = 'Picard'  # default if no jac provided
            elif getattr(self, 'nonlinear_solver') == 'Newton':
                 # Approximate jacobian with finite difference approx
                self.jac = lambda u, t: \
                    approximate_Jacobian(self.f, u, t, self.h_in_fd_jac)
        else:
            if getattr(self, 'nonlinear_solver', None) is None:
                self.nonlinear_solver = 'Newton'  # default if jac provided
            # Wrap user-supplied Jacobian in the way f is wrapped
            jac = self.jac
            self.jac = lambda u, t: \
                np.asarray(jac(u, t, *self.jac_args, **self.jac_kwargs))

        Solver.set_internal_parameters(self)

    def advance(self):
        n = self.n
        un, f, t_new, tn = self.u[n], self.f, self.t[n+1], self.t[n]
        dt = t_new - tn

        # General solver routine with Newton or Picard
        # Newton with Finite-Differential or exact Jac
        i, error = 1, 1E+30
        # Forward Euler step for initial guess for nonlinear solver
        u_new = un + (t_new-tn)*f(un,tn)
        # control by number of intern steps and error tolerance
        while i <= self.max_iter and error > self.eps_iter:
            if self.nonlinear_solver == 'Picard':
                unew = self.Picard_update(u_new)
            elif self.nonlinear_solver == 'Newton':
                F, Jac = self.Newton_system(u_new)
                du = F/Jac if self.neq == 1 else np.linalg.solve(Jac, F)
                unew = u_new - du
            elif self.nonlinear_solver == 'FixedPoint':
                unew = un + dt*f(u_new,tn)
            error = np.abs(unew - u_new).max()
            r = self.relaxation    # Relax factor
            u_new = r*unew + (1-r)*un
            i += 1
        return u_new

class BackwardEuler(SolverImplicit):
    """
    Implicit Backward Euler method::

       u[n+1] = u[n] + dt*f(t[n+1], u[n+1])

    """
    def Picard_update(self, ukp1):
        u, f, n, t = self.u, self.f, self.n, self.t
        dt = t[n+1] - t[n]
        return u[n] + dt*f(ukp1, t[n+1])

    def Newton_system(self, ukp1):
        u, f, n, t = self.u, self.f, self.n, self.t
        dt = t[n+1] - t[n]
        F = ukp1 - (u[n] + dt*f(ukp1, t[n+1]))
        J = np.eye(self.neq) - dt*self.jac(ukp1, t[n+1])
        return F, J


class Backward2Step(SolverImplicit):
    """
    Implicit Backward Euler method with 2 steps::

         u[n+1] = u[n]*4/3 - u[n-1]/3 + (t[n+1-t[n-1]])*f(t[n+1], u[n+1])/3
    """
    def Picard_update(self, ukp1):
        u, f, n, t = self.u, self.f, self.n, self.t
        if n == 0:
            # Backward Euler as starter
            dt = t[n+1] - t[n]
            return u[n] + dt*f(ukp1, t[n+1])
        else:
            dt2 = t[n+1] - t[n-1]
            return 4./3*u[n] - 1./3*u[n-1] + (1./3)*dt2*f(ukp1, t[n+1])

    def Newton_system(self, ukp1):
        u, f, n, t = self.u, self.f, self.n, self.t
        if n == 0:
            # Backward Euler as starter
            dt = t[n+1] - t[n]
            F = ukp1 - (u[n] + dt*f(ukp1, t[n+1]))
            J = np.eye(self.neq) - dt*self.jac(ukp1, t[n+1])
        else:
            dt2 = t[n+1] - t[n-1]
            F = ukp1 - (4./3*u[n] - 1./3*u[n-1] + (1./3)*dt2*f(ukp1, t[n+1]))
            J = np.eye(self.neq) - (1./3)*dt2*self.jac(ukp1, t[n+1])
        return F, J


class ThetaRule(SolverImplicit):
    """
    Theta rule method as a typical weighted method with factor theta::

       u[n+1] = u[n] + dt*(theta*f(u[n+1],t[n+1]) + (1 - theta)*f(u[n],t[n]))

    where theta is a float in [0,1].
    """
    _optional_parameters = SolverImplicit._optional_parameters + ['theta']

    def Picard_update(self, ukp1):
        u, f, n, t, theta = self.u, self.f, self.n, self.t, self.theta
        dt = t[n+1] - t[n]
        return u[n] + theta*dt*f(ukp1, t[n+1]) + (1-theta)*dt*f(u[n], t[n])

    def Newton_system(self, ukp1):
        u, f, n, t, theta = self.u, self.f, self.n, self.t, self.theta
        dt = t[n+1] - t[n]
        F = ukp1 - (u[n] + theta*dt*f(ukp1, t[n+1]) + (1-theta)*dt*f(u[n],t[n]))
        J = np.eye(self.neq) - theta*dt*self.jac(ukp1, t[n+1])
        return F, J


class MidpointImplicit(SolverImplicit):
    '''
    Midpoint Implicit method.
    Scheme:
       u[n+1] = u[n] + dt*f((u[n+1] + u[n])/2., t[n] + dt/2.)
    '''

    def Picard_update(self, ukp1):
        u, f, n, t = self.u, self.f, self.n, self.t
        dt = t[n+1] - t[n]
        return u[n] + dt*f((ukp1 + u[n])/2., t[n] + dt/2.)

    def Newton_system(self, ukp1):
        u, f, n, t = self.u, self.f, self.n, self.t
        dt = t[n+1] - t[n]
        F = ukp1 -  u[n] + dt*f((ukp1 + u[n])/2., t[n] + dt/2.)
        J = np.eye(self.neq) - dt*self.jac(ukp1, t[n+1])
        return F, J



class Adaptive(Solver):
    """Superclass for adaptive solvers."""

    _optional_parameters = Solver._optional_parameters + \
        ['rtol', 'atol', 'first_step', 'min_step', 'max_step']

    def set_internal_parameters(self):
        # Let first_step, min_step and max_ste, if not given, be
        # computed from the user's time points, available as self.t.

        if not hasattr(self, 'first_step'):
            # Use user's first step
            self.set(first_step=self.t[1] - self.t[0])
        time_steps = self.t[1:] - self.t[:-1]
        if not hasattr(self, 'min_step'):
            # Use 1/10 of the user's smallest step
            self.set(min_step=0.1*time_steps.min())
        if not hasattr(self, 'max_step'):
            # Use 10 times the user's greatest step
            self.set(max_step=10*time_steps.max())
        Solver.set_internal_parameters(self)


class AdaptiveResidual(Adaptive):
    """
    Designed for educational purposes to demonstrate a possible
    adaptive strategy.

    Currently, only scalar ODE problems can be applied for purpose of
    simplification.
    """

    _optional_parameters = Adaptive._optional_parameters + \
                           ['solver']

    def __init__(self, f, **kwargs):
        Adaptive.__init__(self, f, **kwargs)
        if 'solver' in kwargs:
            del kwargs['solver']
        self.solver = eval(self.solver)(f, **kwargs)

    def residual(self, u_n, u_next, t_n, t_next):
        dt = t_next - t_n
        t_mean = 0.5*(t_n + t_next)
        u_mean = 0.5*(u_n + u_next)
        u_diff = u_next - u_n
        # Central 2nd order difference approx to the residual
        # Valid for scalar ODE only
        return abs(u_diff/dt - self.f(u_mean, t_mean))

    def solve(self, time_points, terminate=None, printInfo=False):
        self.users_time_points = np.asarray(time_points).copy()
        self.t = t = self.users_time_points
        self.set_internal_parameters()
        # Assume scalar equation...
        if not isinstance(self.U0, (float,int)):
            raise TypeError('Initial condition is not scalar - '
                            'AdaptiveResidual can only work with scalar ODEs')
        self.validate_data()
        self.u = [self.U0]
        self.t = [t[0]]
        self.solver.set_initial_condition(self.U0)
        for k in range(1,len(t)):
            R = 1E+20
            # Try to jump until next user point in time
            ntpoints = 1
            # Halve the time step until residual is small enough
            while R > self.atol:
                ntpoints *= 2
                time_points = np.linspace(t[k-1], t[k], ntpoints)
                dt = time_points[1] - time_points[0]
                if dt < self.min_step:
                    print 'AdaptiveResidual with %s solver, too small %s < %s, R=%s > %s' % (self.solver.__class__.__name__, dt, self.min_step, R, self.atol)
                    print
                    break
                if dt > self.max_step:
                    print 'AdaptiveResidual with %s solver, too large step %s > %s, R=%s > %s' % (self.solver.__class__.__name__, dt, self.max_step, R, self.atol)
                    break

                self.solver.set_initial_condition(self.u[-1])
                unew, tnew = self.solver.solve(time_points, terminate)
                R = self.residual(unew[-2], unew[-1], tnew[-2], tnew[-1])
                if printInfo:
                    print '\n%d time points in (t[%d], t[%d]) = (%.3g, %.3g)' \
                        % (ntpoints, k-1, k, t[k-1], t[k])
                    print 'Residual = %g, Tolerance = %g, calling %s' % \
                        (R, self.atol, self.solver.__class__.__name__)
                # reintegrate with time_step = dt/2
            self.u.extend(unew[1:])
            self.t.extend(tnew[1:])
        return self.u, self.t


class RKFehlberg(Adaptive):
    """The classical adaptive Runge-Kutta-Fehlberg method of order 4-5."""

    _optional_parameters = Adaptive._optional_parameters


    def set_internal_parameters(self):
        Solver.set_internal_parameters(self)

    def advance(self):
        # auxilatory function to pick up the middle number from 3 floats
        def middle(x, y=.1, z=4.):
           return sorted([x, y, z])[1]

        f, n, rtol, atol = self.f, self.n, self.rtol, self.atol
        u_n, t_n, t_next = self.u[n], self.t[n], self.t[n+1]

        dt = t_next - t_n

        # default setting of step size
        min_step, max_step, h = \
            getattr(self, 'min_step', dt/1000.), \
            getattr(self, 'max_step', dt),\
            getattr(self, 'first_step', dt)

        # coefficients in Butcher tableau
        c = (1/4.,
             3/8.,
             3/32.,
             9/32.,
             12/13.,
             1932/2197.,
             -7200/2197.,
             7296/2197.,
             439/216.,
             -8.,
             3680/513.,
             -845/4104.,
             1/2.,
             -8/27.,
             2.,
             -3544/2565.,
             1859/4104.,
             -11/40.,
             1/360.,
             -128/4275.,
             -2197/75240.,
             1/50.,
             2/55.,
             25/216.,
             1408/2565.,
             2197/4104.,
             -1/5.)

        uwork = [u_n,]; twork = [t_n,]
        u, t = u_n, t_n

        while abs(t - t_n) < abs(t_next - t_n):
            u, t = uwork[-1], twork[-1]

            # internal steps
            k1 = h*f(u, t)
            k2 = h*f(u+k1*c[0], t+h*c[0])
            k3 = h*f(u+k1*c[2]+k2*c[3], t+h*c[1])
            k4 = h*f(u+k1*c[5]+k2*c[6]+k3*c[7], t+h*c[4])
            k5 = h*f(u+k1*c[8]+k2*c[9]+k3*c[10]+k4*c[11], t+h)
            k6 = h*f(u+k1*c[13]+k2*c[14]+k3*c[15]+k4*c[16]+k5*c[17],
                     t+h*c[12])
            u_new = u + k1*c[23] + k3*c[24] + k4*c[25] + k5*c[26]

            # local error between 2 levels
            error = np.abs(k1*c[18] + k3*c[19] + k4*c[20] + \
                          k5*c[21] + k6*c[22])
            tol = rtol*np.abs(u_new) + atol
            # Error factor = local-error/error-tolerance
            rms = error/tol
            rms_norm = np.sqrt((np.sum(rms*rms))/self.neq)

            # Close enough or step size can not be reduced any more
            if rms_norm <= 1. or h <= min_step:
                uwork.append(u_new); twork.append(t+h)

            # prevent the error of dividing absolute zero
            error = np.asarray([(1e-16 if x == 0. else x) for x in error]) \
                   if self.neq > 1 else (1e-16 if error == 0. else error)

            # Factor to adjust next step size
            s = (tol/(2*error))**0.25
            # factor should be in a reasonable range[0.1,4.0]
            s = min(map(middle, s)) if self.neq > 1 else middle(s)

            # step size should be in reasonable range [min_step, max_step]
            h = middle(h*s, y=min_step, z=max_step)

            # h should be set to 't_next-twork[-1]' at the last intern step.
            h = min(h, t_next-twork[-1])

        return u_new

class Ode_scipy(Adaptive):
    """
    Super class wrapper for scipy.integrate.ode classes.
    Existing solvers in subclasses are: Vode, Dopri5, Dop853.
    """
    _optional_parameters = Solver._optional_parameters + \
        ['jac', 'jac_kwargs', 'jac_args', 'atol', 'rtol',
         'first_step', 'max_step', 'nsteps']

    # Common scipy.integrate.ode arguments for subclass solvers
    _arglist_scipy = ['f', 'jac', 'atol', 'rtol', 'complex_valued',]
    # Name differences between this interface and scipy arguments
    _name_differences = {'adams_or_bdf': 'method',
                         'ml': 'lband', 'mu': 'rband'}

    def initialize(self):
        try:
            import scipy.integrate.ode as si_ode
        except ImportError:
            raise ImportError('The scipy package must be installed '\
                              'in order to use class %s' % \
                              self.__class__.__name__)

    def set_internal_parameters(self):
        # scipy specifies f and jac as f(t, y, *args) and jac(t, y)
        # while the present interface assumes
        # f(u, t, *f_args, **f_kwargs), jac(u, t, *jac_args, **jac_kwargs)
        self.f4scipy = lambda t, y: self.f(y, t)
        if self.jac is not None:
            # First wrap the user's Jacobian routine as we wrap f
            # (allow jac to return list of lists)
            jac = self.jac
            self.jac = lambda u, t: \
                np.asarray(jac(u, t, *self.jac_args, **self.jac_kwargs))
            # Then switch argument sequence
            self.jac4scipy = lambda t, y: self.jac(y, t)
        else:
            self.jac4scipy = None

        import scipy.integrate.ode as si_ode
        self.integrator = si_ode(self.f4scipy, jac=self.jac4scipy)
        self.scipy_arguments = {}

        # Extract common arguments, and prepare to be transferred to scipy
        for name in self._arglist_scipy:
            value = getattr(self, name, None)
            if value is not None:
                if name in self._parameters and \
                   name in Ode_scipy._name_differences:
                    # different names in scipy
                    name = Ode_scipy._name_differences[name]
                self.scipy_arguments[name] = value

        self.integrator = self.integrator.set_integrator(
            self.__class__.__name__.lower(), **self.scipy_arguments)
        self.integrator = self.integrator.set_initial_value(self.U0, self.t[0])
        Solver.set_internal_parameters(self)

    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t
        unew = self.integrator.integrate(t[n+1])
        if not self.integrator.successful():
            print 'Warning: %s call to scipy.integrate.ode.method.integrate was not successful' % self.__class__.__name__
        if len(unew) == 1:
            return unew[0]
        else:
            return unew

class Vode(Ode_scipy):
    '''
    Wrapper for scipy.integrate.ode.vode, which is a wrapper for vode.f,
    which intends to solve initial value problems of stiff or nonstiff
    type. The well-known vode.f solver applies backward differential
    formulae for iteration.
    '''
    _optional_parameters = Ode_scipy._optional_parameters + \
                           ['adams_or_bdf', 'min_step', 'order']

    # argument list to be passed to scipy.ode for 'vode' method
    _arglist_scipy = ['atol', 'rtol', 'ml', 'mu', 'adams_or_bdf',
                      'with_jacobian', 'nsteps', 'first_step',
                      'min_step', 'max_step', 'order']

    def set_internal_parameters(self):
        # internal argument to be transferred to scipy
        self.with_jacobian = getattr(self, 'jac', None) is not None
        Ode_scipy.set_internal_parameters(self)

class Dopri5(Ode_scipy):
    """
    Wrapper for scipy.integrate.ode.dopri5, which applies the
    Dormand&Prince method of order 5.
    """
    _optional_parameters = Ode_scipy._optional_parameters + \
        ['ifactor', 'dfactor', 'beta', 'safety']

    # argument list to be passed to scipy.ode for 'dopri5' method
    _arglist_scipy = ('atol','rtol','safety','ifactor','dfactor','beta',
                      'nsteps','first_step','max_step')

class Dop853(Ode_scipy):
    """
    Wrapper for scipy.integrate.ode.dop853, which applies the
    Dormand&Prince method of order 8(5,3).
    """
    _optional_parameters = Ode_scipy._optional_parameters + \
        ['ifactor', 'dfactor', 'beta', 'safety']

    # argument list to be passed to scipy.ode for 'dop853' method
    _arglist_scipy = ('atol','rtol','safety','ifactor','dfactor','beta',
                      'nsteps','first_step','max_step')

def list_all_solvers():
    """Return all solver classes in this package, excluding superclasses."""
    # Important: odesolvers.__init__.py must import all solver classes
    # into the namespace for this function to work properly.

    superclasses = ('Solver','Adaptive', 'PyDS', 'Ode_scipy', 'Odepack',
                    'RungeKutta', 'SolverImplicit')
    import odesolvers
    class_members = inspect.getmembers(odesolvers, inspect.isclass)
    solvers = [solver[0] for solver in class_members \
                   if solver[0] not in superclasses]
    return solvers

def list_available_solvers():
    """Return all available solver classes in this package."""
    available_solvers = []
    import odesolvers
    all_solvers = list_all_solvers()
    for solvername in all_solvers:
        try:      # Try to initialize solvers with f is None
            method = eval('odesolvers.%s' % solvername)(None)
            available_solvers.append(solvername)
        except:
            try:
                # Try the exception of linearly solvers in ODEPACK
                # f is illegal for these solvers.
                method = eval('odesolvers.%s' % solvername)()
                available_solvers.append(solvername)
            except:
                # Failed to initialize this solver.
                # Perhaps the required dependency is not installed.
                pass
    return available_solvers

