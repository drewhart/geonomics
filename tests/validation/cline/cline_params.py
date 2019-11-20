#cline_params.py
import numpy as np
from nlmpy import nlmpy

array_center_vals = np.array([*np.linspace(0.25, 0.75, 20)][::-1])
array_center_vals = 0.5+-0.5*np.sin(2*np.pi*array_center_vals)
array_vals = np.hstack(([1]*15, array_center_vals, [0]*15))
env_array = np.vstack([array_vals]*50)

K_array = np.ones((50,50))

#This is a default parameters file generated by Geonomics
#(by the gnx.params.make_parameters_file() function).


                      ## :: ::    :::            ##
                ##:::   :::::    :::   ::    :: :: :::##
             ## ::::     ::           ::   ::::::::::::::##
           ##::::::                       ::::::::: :::::: :##
         ## :    :::                    :::    ::    :::::::::##
        ##ggggg eeee ooo   n   n   ooo   m   m iiiii  cccc ssss##
       ##g     e    o   o  nn  n  o   o  m   m   i   c     s    ##
       ##g     eee o     o n n n o     o mm mm   i   c     sssss##
       ##g ggg eee o     o n  nn o     o m m m   i   c         s##
       ##g   g e    o   o  n   n  o   o  m   m   i   c        ss##
        ##gggg  eeee ooo   n   n   ooo   m   m iiiii  cccc ssss##
         ##  ::::::::        ::::::::::::  :       ::  ::   : ##
           ##  ::::              :::::::  ::     ::::::::  :##
             ## :::               :::::: ::       ::::::  ##
                ##:                ::::                ##
                      ##                         ##



params = {
###############################################################################

###################
#### LANDSCAPE ####
###################
    'landscape': {

    ##############
    #### main ####
    ##############
        'main': {
            #y,x (a.k.a. i,j) dimensions of the Landscape
            'dim':                      (50,50),
            #resolution of the Landscape
            'res':                      (1,1),
            #upper-left corner of the Landscape
            'ulc':                      (0,0),
            #projection of the Landscape
            'prj':                      None,
            }, # <END> 'main'

    ################
    #### layers ####
    ################
        'layers': {

            #layer name (LAYER NAMES MUST BE UNIQUE!)
            'layer_0': {

        #######################################
        #### layer num. 0: init parameters ####
        #######################################

                #initiating parameters for this layer
                'init': {

                    #parameters for a 'defined'-type Layer
                    'defined': {
                        #raster to use for the Layer
                        'rast':                 env_array,
                        #point coordinates
                        'pts':                  None,
                        #point values
                        'vals':                 None,
                        #interpolation method {None, 'linear', 'cubic',
                        #'nearest'}
                        'interp_method':        None,

                        }, # <END> 'defined'

                    }, # <END> 'init'

                }, # <END> layer num. 0


            #layer name (LAYER NAMES MUST BE UNIQUE!)
            'layer_1': {

        #######################################
        #### layer num. 1: init parameters ####
        #######################################

                #initiating parameters for this layer
                'init': {

                    #parameters for a 'defined'-type Layer
                    'defined': {
                        #raster to use for the Layer
                        'rast':                 K_array,
                        #point coordinates
                        'pts':                  None,
                        #point values
                        'vals':                 None,
                        #interpolation method {None, 'linear', 'cubic',
                        #'nearest'}
                        'interp_method':        None,

                        }, # <END> 'defined'

                    }, # <END> 'init'

                }, # <END> layer num. 1


    #### NOTE: Individual Layers' sections can be copy-and-pasted (and
    #### assigned distinct keys and names), to create additional Layers.


            } # <END> 'layers'

        }, # <END> 'landscape'


###############################################################################

###################
#### COMMUNITY ####
###################
    'comm': {

        'species': {

            #species name (SPECIES NAMES MUST BE UNIQUE!)
            'spp_0': {

            #####################################
            #### spp num. 0: init parameters ####
            #####################################

                'init': {
                    #starting number of individs
                    'N':                1000,
                    #carrying-capacity Layer name
                    'K_layer':          'layer_1',
                    #multiplicative factor for carrying-capacity layer
                    'K_factor':         0.5,
                    }, # <END> 'init'

            #######################################
            #### spp num. 0: mating parameters ####
            #######################################

                'mating'    : {
                    #age(s) at sexual maturity (if tuple, female first)
                    'repro_age':                0,
                    #whether to assign sexes
                    'sex':                      False,
                    #ratio of males to females
                    'sex_ratio':                1/1,
                    #whether P(birth) should be weighted by parental dist
                    'dist_weighted_birth':       False,
                    #intrinsic growth rate
                    'R':                        0.5,
                    #intrinsic birth rate (MUST BE 0<=b<=1)
                    'b':                        0.2,
                    #expectation of distr of n offspring per mating pair
                    'n_births_distr_lambda':    1,
                    #whether n births should be fixed at n_births_dist_lambda
                    'n_births_fixed':           True,
                    #radius of mate-search area
                    'mating_radius':            3,
                    }, # <END> 'mating'

            ##########################################
            #### spp num. 0: mortality parameters ####
            ##########################################

                'mortality'     : {
                    #maximum age
                    'max_age':                      None,
                    #min P(death) (MUST BE 0<=d_min<=1)
                    'd_min':                        0,
                    #max P(death) (MUST BE 0<=d_max<=1)
                    'd_max':                        1,
                    #width of window used to estimate local pop density
                    'density_grid_window_width':    None,
                    }, # <END> 'mortality'

            #########################################
            #### spp num. 0: movement parameters ####
            #########################################

                'movement': {
                    #whether or not the species is mobile
                    'move':                     True,
                    #mode of distr of movement direction
                    'direction_distr_mu':       1,
                    #concentration of distr of movement direction
                    'direction_distr_kappa':    0,
                    #mean of distr of movement distance
                    'distance_distr_mu':        0.5,
                    #variance of distr of movement distance
                    'distance_distr_sigma':     0.5,
                    #mean of distr of dispersal distance
                    'dispersal_distr_mu':       0.5,
                    #variance of distr of dispersal distance
                    'dispersal_distr_sigma':    0.5,
                    },    # <END> 'movement'


            #####################################################
            #### spp num. 0: genomic architecture parameters ####
            #####################################################

                'gen_arch': {
                    #file defining custom genomic arch
                    'gen_arch_file':            None,
                    #num of loci
                    'L':                        100,
                    #num of chromosomes
                    'l_c':                      [100],
                    #whether starting allele frequencies should be fixed at 0.5
                    'start_p_fixed':            True,
                    #genome-wide per-base neutral mut rate (0 to disable)
                    'mu_neut':                  0,
                    #genome-wide per-base deleterious mut rate (0 to disable)
                    'mu_delet':                 0,
                    #shape of distr of deleterious effect sizes
                    'delet_alpha_distr_shape':  0.2,
                    #scale of distr of deleterious effect sizes
                    'delet_alpha_distr_scale':  0.2,
                    #alpha of distr of recomb rates
                    'r_distr_alpha':            None,
                    #beta of distr of recomb rates
                    'r_distr_beta':             None,
                    #whether loci should be dominant (for allele '1')
                    'dom':                      False,
                    #whether to allow pleiotropy
                    'pleiotropy':               False,
                    #custom fn for drawing recomb rates
                    'recomb_rate_custom_fn':    None,
                    #number of recomb paths to hold in memory
                    'n_recomb_paths_mem':       int(1e4),
                    #total number of recomb paths to simulate
                    'n_recomb_paths_tot':       int(1e5),
                    'allow_ad_hoc_recomb':      True,
                    #whether to save mutation logs
                    'mut_log':                  False,

                    'traits': {

                        ###########################
                        ####trait 0 parameters ####
                        ###########################
                        #trait name (TRAIT NAMES MUST BE UNIQUE!)
                        'trait_0': {
                            #trait-selection Layer name
                            'layer':                'layer_0',
                            #polygenic selection coefficient
                            'phi':                  0.01,
                            #number of loci underlying trait
                            'n_loci':               1,
                            #mutation rate at loci underlying trait
                            'mu':                   0,
                            #mean of distr of effect sizes
                            'alpha_distr_mu' :      0.5,
                            #variance of distr of effect size
                            'alpha_distr_sigma':    0,
                            #max alpha value
                            'max_alpha_mag':        None,
                            #curvature of fitness function
                            'gamma':                1,
                            #whether the trait is universally advantageous
                            'univ_adv':             False
                            }, # <END> trait 0


    #### NOTE: Individual Traits' sections can be copy-and-pasted (and
    #### assigned distinct keys and names), to create additional Traits.


                        }, # <END> 'traits'

                    }, # <END> 'gen_arch'


                }, # <END> spp num. 0



    #### NOTE: individual Species' sections can be copy-and-pasted (and
    #### assigned distinct keys and names), to create additional Species.


            }, # <END> 'species'

        }, # <END> 'comm'


###############################################################################

###############
#### MODEL ####
###############
    'model': {
        #total Model runtime (in timesteps)
        'T':            1500,
        #min burn-in runtime (in timesteps)
        'burn_T':       60,
        #seed number
        'num':          None,

        ###############################
        #### iterations parameters ####
        ###############################
        'its': {
            #num iterations
            'n_its':            1,
            #whether to randomize Landscape each iteration
            'rand_landscape':   False,
            #whether to randomize Community each iteration
            'rand_comm':        False,
            #whether to burn in each iteration
            'repeat_burn':      True,
            }, # <END> 'iterations'


        ####################################
        #### data-collection parameters ####
        ####################################
        'data': {
            'sampling': {
                #sampling scheme {'all', 'random', 'point', 'transect'}
                'scheme':               'random',
                #sample size at each point, for point & transect sampling
                'n':                    801,
                #coords of collection points, for point sampling
                'points':               None,
                #coords of transect endpoints, for transect sampling
                'transect_endpoints':   None,
                #num points along transect, for transect sampling
                'n_transect_points':    None,
                #collection radius around points, for point & transect sampling
                'radius':               None,
                #when to collect data
                'when':                 0,
                #whether to save current Layers when data is collected
                'include_landscape':    False,
                #whether to include fixed loci in VCF files
                'include_fixed_sites':  False,
                },
            'format': {
                #format for genetic data {'vcf', 'fasta'}
                'gen_format':           ['vcf', 'fasta'],
                #format for vector geodata {'csv', 'shapefile', 'geojson'}
                'geo_vect_format':      'csv',
                #format for raster geodata {'geotiff', 'txt'}
                'geo_rast_format':      'geotiff',
                },
            }, #<END> 'data'

        #####################################
        #### stats-collection parameters ####
        #####################################
        'stats': {
            #mean fitness
            'mean_fit': {
                #whether to calculate
                'calc': True,
                #calculation frequency (in timesteps)
                'freq': 5,
                },
             }, # <END> 'stats'

        } # <END> 'model'

    } # <END> params
