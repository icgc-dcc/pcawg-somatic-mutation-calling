#!/usr/bin/env python3

import os
import re
import sys
import json
import yaml
import subprocess
import shutil


task_dict = json.loads(sys.argv[1])
task_input = task_dict['input']

cwl_source = task_input['cwl_source']
cwl_entry = task_input['cwl_entry']

m = re.match('(.+\/.+\/(.+)):(.+)', cwl_source)

if m:
    git_url = 'https://%s' % m.group(1)
    repo_name = m.group(2)
    release_tag = m.group(3)
else:
    exit('CWL source Git repo incorrect: %s' % cwl_source)

# maybe git pull submodules as well?
command = 'rm -fr %s && git clone %s && cd %s && git checkout %s' % \
            (repo_name, git_url, repo_name, release_tag)

subprocess.call(command, shell=True)

input_template = subprocess.check_output(["cwltool",
                                          "--make-template",
                                          os.path.join(repo_name, cwl_entry)
                                          ])

input_json = yaml.load(input_template)

for i in input_json:
    if i == 'run-id':
        input_json[i] = 'run-id'
    elif isinstance(input_json[i], str):
        input_json[i] = task_input[i]
    elif input_json[i] is None and isinstance(task_input[i], str):
        input_json[i] = task_input[i]
    # cwltool make-template does not do good job with 'null' in template
    elif input_json[i] is None and \
            isinstance(task_input[i], list) and \
            len(task_input[i]) > 0 and \
            task_input[i][0].startswith('/'):  # a bit hacky here, assume it's a local file
        input_json[i] = []
        for f in task_input[i]:
            input_json[i].append(
                    {
                        'class': 'File',
                        'path': f
                    }
                )
    elif isinstance(input_json[i], dict) and input_json[i].get('class') == 'File':
        input_json[i]['path'] = task_input[i]
    else:
        exit('Required input not provided: %s' % i)

# write out the Job JSON for CWL tool
with open('job.json', 'w') as f:
    f.write(json.dumps(input_json, indent=2))

cwl_outdir = 'outdir'
if os.path.exists(cwl_outdir):  # remove  if exist
    shutil.rmtree(cwl_outdir)

os.makedirs(cwl_outdir)

# launch cwltool
cmd = "cwltool --non-strict --debug --outdir %s %s job.json" % \
        (cwl_outdir, os.path.join(repo_name, cwl_entry))
p = subprocess.Popen(
                        [cmd],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True
                    )

stdout, stderr = p.communicate()

if p.returncode != 0:  # cwltool run failed
    print(stdout)
    print(stderr, file=sys.stderr)
    exit(p.returncode)

# output json is a bit tricky as we don't know expected output parameters for
# each of the cwl tools, we are going to hardcode for each tool for now

output_dict = dict()

if repo_name == 'pcawg-gatk-cocleaning':
    for bamtype in ['normal', 'tumor']:
        # get the basename of the input normal/tumor bams
        bambase = os.path.basename(input_json[bamtype+'_bam']['path']).replace('.bam', '')
        output_file = os.path.join(os.getcwd(), cwl_outdir, bambase+'.realigned.cleaned.bam')
        if os.path.isfile(output_file):
            output_dict['cleaned_'+bamtype+'_bam'] = output_file
        else:
            exit('BQSR CoCleaning failed to produce output for cleaned_%s_bam!' % bamtype)

else:
    exit('Unknown workflow from git repo: %s' % repo_name)

with open('output.json', 'w') as f:
    f.write(json.dumps(output_dict, indent=2))
