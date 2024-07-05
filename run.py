#!/usr/bin/env python



EXAMPLE_DESCRIPTIVE_NAME = 'Simple carputils Example'


from datetime import date
import os
# import required carputils modules
from carputils import settings
from carputils import tools
from carputils import mesh
from carputils import testing

EXAMPLE_DIR = os.path.dirname(__file__)

# define parameters exposed to the user on the commandline
def parser():
    parser = tools.standard_parser()
    parser.add_argument('--tend',
                        type=float, default=20.,
                        help='Duration of simulation (ms). Run for longer to also see repolarization.')
    return parser

def jobID(args):
    """
    Generate name of top level output directory.
    """
    today = date.today()
    return '{}_simple_{}_{}_np{}'.format(today.isoformat(), args.tend,
                                         args.flv, args.np)

@tools.carpexample(parser, jobID)
def run(args, job):

    # Generate mesh, units in mm, centered around origin
    # By default, elements are tagged as "1". Can be changed by adding box or sphere regions
    # See carputils doxygen documentation for details

    # Generate and return base name
    meshname = "/home/diya/Documents/openCARP/external/experiments/tutorials/02_EP_tissue/00_simple/tetrahedralized"

    # Instead of generating a mesh, you could also load one using the 'meshname' openCARP
    # command. This requires .elem and .pts files that can be generated for VTK files using
    # meshtool 
    
    # Get basic command line, including solver options from external .par file
    #cmd = tools.carp_cmd(tools.carp_path(os.path.join(EXAMPLE_DIR, 'simple.par')))
    cmd = tools.carp_cmd(tools.simfile_path(os.path.join(EXAMPLE_DIR, 'simple.par')))
    
    # Attach electrophysiology physics (monodomain) to mesh region with tag 1
    cmd += tools.gen_physics_opts(IntraTags=[1])
        # Stimulus parameters
    stim = ['-num_stim', 1,
            '-stimulus[0].name', 'S1',
            '-stimulus[0].stimtype',1,
            '-stimulus[0].start', 0,
            '-stimulus[0].strength', -1500,
            '-stimulus[0].duration', 1,
            '-stimulus[0].region' , 0 ,
            '-stimulus[0].x0',-39.94,
            '-stimulus[0].x1',71.54,
            '-stimulus[0].y0', -84.36,
            '-stimulus[0].y1',13.15,
            '-stimulus[0].z0',-51.74,
            '-stimulus[0].x1',48.13
             
       ]
    cmd += stim

    cmd += ['-simID',    job.ID,
            '+smeshname', meshname,
            '-tend',     args.tend]

    # Set monodomain conductivities
    cmd += ['-num_gregions',			1,
    		'-gregion[0].name', 		"myocardium",
    		'-gregion[0].num_IDs', 	1,  		# one tag will be given in the next line
    		'-gregion[0].ID', 		"1",		# use these settings for the mesh region with tag 1
    		# mondomain conductivites will be calculated as half of the harmonic mean of intracellular
    		# and extracellular conductivities
    		'-gregion[0].g_el', 		0.625,	# extracellular conductivity in longitudinal direction
    		'-gregion[0].g_et', 		0.236,	# extracellular conductivity in transverse direction
    		'-gregion[0].g_en', 		0.236,	# extracellular conductivity in sheet direction
    		'-gregion[0].g_il', 		0.174,	# intracellular conductivity in longitudinal direction
    		'-gregion[0].g_it', 		0.019,	# intracellular conductivity in transverse direction
    		'-gregion[0].g_in', 		0.019,	# intracellular conductivity in sheet direction
    		'-gregion[0].g_mult',		0.5		# scale all conducitivites by a factor (to reduce conduction velocity)    		
    		]

    # Define the ionic model to use
    cmd += ['-num_imp_regions',          1,
            '-imp_region[0].im',         'Courtemanche',
            '-imp_region[0].num_IDs',    1,
            '-imp_region[0].ID[0]',      1     # use this setting for the mesh region with tag 1    
    ]

    # Add the stimulus definition
  
  # cmd += ['-num_stim', 1,
   #     '-stim[0].stimtype',1,       # Type 1 for a uniform/global stimulus
    #    '-stim[0].start', 0,          # Start time at 0 ms
     #   '-stim[0].duration',1,       # Duration of 1 ms
      #  '-stim[0].strength', -1500
       # ]
    


    # compute local activation times in postprocessing
    cmd += ['-num_LATs',           1,
           '-lats[0].ID',         'activation',
           '-lats[0].all',        0,	# only detect first activation
           '-lats[0].measurand',  0,	# determine LAT from transmembrane voltage
           '-lats[0].mode',       0,	# take maximum slope to detemine LAT
           '-lats[0].threshold', -10,	# -10mV threshold
           ]

    if args.visualize:
        cmd += ['-gridout_i', 3]	# output both surface & volumetric mesh for visualization

    # Run simulation
    job.carp(cmd)

    # Do visualization
    if args.visualize and not settings.platform.BATCH:

        # Prepare file paths
        geom = os.path.join(job.ID, os.path.basename(meshname)+'_i')
        # display transmembrane voltage
        data = os.path.join(job.ID, 'vm.igb.gz')
        # Alternatively, you could visualize the activation times instead
        # data = os.path.join(job.ID, 'init_acts_activation-thresh.dat')
        
        # load predefined visualization settings
        view = tools.simfile_path(os.path.join(EXAMPLE_DIR, 'simple.mshz'))

        # Call meshalyzer
        job.meshalyzer(geom, data, view)

if __name__ == '__main__':
    run()
    
