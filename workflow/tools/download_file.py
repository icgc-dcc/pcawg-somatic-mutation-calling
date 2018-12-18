#!/usr/bin/env python3

import sys
import json
import subprocess
import os
import shutil

task_dict = json.loads(sys.argv[1])
task_input = task_dict['input']
file_name = task_input.get('file_name')

output_file = file_name

if str(file_name).startswith('song://'):
    object_id = str(file_name).split('/')[4]
    profile = str(file_name).split('/')[2]

    outdir = os.path.join(os.getcwd(),'outdir')
    if os.path.exists(outdir):  # remove  if exist
        shutil.rmtree(outdir)

    os.makedirs(outdir)

    score_container = "overture/score:1.5.0"
    subprocess.check_output(['docker', 'pull', score_container])
    subprocess.check_output(['docker','run','-it',
                             '-e','ACCESSTOKEN',
                             'overture/score',
                             'download',
                             '--profile'+profile,
                             '--object-id'+object_id,
                             '--output-dir',outdir])

    for f in os.listdir(outdir):
        if f.endswith('.bam'):
            output_file = os.path.join(outdir,f)
        else:
            output_file = None


with open('output.json', 'w') as f:
    f.write(json.dumps({'file_path':output_file}, indent=2))
