#!/usr/bin/env python3

import os
import re
import sys
import json
import yaml
import subprocess


task_dict = json.loads(sys.argv[1])

cwl_source = task_dict['cwl_source']
cwl_entry = task_dict['cwl_entry']

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

exit({
        "task_dict": task_dict,
        "input_json_template": input_json
    })
