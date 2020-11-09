#!/usr/bin/python
# _simult_select.py

# flake8: noqa

# geonomics imports
from geonomics.utils.viz import _check_display

# other imports
import os
import numpy as np
import matplotlib as mpl
_check_display()
import matplotlib.pyplot as plt
from matplotlib import gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
import time


# define a function to calculate the mean difference between phenotype
# and environment for a species
def calc_mean_z_e_diff(spp, trait_num=0):
    zs = spp._get_z()[:, trait_num].ravel()
    es = spp._get_e(lyr_num=spp.gen_arch.traits[trait_num].lyr_num)
    mean_diff = np.mean(np.abs(zs - es))
    return mean_diff


def _make_params():
    array_center_vals = np.array([*np.linspace(0.25, 0.75, 20)][::-1])
    array_center_vals = 0.5+-0.5*np.sin(2*np.pi*array_center_vals)
    array_vals = np.hstack(([1]*15, array_center_vals, [0]*15))
    env_array0 = np.vstack([array_vals]*50)
    env_array1= env_array0.T

    K_array = np.ones((50,50))

    #This is a default parameters file generated by Geonomics
    #(by the gnx.params.make_parameters_file() function).


                          ## :: ::    :::            ##
                    ##:::   :::::    :::   ::    :: :: :::##
                 ## ::::     ::           ::   ::::::::::::::##
               ##::::::                       ::::::::: :::::: :##
             ## :    :::                    :::    ::    :::::::::##
            ##GGGGG EEEE OOO   N   N   OOO   M   M IIIII  CCCC SSSS##
           ##G     E    O   O  NN  N  O   O  M   M   I   C     S    ##
           ##G     EEE O     O N N N O     O MM MM   I   C     SSSSS##
           ##G GGG EEE O     O N  NN O     O M M M   I   C         S##
           ##G   G E    O   O  N   N  O   O  M   M   I   C        SS##
            ##GGGG  EEEE OOO   N   N   OOO   M   M IIIII  CCCC SSSS##
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
                            'rast':                 env_array0,
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
                            'rast':                 env_array1,
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



                #layer name (LAYER NAMES MUST BE UNIQUE!)
                'layer_2': {

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

                    }, # <END> layer num. 2


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
                        'K_layer':          'layer_2',
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
                        #intrinsic growth rate
                        'R':                        0.5,
                        #intrinsic birth rate (MUST BE 0<=b<=1)
                        'b':                        0.5,
                        #expectation of distr of n offspring per mating pair
                        'n_births_distr_lambda':    1,
                        #whether n births should be fixed at n_births_dist_lambda
                        'n_births_fixed':           True,
                        #radius of mate-search area
                        'mating_radius':            3,
                        'choose_nearest_mate':      False,
                        'inverse_dist_mating':      False,
                        }, # <END> 'mating'

                ##########################################
                #### spp num. 0: mortality parameters ####
                ##########################################

                    'mortality'     : {
                        #maximum age
                        'max_age':                      5,
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
                        'movement_distance_distr_param1':        0.5,
                        #variance of distr of movement distance
                        'movement_distance_distr_param2':     0.5,
                        'movement_distance_distr':          'wald',
                        #mean of distr of dispersal distance
                        'dispersal_distance_distr_param1':       0.5,
                        #variance of distr of dispersal distance
                        'dispersal_distance_distr_param2':    0.5,
                        'dispersal_distance_distr':     'wald',
                        },    # <END> 'movement'


                #####################################################
                #### spp num. 0: genomic architecture parameters ####
                #####################################################

                    'gen_arch': {
                        #file defining custom genomic arch
                        'gen_arch_file':            None,
                        #num of loci
                        'L':                        1000,
                        #num of chromosomes
                        'l_c':                      [1000],
                        #whether starting allele frequencies should be fixed at 0.5
                        'start_p_fixed':            0.5,
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
                        'n_recomb_sims':            10000,
                        'start_neut_zero':          False,
                        'allow_ad_hoc_recomb':      False,
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
                                'phi':                  0.05,
                                #number of loci underlying trait
                                'n_loci':               10,
                                #mutation rate at loci underlying trait
                                'mu':                   0,
                                #mean of distr of effect sizes
                                'alpha_distr_mu' :      0.1,
                                #variance of distr of effect size
                                'alpha_distr_sigma':    0,
                                #max alpha value
                                'max_alpha_mag':        None,
                                #curvature of fitness function
                                'gamma':                1,
                                #whether the trait is universally advantageous
                                'univ_adv':             False
                                }, # <END> trait 0

                            ###########################
                            ####trait 1 parameters ####
                            ###########################
                            #trait name (TRAIT NAMES MUST BE UNIQUE!)
                            'trait_1': {
                                #trait-selection Layer name
                                'layer':                'layer_1',
                                #polygenic selection coefficient
                                'phi':                  0.05,
                                #number of loci underlying trait
                                'n_loci':               10,
                                #mutation rate at loci underlying trait
                                'mu':                   0,
                                #mean of distr of effect sizes
                                'alpha_distr_mu' :      0.1,
                                #variance of distr of effect size
                                'alpha_distr_sigma':    0,
                                #max alpha value
                                'max_alpha_mag':        None,
                                #curvature of fitness function
                                'gamma':                1,
                                #whether the trait is universally advantageous
                                'univ_adv':             False
                                }, # <END> trait 1

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
            'T':            1000,
            #min burn-in runtime (in timesteps)
            'burn_T':       60,
            #seed number
            'num':          None,
            #time step interval for simplification of tskit tables
            'tskit_simp_interval':      100,

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

    return params


def _run(params, save_figs=False, time_it=False):

    # create data structure to store z-e diffs for both traits
    z_e_diffs = {0: [], 1: []}

    # start timer
    if time_it:
        start = time.time()

    # set model name (since not being read in from separate params file)
    params.model['name'] = 'simult_select_demo'

    # make the model
    from .. import make_model
    mod = make_model(params)

    # get total runtime from params
    T = mod.params.model.T

    # run model
    mod.walk(T=10000, mode='burn', verbose=True)
    for t in range(T):
        if not time_it:
            for trt_num in range(len(mod.comm[0].gen_arch.traits)):
                z_e_diffs[trt_num].append(calc_mean_z_e_diff(mod.comm[0],
                                                             trait_num=trt_num))
        mod.walk(T=1, mode='main', verbose=True)
    if not time_it:
        for trt_num in range(len(mod.comm[0].gen_arch.traits)):
            z_e_diffs[trt_num].append(calc_mean_z_e_diff(mod.comm[0],
                                                         trait_num=trt_num))

    # stop timer
    if time_it:
        stop = time.time()
        tot_time = stop - start

    # plot the resulting species on top of each layer
    fig = plt.figure(figsize=(15, 10))
    fig.tight_layout()
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])
    im = plt.pcolormesh(np.linspace(0, mod.land.dim[0], mod.land.dim[0]+1),
                        np.linspace(0, mod.land.dim[1], mod.land.dim[1]+1),
                        mod.land[0].rast, cmap='coolwarm')
    ax1 = plt.subplot(gs[0])
    mod.plot_phenotype(0, 0, 0, size=85)
    divider = make_axes_locatable(ax1)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = plt.colorbar(im, cax=cax)
    cbar.set_label('environmental and phenotypic value', rotation=270,
                   labelpad=25, y=0.5, size=15)
    ax2 = plt.subplot(gs[1])
    im = plt.pcolormesh(np.linspace(0, mod.land.dim[0], mod.land.dim[0]+1),
                        np.linspace(0, mod.land.dim[1], mod.land.dim[1]+1),
                        mod.land[1].rast, cmap='BrBG_r')
    mod.plot_phenotype(0, 1, 1, size=85)
    divider = make_axes_locatable(ax2)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = plt.colorbar(im, cax=cax)
    cbar.set_label('environmental and phenotypic value', rotation=270,
                   labelpad=25, y=0.5, size=15)
    ax1.set_title('trait 0', size=20)
    ax2.set_title('trait 1', size=20)
    plt.show()

    # print out time
    if time_it:
        print("Model ran in %0.2f seconds." % tot_time)

    # save the figure
    if save_figs:
        plt.savefig('sim_sel.pdf', format='png', dpi=1000)


    # plot z-e diffs
    z_e_fig = plt.figure()
    ax = z_e_fig.add_subplot(111)
    trt_colors = ['#096075', '#e87d4f']
    plt.plot(range(len(z_e_diffs[0])), z_e_diffs[0], trt_colors[0])
    plt.plot(range(len(z_e_diffs[1])), z_e_diffs[1], trt_colors[1])
    ax.legend(labels=['trait = %i' % trt for trt in range(2)],
              loc='best', fontsize='medium')
    ax.set_xlabel('time')
    ax.set_ylabel(('mean difference between individuals\'\nphenotypes and '
                   'environmental values'), size=12)
    plt.show()
    if save_figs:
        plt.savefig('sim_sel_z-e_plot.png', format='png', dpi=1000)

    return mod


