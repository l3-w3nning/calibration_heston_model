# calibration_heston_model
The logic is as follows: The user is asked for a Stock Ticker and a (Call) Option expiration date over a GUI, afterwards option chain data is loaded over the yfinance datafeed into a SQLite database. From there the user can access the data and proceed to calibrate a Heston model (with 5 parameters) with the given option chain. (However the SQL DBs are also supplied here)
The calibration uses elements of the quantlib library (simulation of paths of the heston model for a given set of params), however i plan to also implement a Euler-Maruyama scheme myself (to see how much worse poorly written Python code is performance-wise compared to the C++-backed quantlib routines;).
The paths of the Heston model are then passed to a LeastSquares wrapper function, which is then passed to the Basin Hopping algorithm (which luckily is already implemented in Scipy). This algorithm derives a global optimum, however the range of possible parameters is constrained manually by the user in order for the parameters to remain in a sensible range.
