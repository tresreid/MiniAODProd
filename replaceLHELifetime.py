#! /usr/bin/env python
import random
import argparse
import os

# inFn = 'mylhes/psZpMuMu_Mps-100p0_MZp-10p0_ctau-0p1_3583819.lhe'
# outFn = 'replaced.lhe'
# rpid = 32
# ctau = 0.1 #mm

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', type=str, required=True, help='Input LHE, which is to be replaced')
parser.add_argument('-t', '--ctau', type=float, required=True, help='Mean proper decay length[mm]')
parser.add_argument('-p', '--pid', type=int, default=1000023, help='Particle whose lifetime is going to be replaced')
args = parser.parse_args()

inFn = args.input
rpid = 1000023
#rpid = args.pid
ctau = args.ctau
#ctau = 100.0

if __name__ == '__main__':
    inf = open(inFn, 'r')
    outf = open(inFn+'.tmp', 'w')

    eventBegin = False
    eventEnd = True
    
    for line in inf:
        if line.startswith('<event>'):
            eventBegin = True
            eventEnd = False
        if line.startswith('</event>'):
            eventBegin = False
            eventEnd = True

        if not (eventBegin==True and eventEnd==False):
            outf.write(line)
            continue
        if (line.split()[0] != str(1000023)):
            outf.write(line)
            continue
        else:
            assert(len(line.split())==13)
            togo = line.split()
            #togo[11] = '{0:.5E}'.format(ctau))
	    if ctau == 0:
		pass
	    else:
            	togo[11] = '{0:.5E}'.format(random.expovariate(1./ctau))
            outf.write(' '.join(togo) + '\n')

    outf.close()
    inf.close()

    os.system('mv {0}.tmp {0}'.format(inFn))	
