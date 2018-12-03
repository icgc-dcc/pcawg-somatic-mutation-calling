#!/usr/bin/env python3

import os
import sys
import json
import yaml
import subprocess
import glob
import shutil


task_dict = json.loads(sys.argv[1])

task_input = task_dict['input']
dockstore_tool = task_input['dockstore_tool']

input_template = subprocess.check_output(["cwltool",
                                          "--make-template",
                                          dockstore_tool
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
cmd = "cwltool --non-strict --debug --outdir %s %s job.json" % (cwl_outdir, dockstore_tool)
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

tool_basename = os.path.basename(dockstore_tool)
if tool_basename == 'muse.cwl':
    output_file = os.path.join(os.getcwd(), cwl_outdir, 'muse.vcf')
    if os.path.isfile(output_file):
        output_dict['mutations'] = output_file[0]
    else:
        exit('MuSE failed to produce output for mutations')

elif tool_basename == 'sanger-caller.cwl':
    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.somatic.sv.tar.gz'))
    if len(output_file) >= 1:
        output_dict['somatic_sv_tar_gz'] = output_file[0]
    else:
        exit('Sanger caller failed to produce output for somatic_sv_tar_gz')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.somatic.snv_mnv.tar.gz'))
    if len(output_file) >= 1:
        output_dict['somatic_snv_mnv_tar_gz'] = output_file[0]
    else:
        exit('Sanger caller failed to produce output for somatic_snv_mnv_tar_gz')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.somatic.verifyBamId.tar.gz'))
    if len(output_file) >= 1:
        output_dict['somatic_verifyBamId_tar_gz'] = output_file[0]
    else:
        exit('Sanger caller failed to produce output for somatic_verifyBamId_tar_gz')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.somatic.indel.tar.gz'))
    if len(output_file) >= 1:
        output_dict['somatic_indel_tar_gz'] = output_file[0]
    else:
        exit('Sanger caller failed to produce output for somatic_indel_tar_gz')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.somatic.genotype.tar.gz'))
    if len(output_file) >= 1:
        output_dict['somatic_genotype_tar_gz'] = output_file[0]
    else:
        exit('Sanger caller failed to produce output for somatic_genotype_tar_gz')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.somatic.cnv.tar.gz'))
    if len(output_file) >= 1:
        output_dict['somatic_cnv_tar_gz'] = output_file[0]
    else:
        exit('Sanger caller failed to produce output for somatic_cnv_tar_gz')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.somatic.imputeCounts.tar.gz'))
    if len(output_file) >= 1:
        output_dict['somatic_imputeCounts_tar_gz'] = output_file[0]
    else:
        exit('Sanger caller failed to produce output for somatic_imputeCounts_tar_gz')

elif tool_basename == 'delly-sv.cwl':
    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.somatic.sv.vcf.gz'))
    if len(output_file) >= 1:
        output_dict['somatic_sv_vcf'] = output_file[0]
    else:
        exit('Delly SV caller failed to produce output for somatic_sv_vcf')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.sv.cov.plots.tar.gz'))
    if len(output_file) >= 1:
        output_dict['cov_plots'] = output_file[0]
    else:
        exit('Delly SV caller failed to produce output for cov_plots')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.sv.cov.tar.gz'))
    if len(output_file) >= 1:
        output_dict['cov'] = output_file[0]
    else:
        exit('Delly SV caller failed to produce output for cov')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.somatic.sv.bedpe.txt'))
    if len(output_file) >= 1:
        output_dict['somatic_bedpe'] = output_file[0]
    else:
        exit('Delly SV caller failed to produce output for somatic_bedpe')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.germline.sv.bedpe.txt'))
    if len(output_file) >= 1:
        output_dict['germline_bedpe'] = output_file[0]
    else:
        exit('Delly SV caller failed to produce output for germline_bedpe')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.sv.log.tar.gz'))
    if len(output_file) >= 1:
        output_dict['sv_log'] = output_file[0]
    else:
        exit('Delly SV caller failed to produce output for sv_log')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.sv.timing.json'))
    if len(output_file) >= 1:
        output_dict['sv_timing'] = output_file[0]
    else:
        exit('Delly SV caller failed to produce output for sv_timing')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.sv.qc.json'))
    if len(output_file) >= 1:
        output_dict['sv_qc'] = output_file[0]
    else:
        exit('Delly SV caller failed to produce output for sv_qc')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.germline.sv.vcf.gz'))
    if len(output_file) >= 1:
        output_dict['germline_sv_vcf'] = output_file[0]
    else:
        exit('Delly SV caller failed to produce output for germline_sv_vcf')

elif tool_basename == 'dkfz-caller.cwl':
    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.somatic.cnv.tar.gz'))
    if len(output_file) >= 1:
        output_dict['somatic_cnv_tar_gz'] = output_file[0]
    else:
        exit('DKFZ caller failed to produce output for somatic_cnv_tar_gz')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.somatic.cnv.vcf.gz'))
    if len(output_file) >= 1:
        output_dict['somatic_cnv_vcf_gz'] = output_file[0]
    else:
        exit('DKFZ caller failed to produce output for somatic_cnv_vcf_gz')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.germline.indel.vcf.gz'))
    if len(output_file) >= 1:
        output_dict['germline_indel_vcf_gz'] = output_file[0]
    else:
        exit('DKFZ caller failed to produce output for germline_indel_vcf_gz')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.somatic.indel.tar.gz'))
    if len(output_file) >= 1:
        output_dict['somatic_indel_tar_gz'] = output_file[0]
    else:
        exit('DKFZ caller failed to produce output for somatic_indel_tar_gz')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.somatic.indel.vcf.gz'))
    if len(output_file) >= 1:
        output_dict['somatic_indel_vcf_gz'] = output_file[0]
    else:
        exit('DKFZ caller failed to produce output for somatic_indel_vcf_gz')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.germline.snv_mnv.vcf.gz'))
    if len(output_file) >= 1:
        output_dict['germline_snv_mnv_vcf_gz'] = output_file[0]
    else:
        exit('DKFZ caller failed to produce output for germline_snv_mnv_vcf_gz')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.somatic.snv_mnv.tar.gz'))
    if len(output_file) >= 1:
        output_dict['somatic_snv_mnv_tar_gz'] = output_file[0]
    else:
        exit('DKFZ caller failed to produce output for somatic_snv_mnv_tar_gz')

    output_file = glob.glob(os.path.join(os.getcwd(), cwl_outdir, '*.somatic.snv_mnv.vcf.gz'))
    if len(output_file) >= 1:
        output_dict['somatic_snv_mnv_vcf_gz'] = output_file[0]
    else:
        exit('DKFZ caller failed to produce output for somatic_snv_mnv_vcf_gz')

else:
    exit('Unknown Dockstore tool: %s' % tool_basename)

with open('output.json', 'w') as f:
    f.write(json.dumps(output_dict, indent=2))
