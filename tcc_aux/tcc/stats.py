import numpy as np
def correlation(y_values_curve1,y_values_curve2):
    ## Calculate the Pearson correlation coefficient
    correlation_matrix = np.corrcoef(y_values_curve1, y_values_curve2)
    correlation_coefficient = correlation_matrix[0, 1]
    #
    print(f"Correlation Coefficient: {correlation_coefficient}")
    return correlation_coefficient

#region MODIFIED

#############################################################
# @copyright Copyright (c) 2020 All Right Reserved, b<>com http://www.b-com.com/
#
# BER/SER of LoRa signal
# Author: Vincent Savaux, IRT b<>com, Rennes
# email: vincent.savaux@b-com.com
# date: 2020-08-21

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, see <http://www.gnu.org/lice
#############################################################

#@@@@@@@@@@@@@@@@@@@@ Modified by Vitor Carvalho @@@@@@@@@@@@@@@@@@@@@@


#############################################################
# Import some external function
#############################################################
import gmpy2
from gmpy2 import mpfr
from scipy.special import comb

#############################################################
# Set precision
# at least 150 bits for SF7, up to 4000 bits for SF12
#############################################################

def trim_ber_plot(error_list,limit = 10e-4):
    trimmed_error_list = []
    for i in range(0,len(error_list)):
        if error_list[i] <= limit:
            trimmed_error_list.append(limit)
        else:
            trimmed_error_list.append(error_list[i])
    return trimmed_error_list
    

def theoric_BER(sf, snr_start=-25, snr_end=0, step=0.2, trim_limit = 0, precision=4000):
    # Set/initialize parameters
    n_fft = 2**sf  # Corresponding FFT size
    p_error_nochan =[]
    p_error = []  # list containing the error probability for Rayleigh channel
    p_error_rice = []  # list containing the error probability for Rice channel
    # Set Rice/Rayleigh parameters
    sigma_h_ray = 1.  # variance of Rayleigh channel
    lambda_rice = 1.  # default value of mean of Rice distribution
    sigma_h_rice = 0.25  # variance of Rayleigh channel

    # print(lambda_rice,sigma_h_rice)
    gmpy2.get_context().precision = precision
    # Calculate the number of steps
    num_steps = int((snr_end - snr_start) / step) + 1

    # Create the list of SNR values
    SNR_l = [snr_start + i * step for i in range(num_steps)]
    print(len(SNR_l))
    for snr in SNR_l:
        # print(snr)
        sig2 = mpfr(10**(-snr/10.0))  # Noise variance
        # snr_lin = mpfr(1*10**(snr/10.0))
        error = mpfr(0.0)  # Initialise error
        error_nochan = mpfr(0.0) # Initialise error
        error_rice = mpfr(0.0)  # Initialise error
        for k in range(1, n_fft):
            nchoosek = mpfr(comb(n_fft-1, k, exact=True))
            #################################################
            # Symbol Error Rate over AWGN Channel
            #################################################
            error_nochan = error_nochan - mpfr(nchoosek * (-1)**k / (k+1)) \
             * mpfr(gmpy2.exp(-k*n_fft/(2*(k+1)*sig2)))
            #################################################
            # Symbol Error Rate over Rice Channel
            #################################################
            error_rice = error_rice - mpfr(nchoosek * (-1)**k*sig2 / ((k+1)*sig2 + k*n_fft*sigma_h_rice)) \
                * mpfr(gmpy2.exp(-1*k*n_fft*lambda_rice/((k+1)*sig2 + k*n_fft*sigma_h_rice)))
            #################################################
            # Symbol Error Rate over Rayleigh Channel
            #################################################
            error = error - mpfr(nchoosek * (-1)**k*sig2 /
                                 ((k+1)*sig2 + k*n_fft*sigma_h_ray))
            # print(nchoosek)
        error_nochan = mpfr(error_nochan, 32)  # Limit precision for printing/saving
        p_error_nochan.append(float(error_nochan))
        error = mpfr(error, 32)  # Limit precision for printing/saving
        p_error.append(float(error))
        error_rice = mpfr(error_rice, 32)
        p_error_rice.append(float(error_rice))

    if(trim_limit!=0):
        trimmed_ber_awgn = trim_ber_plot(p_error_nochan)
        #trimmed_ber_ray = trim_ber_plot(p_error)
        #trimmed_ber_rice = trim_ber_plot(p_error_rice)
        return [SNR_l,trimmed_ber_awgn]#,trimmed_ber_ray,trimmed_ber_rice]
    else :
        return [SNR_l,p_error_nochan]#n,p_error,p_error_rice]
    
#endregion MODIFIED