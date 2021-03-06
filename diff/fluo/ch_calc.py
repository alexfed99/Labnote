#!/usr/bin/env python3

""" Copyright © 2020 Borys Olifirov
Channels crosstalk calculator

"""

import sys
import os
import logging

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt


def wavelen2rgb(Wavelength, MaxIntensity=100):
    """Calculate RGB values given the wavelength of visible light.

    Arguments:
    * Wavelength:  Wavelength in nm.  Scalar floating.
    * MaxIntensity:  The RGB value for maximum intensity.  Scalar 
      integer.

    Returns:
    * 3-element list of RGB values for the input wavelength.  The
      values are scaled from 0 to MaxIntensity, where 0 is the
      lowest intensity and MaxIntensity is the highest.  Integer
      list.

    Visible light is in the range of 380-780 nm.  Outside of this
    range the returned RGB triple is [0,0,0].

    Based on code by Earl F. Glynn II at:
       http://www.efg2.com/Lab/ScienceAndEngineering/Spectra.htm
    See also:
       http://www.physics.sfasu.edu/astro/color/spectra.html
    whose code is what Glynn's code is based on.

    Example:
    >>> from wavelen2rgb import wavelen2rgb
    >>> waves = [300.0, 400.0, 600.0]
    >>> rgb = [wavelen2rgb(waves[i], MaxIntensity=255) for i in range(3)]
    >>> print rgb
    [[0, 0, 0], [131, 0, 181], [255, 190, 0]]
    """

    def Adjust_and_Scale(Color, Factor, Highest=100):
        """Gamma adjustment.

        Arguments:
        * Color:  Value of R, G, or B, on a scale from 0 to 1, inclusive,
          with 0 being lowest intensity and 1 being highest.  Floating
          point value.
        * Factor:  Factor obtained to have intensity fall off at limits 
          of human vision.  Floating point value.
        * Highest:  Maximum intensity of output, scaled value.  The 
          lowest intensity is 0.  Scalar integer.

        Returns an adjusted and scaled value of R, G, or B, on a scale 
        from 0 to Highest, inclusive, as an integer, with 0 as the lowest 
        and Highest as highest intensity.

        Since this is a helper function I keep its existence hidden.
        See http://www.efg2.com/Lab/ScienceAndEngineering/Spectra.htm and
        http://www.physics.sfasu.edu/astro/color/spectra.html for details.
        """
        Gamma = 0.80

        if Color == 0.0:
            result = 0
        else:
            result = int( round(pow(Color * Factor, Gamma) * round(Highest)) )
            if result < 0:        result = 0
            if result > Highest:  result = Highest

        return result


    if (Wavelength >= 380.0) and (Wavelength < 440.0):
        Red   = -(Wavelength - 440.) / (440. - 380.)
        Green = 0.0
        Blue  = 1.0

    elif (Wavelength >= 440.0) and (Wavelength < 490.0):
        Red   = 0.0
        Green = (Wavelength - 440.) / (490. - 440.)
        Blue  = 1.0

    elif (Wavelength >= 490.0) and (Wavelength < 510.0):
        Red   = 0.0
        Green = 1.0
        Blue  = -(Wavelength - 510.) / (510. - 490.)

    elif (Wavelength >= 510.0) and (Wavelength < 580.0):
        Red   = (Wavelength - 510.) / (580. - 510.)
        Green = 1.0
        Blue  = 0.0

    elif (Wavelength >= 580.0) and (Wavelength < 645.0):
        Red   = 1.0
        Green = -(Wavelength - 645.) / (645. - 580.)
        Blue  = 0.0

    elif (Wavelength >= 645.0) and (Wavelength <= 780.0):
        Red   = 1.0
        Green = 0.0
        Blue  = 0.0

    else:
        Red   = 0.0
        Green = 0.0
        Blue  = 0.0


    #- Let the intensity fall off near the vision limits:

    if (Wavelength >= 380.0) and (Wavelength < 420.0):
        Factor = 0.3 + 0.7*(Wavelength - 380.) / (420. - 380.)
    elif (Wavelength >= 420.0) and (Wavelength < 701.0):
        Factor = 1.0
    elif (Wavelength >= 701.0) and (Wavelength <= 780.0):
        Factor = 0.3 + 0.7*(780. - Wavelength) / (780. - 700.)
    else:
        Factor = 0.0


    #- Adjust and scale RGB values to 0 to MaxIntensity integer range:

    R = Adjust_and_Scale(Red,   Factor, MaxIntensity)
    G = Adjust_and_Scale(Green, Factor, MaxIntensity)
    B = Adjust_and_Scale(Blue,  Factor, MaxIntensity)


    #- Return 3-element list value:

    return [R, G, B]


class fluorophore:
    def __init__(self, fluo_name, fluo_df, laser_list, ch_list):
        self.fluo_name = fluo_name
        self.ex_spec = np.array(fluo_df.ex)
        self.em_spec = np.array(fluo_df.em)


FORMAT = "%(asctime)s| %(levelname)s [%(filename)s: - %(funcName)20s]  %(message)s"
logging.basicConfig(level=logging.INFO,
                    format=FORMAT)

plt.style.use('dark_background')
plt.rcParams['figure.facecolor'] = '#272b30'


fluo_list = ['mTFP1', 'fluo_4']
ex_list = [456, 488]
ch_dict = {'ch_1':[492, 510],
           'ch_2':[510, 600]}

# read CSV spectra
spectra_dict = {}
for root, dirs, files in os.walk(os.getcwd()):
    for file in files:
        if file.endswith('.csv') and file.split('.')[0] in fluo_list:
            file_path = os.path.join(root, file)

            raw_csv = pd.read_csv(file_path)
            raw_csv.columns = ['w', 'ex', 'em']

            if raw_csv['em'].max() <= 1:
              raw_csv['ex'] = raw_csv['ex'] *100
              raw_csv['em'] = raw_csv['em'] *100

            spectra_dict.update({file.split('.')[0]: raw_csv})
            logging.info('{} spectra uploaded'.format(file.split('.')[0]))


# ex lvl
ch_talk = {}
for fluo in fluo_list:
    fluo_spectra = spectra_dict[fluo]
    for laser in ex_list:
        ex_lvl = int(fluo_spectra.loc[fluo_spectra['w'] == laser, 'ex'])
        logging.info('{}|{} nm = {}'.format(fluo, laser, ex_lvl))
#     for ch in ch_dict:
#         ch_bandpass = ch_dict[ch]
#         print(fluo_spectra.index[fluo_spectra['w'] >= ch_bandpass[0] and fluo_spectra['w'] <= ch_bandpass[1]].tolist())



# crosstalk


# build plots
for fluo in fluo_list:
    fluo_spectra = spectra_dict[fluo]
    plt.plot(fluo_spectra.w, fluo_spectra.em,  # emission
             label='{}, em'.format(fluo),
             color=wavelen2rgb(fluo_spectra.loc[fluo_spectra['em'].idxmax(), 'w'], 1))
    plt.plot(fluo_spectra.w, fluo_spectra.ex,  # excitation
             label='{}, ex'.format(fluo),
             linestyle='--',
             color=wavelen2rgb(fluo_spectra.loc[fluo_spectra['em'].idxmax(), 'w'], 1))

for ch in ch_dict:
    ch_band = ch_dict[ch]
    plt.fill_between(x=range(ch_band[0], ch_band[1], 1),
                 y1=0,
                 y2=110,
                 alpha=0.35,
                 label=ch)

for laser in ex_list:
    plt.plot([laser, laser], [0, 110],
             label='{} nm'.format(laser),
             linewidth=2,
             color=wavelen2rgb(laser, 1))

plt.xlabel('Wavelength, nm')
plt.ylabel('Intensity, %')
plt.xlim(300,650)
plt.legend()
plt.tight_layout()
plt.show()
