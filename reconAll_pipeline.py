#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 14:03:16 2019

@author: Or Duek
Use the BIDS app for freesurfer to run recon-all on all sessions
This pipeline will iterate through subjects and send it to run.py after that will move it to final location
"""

# set variables
input_dir = '/media/Data/kpe_forFmriPrep' # this should be BIDS compatible
work_dir = '/media/Data/work'
freeSurfer_output = '/home/or/Documents/reconAll'# this should be on a home or something that's not CIFS/SAMBA

final_output =  '/media/Data/KPE_fmriPrep_preproc/reconOutput'

bids_app_location = '/home/or/freesurfer'


from nipype.interfaces.base import CommandLine
import nipype.pipeline.engine as pe
import nipype.interfaces.io as nio
from nipype.interfaces.utility import Function
import nipype.interfaces.utility as util  # utility
from nipype import Node, Workflow
import os


os.chdir(bids_app_location)

# take subject numbers and iterate
subject_list = ['008','1223','1253','1263','1293','1307','1315','1322','1339','1343','1351','1356','1364','1369','1387','1390','1403','1464', '1468', '1480', '1499', '1561']

infosource = pe.Node(util.IdentityInterface(fields=['subject_id'
                                            ],
                                    ),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]

# send the run.py command
def reconAll(subject_id):
    input_dir = '/media/Data/kpe_forFmriPrep'
    freeSurfer_output = '/home/or/Documents/reconAll'
    bids_app_location = '/home/or/freesurfer'
    cmd = bids_app_location + '/run.py ' + input_dir + ' ' + freeSurfer_output + ' participant --participant_label ' + subject_id + ' --skip_bids_validator --license_file /home/or/Downloads/freesurferLicense/license.txt --n_cpus 6'
    return cmd  

recon_cmd= pe.Node(name='recon_cmd',
               interface=Function(input_names=['subject_id'],
                                  output_names=['cmd'],
                                  function=reconAll))

runRecon = pe.Node(name="runRecon", interface=CommandLine(command='python'))

# take the output files and move them to final location on synology
#datasink = Node(nio.DataSink(base_directory=final_output),
#                                         name="datasink")

moveDat = pe.Node(interface=Function(input_names=['scr','dst'], 
                                     function = nio.copytree),
                                     name = "moveDat")

wfReconn = Workflow(name="reconAll", base_dir=work_dir)

wfReconn.connect([
        (infosource, recon_cmd, [('subject_id' , 'subject_id')]),
        (recon_cmd, runRecon, [('cmd', 'args')])
      
        ])


wfReconn.run()
