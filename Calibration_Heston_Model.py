#next: parameter estimation of params with (stochgradient) descent dafür funktion unten anpassen an die params die ich hab

import numpy as np
import pandas as pd
from get_calibration_data import get_calibration_data
from scipy.optimize import basinhopping
import QuantLib as ql


def optionval(strike, stockprice):
    return max([0,stockprice-strike])

data=get_calibration_data()
calibration_data_heston=data[0]#anpassen, wenn das named array ist

market_data=data[1]

rfr=market_data.loc[0,"RiskFreeRate"]
  
rfr=market_data.loc[0,"RiskFreeRate"]  
deltat=market_data.loc[0,"Deltat"]
spot=market_data.loc[0,"S0"]
numsteps=market_data.loc[0,"numsims"]

strikes=list(calibration_data_heston["strike"])
market_prices_calls=list(calibration_data_heston["lastPrice"])
strikes.pop()#last element is unecessary metadata
market_prices_calls.pop()#last element is unecessary metadata

calibration_strikes_prices=[strikes,market_prices_calls] 

calibration_date=calibration_data_heston["lastTradeDate"].loc[0]


day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()
calculation_date = ql.Date(calibration_date.day, calibration_date.month, calibration_date.year)
ql.Settings.instance().evaluationDate = calculation_date

expiration_dates=[calculation_date]*len(calibration_data_heston)
strikes=calibration_data_heston["strike"]
impvola=[calibration_data_heston["impliedVolatility"]]



dividend_rate = 0.0
yield_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, rfr, day_count))
dividend_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, dividend_rate, day_count))



def generate_multi_paths_df(sequence, num_paths):
    spot_paths = []
    vol_paths = []

    for i in range(num_paths):
        sample_path = sequence.next()
        values = sample_path.value()

        spot, vol = values

        spot_paths.append([x for x in spot])
        vol_paths.append([x for x in vol])

    df_spot = pd.DataFrame(spot_paths, columns=[spot.time(x) for x in range(len(spot))])
    df_vol = pd.DataFrame(vol_paths, columns=[spot.time(x) for x in range(len(spot))])

    return df_spot, df_vol




def wrapper_heston(x,yield_ts,dividend_ts,spot,seed):
    #to do:fix rng to fixed seed
    '''
    :param x: List of arguments for heston engine with x[0]=theta,x[1]=kappa,x[2]=sigma,x[3]=rho,x[4]=v0
    :return last price of heston stock price given arguments 
    '''
    timestep = 100
    length = deltat
    times = ql.TimeGrid(length, timestep)

    heston_process=ql.HestonProcess(yield_ts, dividend_ts, spot, x[0],x[1],x[2],x[3],x[4])
    dimension = heston_process.factors()
    rng = ql.GaussianRandomSequenceGenerator(ql.UniformRandomSequenceGenerator(dimension * timestep, ql.UniformRandomGenerator(seed=seed)))
    seq = ql.GaussianMultiPathGenerator(heston_process, list(times), rng, False)
    sample_path,sample_vol=generate_multi_paths_df(seq,num_paths=1)
    heston_price=sample_path.iloc[0]
    heston_price=list(heston_price).pop()
    
    
    return heston_price



def wrapper_lsq(x):

    strikes=calibration_strikes_prices[0]
    option_prices_market=calibration_strikes_prices[1]
    N=len(strikes)
    
    heston_price=wrapper_heston(x,yield_ts,dividend_ts,ql.QuoteHandle(ql.SimpleQuote(spot)),seed=2 )
    print(heston_price)
    for i in range(N):
        lsq=(optionval(heston_price,strikes[i])-option_prices_market[i])**2

    lsq=lsq/N

    return lsq

#bound the parameter space in order not to breach into unvalid parameter space
 
btheta = (0,1)
bkappa = (0.01,15)
bsigma = (0.01,1.)
brho = (-1,1)
bsigma0 = (0,1.0)
bounds = [btheta, bkappa, bsigma, brho, bsigma0]

class RandomDisplacementBounds(object):
    """random displacement with bounds:  see: https://stackoverflow.com/a/21967888/2320035
    """
    def __init__(self, xmin, xmax, stepsize=0.5):
        self.xmin = xmin
        self.xmax = xmax
        self.stepsize = stepsize

    def __call__(self, x):
        """take a random step but ensure the new position is within the bounds """
        min_step = np.maximum(self.xmin - x, -self.stepsize)
        max_step = np.minimum(self.xmax - x, self.stepsize)

        random_step = np.random.uniform(low=min_step, high=max_step, size=x.shape)
        xnew = x + random_step

        return xnew

bounded_step = RandomDisplacementBounds(np.array([b[0] for b in bounds]), np.array([b[1] for b in bounds]))

#Custom optimizer
minimizer_kwargs = {"method":"L-BFGS-B", "bounds": bounds}

#Solve with bounds
x0=[0.07, 0.5, 0.1, 0.1, 0.1] #initial_conditions
ret = basinhopping(wrapper_lsq, x0, minimizer_kwargs=minimizer_kwargs, niter=10, take_step=bounded_step)




print("global minimum: x = [%.4f, %.4f, %.4f, %.4f, %.4f], f(x) = %.4f" % (ret.x[0],
                                                          ret.x[1],ret.x[2],ret.x[3],ret.x[4],
                                                          ret.fun))


    
    

    









