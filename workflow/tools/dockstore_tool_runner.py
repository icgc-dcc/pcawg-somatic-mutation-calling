#!/usr/bin/env python3

import json
import yaml
import subprocess


task_dict = json.loads(sys.argv[1])

input_template = subprocess.check_output(["cwltool",
                                          "--make-template",
                                          task_dict.get("dockstore_tool")
                                          ])

input_json = yaml.load(input_template)

exit({
        "task_dict": task_dict,
        "input_json_template": input_json
    })
