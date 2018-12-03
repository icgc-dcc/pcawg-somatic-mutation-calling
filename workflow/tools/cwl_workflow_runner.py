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
    elif input_json[i] is None or isinstance(input_json[i], str):
        input_json[i] = task_input[i]
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
    output_file = os.path.join(os.getcwd(), cwl_outdir, 'printreads_tumor/output/*.cleaned.bam')
    if os.path.isfile(output_file):
        output_dict['cleaned_tumor_bam'] = output_file[0]
    else:
        exit('BQSR CoCleaning failed to produce output for cleaned_tumor_bam!')

    output_file = os.path.join(os.getcwd(), cwl_outdir, 'printreads_normal/output/*.cleaned.bam')
    if os.path.isfile(output_file):
        output_dict['cleaned_normal_bam'] = output_file[0]
    else:
        exit('BQSR CoCleaning failed to produce output for cleaned_normal_bam!')

else:
    exit('Unknown workflow from git repo: %s' % repo_name)

with open('output.json', 'w') as f:
    f.write(json.dumps(output_dict, indent=2))
