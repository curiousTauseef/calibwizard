'''The following program computes the non-linearity correction coefficients using csv as the input'''
'''Example: python NonLinearityCalibration.py --file filename --phaseCorr 0 --modFreq 48 '''

 # 
 #
 # Copyright (C) {2017} Texas Instruments Incorporated - http://www.ti.com/ 
 # 
 # 
 #  Redistribution and use in source and binary forms, with or without 
 #  modification, are permitted provided that the following conditions 
 #  are met:
 #
 #    Redistributions of source code must retain the above copyright 
 #    notice, this list of conditions and the following disclaimer.
 #
 #    Redistributions in binary form must reproduce the above copyright
 #    notice, this list of conditions and the following disclaimer in the 
 #    documentation and/or other materials provided with the   
 #    distribution.
 #
 #    Neither the name of Texas Instruments Incorporated nor the names of
 #    its contributors may be used to endorse or promote products derived
 #    from this software without specific prior written permission.
 #
 #  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
 #  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
 #  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 #  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
 #  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
 #  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
 #  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 #  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 #  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
 #  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
 #  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 #
#

import csv
import os
import sys
import numpy as np
import argparse

def NonLinearityCalibration(filename, modFreq, modFreq2, phaseCorr = 0, phaseCorr2 = 0):
    """This function computes non linearity coefficients. 
    
    **Parameters**::
        -fileName: CSV file containing data of measured distance and captured phase
        -phaseCorr: The phase offset value for the given modulation frequency
        -modFreq: The modulation frequency at which data is captured. 
        
    **Returns**::
        -Non linearity coefficients for the given profile
        """
    c = 299792458
    if not os.path.exists(filename):
        return
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        distances = []
        phases = []
        phases2 = []
        for row in reader:
            distances.append(float(row[0]))
            phases.append(float((row[1])))
            if len(row) > 2:
                phases2.append(float(row[2]))
    if not distances or not phases:
        print("Data missing")
        return
    distances = np.array(distances)
    phases = np.array(phases)
    
    distancesToPhase = distances*modFreq*4096*2e6/(100*c)
    distancesToPhase = distancesToPhase[distances.argsort()]
    measuredPhase = phases[distances.argsort()]
    print (measuredPhase)
    y = getCoefficients(measuredPhase, distancesToPhase, phaseCorr)
    if phases2:
        phases2 = np.array(phases2)
        distancesToPhase2 = distances*modFreq2*4096*2e6/(100*c)
        distancesToPhase2 = distancesToPhase2[distances.argsort()]
        measuredPhase2 = phases2[distances.argsort()]
        y1 = getCoefficients(measuredPhase2, distancesToPhase2, phaseCorr2)
    else:
        y1 = None

    return True, y, y1

def getCoefficients(measuredPhase, distancesToPhase, phaseCorr):
    if not phaseCorr:
        phaseCorr1 = -distancesToPhase[np.size(measuredPhase)/2] + measuredPhase[np.size(measuredPhase)/2]
        print phaseCorr1
    else:
        phaseCorr1 = 0              
    expectedPhase = distancesToPhase + phaseCorr + phaseCorr1
    expectedPhase = expectedPhase%4096    
    measuredPhase = measuredPhase + phaseCorr
    indices = measuredPhase.argsort()
    measuredPhase = measuredPhase[indices]
    expectedPhase = expectedPhase[indices]
    print (expectedPhase)
    print (measuredPhase)
    offsetPoints = np.arange(0., 4096., 256.)        
    y = np.around(np.interp(offsetPoints, measuredPhase, expectedPhase))
    indexes = []
    for val in np.arange(len(y)-1):
        indexes.append(y[val] == y[val+1])
    for val in np.arange(len(indexes)-1):
        if indexes[val] == True and indexes[val+1] == False:
            y[0:val+1] = offsetPoints[0:val+1]
        if indexes[val] == False and indexes[val+1] == True:
            y[val+1:] = offsetPoints[val+1:]
            y = y.astype(int)          
    return y
            
def parseArgs (args = None):
    
    parser = argparse.ArgumentParser(description='Calculate Common Phase Offsets')
    parser.add_argument('-f', '--file', help = 'CSV file', required = 'True', default= None)
    parser.add_argument('-m', '--modFreq', type = float, help = 'Modulation Frequency', required = 'True', default= 10)
    parser.add_argument('-p', '--phaseCorr', help = 'Phase Corr Value', type = int,  required = 'True', default = 0)     
    return parser.parse_args(args)           

if __name__ == '__main__':
    val = parseArgs(sys.argv[1:])
    ret = NonLinearityCalibration(val.file, val.phaseCorr, val.modFreq)
    if not ret:
        print"Can't get the nonlinearity coefficients"
        sys.exit()
    else: 
        boo, coefficients, expectedPhase, measuredPhase = ret
        data = ''
        for c in coefficients:
            data += str(c) + ' '
    
    print "phase_lin_coeff0 = " + data