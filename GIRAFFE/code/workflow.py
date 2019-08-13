#This is a Nipype generator. Warning, here be dragons.
#!/usr/bin/env python

import sys
import nipype
import nipype.pipeline as pe

import nipype.interfaces.io as io
import nipype.interfaces.mrtrix3 as mrtrix3

#Generic datagrabber module that wraps around glob in an
io_data_grabber = pe.Node(io.DataGrabber(outfields=["outfiles"]), name = 'io_data_grabber')
io_data_grabber.inputs.sort_filelist = True
io_data_grabber.inputs.template = "/Users/bsms9gep/data/*.nii"

#Wraps the executable command ``mrconvert``.
mrtrix3_mrconvert = pe.Node(interface = mrtrix3.MRConvert(), name='mrtrix3_mrconvert')
mrtrix3_mrconvert.inputs.grad_fsl = ("/Users/bsms9gep/data/bvecs", "/Users/bsms9gep/data/bvals")

#Wraps the executable command ``dwi2mask``.
mrtrix3_brain_mask = pe.Node(interface = mrtrix3.BrainMask(), name='mrtrix3_brain_mask')

#Wraps the executable command ``dwibiascorrect``.
mrtrix3_dwibias_correct = pe.Node(interface = mrtrix3.DWIBiasCorrect(), name='mrtrix3_dwibias_correct')

#Wraps the executable command ``dwi2response``.
mrtrix3_response_sd = pe.Node(interface = mrtrix3.ResponseSD(), name='mrtrix3_response_sd')
mrtrix3_response_sd.inputs.algorithm = 'dhollander'

#Wraps the executable command ``dwi2fod``.
mrtrix3_estimate_fod = pe.Node(interface = mrtrix3.EstimateFOD(), name='mrtrix3_estimate_fod')
mrtrix3_estimate_fod.inputs.algorithm = 'msmt_csd'

#Generic datasink module to store structured outputs
io_data_sink = pe.Node(interface = io.DataSink(), name='io_data_sink')
io_data_sink.inputs.base_directory = "/Users/bsms9gep/results"

#Create a workflow to connect all those nodes
analysisflow = nipype.Workflow('MyWorkflow')
analysisflow.connect(io_data_grabber, "outfiles", mrtrix3_mrconvert, "in_file")
analysisflow.connect(mrtrix3_mrconvert, "out_file", mrtrix3_dwibias_correct, "in_file")
analysisflow.connect(mrtrix3_dwibias_correct, "out_file", mrtrix3_brain_mask, "in_file")
analysisflow.connect(mrtrix3_dwibias_correct, "out_file", mrtrix3_response_sd, "in_file")
analysisflow.connect(mrtrix3_response_sd, "wm_file", mrtrix3_estimate_fod, "wm_txt")
analysisflow.connect(mrtrix3_brain_mask, "out_file", mrtrix3_estimate_fod, "mask_file")
analysisflow.connect(mrtrix3_response_sd, "csf_file", mrtrix3_estimate_fod, "csf_txt")
analysisflow.connect(mrtrix3_response_sd, "gm_file", mrtrix3_estimate_fod, "gm_txt")
analysisflow.connect(mrtrix3_dwibias_correct, "out_file", mrtrix3_estimate_fod, "in_file")
analysisflow.connect(mrtrix3_estimate_fod, "wm_odf", io_data_sink, "odf")

#Run the workflow
plugin = 'MultiProc' #adjust your desired plugin here
plugin_args = {'n_procs': 1} #adjust to your number of cores
analysisflow.write_graph(graph2use='flat', format='png', simple_form=False)
analysisflow.run(plugin=plugin, plugin_args=plugin_args)
