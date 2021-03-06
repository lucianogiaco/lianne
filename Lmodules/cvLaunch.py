

#####################################
# NAME: cvLaunch.py.py
# AUTHOR: Luciano Giaco'
# Date: 03/02/2022
version = "0.1"
# ===================================

# Launch script for coverage
# It's required because it needs to parse 
# the bam file folder when the localApp finiched

import os
import argparse
import subprocess

LIANNE_FOLDER = '/data/hpc-data/shared/pipelines/lianne/'
COV_MODULE = os.path.join(LIANNE_FOLDER, 'Lmodules/coverage.py')



def main(email, out_localApp, debug, ot):

	par = '#! /bin/bash\n\
\n\
#PBS -o '+out_localApp+'/stdout_coverage\n\
#PBS -e '+out_localApp+'/stderr_coverage\n\
#PBS -l select=1:ncpus=2:mem=5g\n'
	if email == 'noEmail':
		pass 
	else:
		par = par+"#PBS -M "+email+"\n"
		par = par+"#PBS -m ae\n"
	par = par+"#PBS -N lianne_"+ot+"Coverage\n\
#PBS -q workq\n\n"


	dr_cl = 'module load anaconda/3\n'
	dr_cl = dr_cl+'init bash\n'
	dr_cl = dr_cl+'source ~/.bashrc\n'
	dr_cl = dr_cl+'conda activate /data/hpc-data/shared/condaEnv/lianne\n'
	dr_cl = dr_cl+'cd '+out_localApp
	dr_cl = dr_cl+'\n'
	dr_cl = dr_cl+'\n'

	dr_sh = par+'\n\n'+dr_cl

	
	# write coverage sh
	
	coverage_file_run = os.path.join(out_localApp, ot+'Coverage_run.sh')

	# retrieve bam file path for coverage analysis
	if ot == 'snv':
		bamDir = os.path.join(out_localApp, 'Logs_Intermediates/StitchedRealigned')
	elif ot == 'cnv':
		bamDir = os.path.join(out_localApp, 'Logs_Intermediates/DnaRealignment')
	elif ot == 'rna':
		bamDir = os.path.join(out_localApp, 'Logs_Intermediates/RnaAlignment')
	else:
		print('[WARNING] bam file type not recognized for coverage')
		print('[WARNING] exit')
		os.sys.exit()
	bam_list = []
	for root, dirs, file in os.walk(bamDir):
		for f in file:
			if f.endswith('.bam'):
				bam_file = os.path.join(root, f)
				bam_list.append(bam_file)

	if debug is False:
		# build sh file
		sh = open(coverage_file_run, 'w')
		sh.write(dr_sh)
		for b in bam_list:
			sh.write('python3 '+COV_MODULE+' -i '+b+' -p '+ot+'\n')
		sh.close()
		jobid2 = subprocess.run(['qsub', coverage_file_run], stdout=subprocess.PIPE, universal_newlines=True)
	else:
		print('[DEBUG] coverage_run.sh file written in foder: ')
		print(coverage_file_run)
		print('[DEBUG] coverage_run.sh file contains:')
		print(dr_sh)
		for b in bam_list:
			print('python3 '+COV_MODULE+' -i '+b+' -p '+ot)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Launch script for coverage - Lianne module')

##################################################################################################

	# arguments
	parser.add_argument('-e', '--email', required=False,
						help='sh parameters built by Lianne',
						default = 'noEmail')
	parser.add_argument('-o', '--outLocalApp', required=True,
						help='Output folder of Local App')
	parser.add_argument('-d', '--debug', required=False,
						action='store_true',
						help='Run the script in debug mode\nNo jobs will be send\nNo file will be written - Default=False')
	parser.add_argument('-p', '--output_prefix', required=True,
						help="Prefix of output folder.\nSelections allowed: snv, rna, cnv",
						choices=['snv', 'rna', 'cnv'])

##################################################################################################

	args = parser.parse_args()
	email = args.email
	out_localApp = args.outLocalApp
	debug = args.debug
	ot = args.output_prefix

	main(email, out_localApp, debug, ot)

