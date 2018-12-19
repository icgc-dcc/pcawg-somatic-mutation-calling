#!/usr/bin/env python3

import sys
import json
import subprocess
import os
import shutil

task_dict = json.loads(sys.argv[1])
task_input = task_dict['input']
file_path = task_input.get('file_path')

output_file = file_path

if str(file_path).startswith('song://'):
    object_id = str(file_path).split('/')[4]
    profile = str(file_path).split('/')[2]

    if not profile in ['collab','aws']: raise Exception("Provide a profile in collab or aws. %s" % (profile))

    outdir = os.path.join(os.getcwd(),'outdir')

    os.makedirs(outdir, exist_ok=True)

    score_container = "overture/score:1.5.0"
    subprocess.check_output(['docker','run',
                             '-e','ACCESSTOKEN',
                             score_container,
                             'bin/score-client',
                             '--profile', profile,
                             'download',
                             '--object-id', object_id,
                             '--output-dir', outdir])

    for f in os.listdir(outdir):
        if f.endswith('.bam'):
            output_file = os.path.join(outdir,f)
            break

if not (output_file.endswith('.bam') and os.path.isfile(output_file)):
    exit('Input BAM not ready!')

with open('output.json', 'w') as f:
    f.write(json.dumps({'file_path':output_file}, indent=2))
