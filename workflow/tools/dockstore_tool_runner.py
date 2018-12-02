#!/usr/bin/env python3

import sys
import json
import yaml
import subprocess


task_dict = json.loads(sys.argv[1])

task_input = task_dict['input']
dockstore_tool = task_input['dockstore_tool']

input_template = subprocess.check_output(["cwltool",
                                          "--make-template",
                                          dockstore_tool
                                          ])

input_json = yaml.load(input_template)

output_dict = {
                "task_dict": task_dict,
                "input_json_template": input_json
              }

with open('output.json', 'w') as f:
    f.write(json.dumps(output_dict, indent=2))
