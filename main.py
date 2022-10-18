from gui import mclass
from set_calibration_data import set_option_data
from tkinter import *
from tkinter.ttk import *
from Calibration_Heston_Model import (
    calibration_heston,
    RandomDisplacementBounds,
    wrapper_lsq,
)
import numpy as np


def main():

    # load data into db
    #stock_data = input("please enter stock ticker: ")
    #base_date = input("please enter expiration date in format YYYY-mm-dd: ")
    #data = set_option_data(stock_data, base_date)
    #window = Tk()
    #start = mclass(window, data)

    #window.mainloop()

    # bound the parameter space in order not to breach into unvalid parameter space

    btheta = (0, 1)
    bkappa = (0.01, 15)
    bsigma = (0.01, 1.0)
    brho = (-1, 1)
    bsigma0 = (0, 1.0)
    bounds = [btheta, bkappa, bsigma, brho, bsigma0]

    bounded_step = RandomDisplacementBounds(
        np.array([b[0] for b in bounds]), np.array([b[1] for b in bounds])
    )

    # Custom optimizer
    minimizer_kwargs = {"method": "L-BFGS-B", "bounds": bounds}

    # Solve with sensible bounds
    x0 = [
        0.07,
        0.5,
        0.1,
        0.1,
        0.1,
    ]  # initial_conditions, arbitrary, note that basin hopping should be rather robust w.r.t. change in initial conditions

    calibrated_params = calibration_heston(
        wrapper_lsq, x0, minimizer_kwargs, bounded_step
    )

    print(
        "global minimum: x = [theta=%.4f, kappa=%.4f, sigma=%.4f, rho=%.4f, v0=%.4f], f(x) (minimum of option market prices and model prices) = %.4f"
        % (
            calibrated_params.x[0],
            calibrated_params.x[1],
            calibrated_params.x[2],
            calibrated_params.x[3],
            calibrated_params.x[4],
            calibrated_params.fun,
        )
    )


if __name__ == "__main__":
    main()
