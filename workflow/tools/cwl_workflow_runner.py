#!/usr/bin/env python3

import os
import re
import sys
import json
import yaml
import subprocess


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

command = 'git clone %s; cd %s; git checkout %s' % (git_url, repo_name, release_tag)

subprocess.call(command, shell=True)

input_template = subprocess.check_output(["cwltool",
                                          "--make-template",
                                          os.path.join(repo_name, cwl_entry)
                                          ])

input_json = yaml.load(input_template)

output_dict = {
                "task_dict": task_dict,
                "input_json_template": input_json
              }

with open('output.json', 'w') as f:
    f.write(json.dumps(output_dict, indent=2))
