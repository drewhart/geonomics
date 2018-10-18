#!/usr/bin/python
# main.py

'''
##########################################

Module name:          main


Module contains:
                      - the Geonomics main module, containing the key,
                        highest-level functions the common user would need


Author:               Drew Ellison Hart
Email:                drew.hart@berkeley.edu
Github:               URL
Start date:           07-06-18
Documentation:        URL


##########################################
'''

#geonomics imports
from sim import model
from sim import params as par
from structs import landscape, genome, individual, population, community

#other imports
import re
import os, sys, traceback
from collections import Counter as C
import numpy as np
import pandas as pd

######################################
# -----------------------------------#
# CLASSES ---------------------------#
# -----------------------------------#
######################################


######################################
# -----------------------------------#
# FUNCTIONS -------------------------#
# -----------------------------------#
######################################

#wrapper around params.make_parameters_file
#TODO
def make_parameters_file(filepath=None, layers=1, populations=1, data=None,
                         stats=None, seed=None):
    """
    Create a new parameters file.

    Write to disk a new, template parameters file. The file will contain the
    numbers and types of sections indicated by the parameters fed to this
    function. It can often be used 'out of the box' to make a new Model
    object, but typically it will be edited by the user to stipulate
    the scenario being simulated, then used to instantiate a Model.

    Parameters
    ----------
    filepath : str, optional
        Where to write the resulting parameters file, in /path/to/filename.py
        format. Defaults to None. If None, a file named
        "GEONOMICS_params_<datetime>.py" will be written to the working
        directory.
    layers : {int, list of dicts}, optional
        Number (and optionally, types) of Layer-parameter sections to include
        in the parameters file that is generated. Defaults to 1. Valid values
        and their associated behaviors are:

        int:
            Add sections for the stipulated number of Layers, each with default
            settings:
                - parameters for creating Layers of type 'random' (i.e.
                  Layers that will be generated by interpolation from
                  randomly valued random points)
                - no LandscapeChanger parameters
        [dict, ..., dict]:
            Each dict in this list should be of the form:
                {'type':    'random', 'defined', 'file', or 'nlmpy',
                'change':   bool
                }
            This will add one section of Layer parameters, with the
            contents indicated, for each dict in this list.
    populations : {int, list of dicts}, optional
        Number (and optionally, types) of Population-parameter sections to
        include in the parameters file that is generated. Defaults to 1. Valid
        values and their associated behaviors are:

        int:
            Add sections for the stipulated number of Populations, each with
            default settings:
                - parameters for movement without a MovementSurface
                - parameters for a GenomicArchitecture with 0 Traits (i.e. with
                  only neutral loci)
                - no _PopulationChanger parameters
        [dict, ..., dict]:
            Each dict should contain at least one argument from among the
            following:
                {'movement':                       bool,
                'movement_surface':                bool,
                'genomes':                         bool,
                'n_traits':                        int,
                'custom_genomic_architecture':     bool,
                'demographic_change':              int,
                'parameter_change':                bool
                }
            This will add one section of Population parameters, customized
            as indicated, for each dict in the list.

    data : bool, optional
        Whether to include a Data-parameter section in the parameters file that
        is generated. Defaults to None. Valid values and their associated
        behaviors are:

        None, False:
            Will not add a section for parameterizing data to be collected.
            No _DataCollector will be created for the Model object made from
            the resulting parameters file, and no data will be collected
            during the model runs.
        True:
            Will add a section that can be used to parameterize which
            data will be collected during the model runs, when, and what
            file formats will be used to write it to disk.
            (This which will be managed by the model's _DataCollector
            object.)

    stats : bool, optional
        Whether to include a Stats-parameter section in the parameters file that
        is generated. Defaults to None. Valid values and their associated
        behaviors are:

        None, False:
            Will not add a section for parameterizing the statistics to be
            calculated. No _StatsCollector will be created for the Model
            object made from the resulting parameters file, and no
            statistics will be calculated during the model runs.
        True:
            Will add a section that can be used to parameterize which
            statistics will be calculated during the model runs, and when.
            (This will be managed by the model's _StatsCollector object.)

    seed : bool, optional
        Whether to include a seed-parameter section in the parameters file that
        is generated. Defaults to None. Valid values and their associated
        behaviors are:

        None, False:
            Will not add a section for parameterizing how the random number
            generators are seeded, hence generators will be seeded at
            random and results will be unreproducible.
        True:
            Will add a section for parameterizing how the random number
            generators are seeded, so that results will be reproducible.

    Returns
    -------
    out : None
        Returns no output. Resulting parameters file will be written to the
        location and filename indicated (or by default, will be written to a
        file named "GEONOMICS_params_<datetime>.py" in the working directory).

    See Also
    --------
    sim.params.make_parameters_file

    Notes
    -----
    All parameters of this function are optional. Calling the function without
    providing any parameters will always produce the parameters file for the
    default model scenario. This file can be instantiated as a Model object and
    run without being edited. Those three steps (create default parameters file;
    create model from that parameters file; run the model) serve as a base case
    to test successful package installation, and are wrapped around by the
    convenience function `gnx.run_default_model`.

    Examples
    --------
    In the simplest example, we can create a parameters file for the default
    model. Then (assuming it is the only Geonomics parameters file in the
    current working directory, so that it can be unambiguously identified) we
    can call the gnx.make_model function to create a Model object from that
    file, and then call the Model.run method to run the model (setting the
    'verbose' parameter to True, so that we can observe model output).

    >>> gnx.make_parameters_file()
    >>> mod = gnx.make_model()
    >>> mod.run(verbose = True)
    TODO: PUT TYPICAL MODEL OUTPUT HERE, EVEN THOUGH IT'S ONLY PRINTED?

    We can use some of the function's arguments, to create a parameters
    file for a model with 3 Layers and 1 Population (all with the default
    components for their sections of the parameters file) and with a section
    for parameterizing data collection.

    >>> gnx.make_parameters_file(layers = 3, data = True)

    As a more complex example that is likely to be similar to most use cases,
    we can create a parameters file for a model scenario with:
        - 2 Layers (one being an nlmpy Layer that will not change over model
          time, the other being a raster read in from a GIS file and being
          subject to change over model time);
        - 2 Populations (the first having genomes, 2 Traits, and movement
          that is dictated by a MovementSurface; the second not having
          genomes but having a MovementSurface as well, and undergoing
          demographic change)
        - data-collection;
        - stats-collection;
        - a section for setting the seed for the random-number generators.
    We can save this to a file named "2-pop_2-trait_model.py" in our current
    working directory.

    >>> gnx.make_parameters_file(
    >>>     #list of 2 dicts, each containing the values for each Layer's
    >>>     #parameters section
    >>>     layers = [
    >>>         {'type': 'nlmpy'},                              #layer 1 
    >>>         {'type': 'gis',                                 #layer 2 
    >>>          'change': True}
    >>>         ],
    >>>     #list of 2 dicts, each containing the values for each Population's
    >>>     #parameters section
    >>>     populations = [
    >>>         {'genomes': True,                               #pop 1
    >>>          'n_traits': 2,
    >>>          'movement': True,
    >>>          'movement_surface': True},
    >>>         {'genomes': False,                              #pop 2
    >>>          'movement': True,
    >>>          'movement_surface': True,
    >>>          'demographic_change': True}
    >>>         ],
    >>>     #arguments to the data, stats,and seed parameters
    >>>     data = True, stats = True, seed = True,
    >>>     #destination to which to write the resulting parameter file
    >>>     filepath = '2-pop_2-trait_model.py')

    """

    par._make_parameters_file(filepath = filepath, layers = layers,
                                populations = populations, data = data,
                                stats = stats, seed = seed)


#wrapper around params.read
def read_parameters_file(filepath):
    """
    Create a new ParametersDict object.

    Read the Geonomics parameters file saved at the location indicated by
    'filepath', check its validity (i.e. that all the Layers and Populations
    parameterized in that file have been given distinct names), then use the
    file to instantiate a ParametersDict object.

    Parameters
    ----------
    filepath : str
        String indicating the location of the Geonomics parameters file that
        should be made into a ParametersDict object.

    Returns
    -------

    An object of the ParametersDict class (a dict of nested dicts, all
    of which have key-value pairs whose values can be accessed using typical
    dict notation or using dot notation with the keys).

    Raises
    ------
    AssertionError
        If either the Layers or the Populations parameterized in the parameters
        file have not all been given distinct names

    See Also
    --------
    sim.params.read
    sim.params.ParametersDict

    Examples
    --------
    Read a parameters file called "null_model.py" (located in the current
    working directory).

    >>> gnx.read_parameters_file('null_model.py')
    <class 'sim.params.ParametersDict'>
    Model name:                                     GEONOMICS_params_13-10-2018_15:54:03

    """

    #first read in file as a block of text
    with open(filepath, 'r') as f:
        txt = f.read()
    #find all the layer names and pop names
    lyr_names = re.findall('\S+(?=: \{\n\n\s+#*\n\s+#### layer num\.)', txt)
    lyr_names = [re.sub("'", '"', n) for n in lyr_names]
    pop_names = re.findall('\S+(?=: \{\n\n\s+#*\n\s+#### pop num\.)', txt)
    pop_names = [re.sub("'", '"', n) for n in pop_names]
    #get Counter objects of each
    lyr_name_cts = C(lyr_names)
    pop_name_cts = C(pop_names)
    #assert that each layer name is used only once
    assert set([*lyr_name_cts.values()]) == {1}, ("At least one of the "
        "Layer names provided in the parameters file appears to be used more "
        "than once. Violating names include: %s") % (';'.join([( "'%s', "
        "used %i times.") % (str(k),
                            v) for k, v in lyr_name_cts.items() if v>1]))
    #assert that each pop name is used only once
    assert set([*pop_name_cts.values()]) == {1}, ("At least one of the "
        "Population names provided in the parameters file appears to be used "
        "more than once. Violating names include: %s") % (';'.join([("'%s', "
            "used %i times.") % (
                str(k), v) for k, v in pop_name_cts.items() if v>1]))

    #break the file into sections for each population, then check that
    #trait names are only used once within each pop
    pop_sects = re.split('#pop name', txt)
    for sect in pop_sects:
        trt_names = re.findall('\S+(?=: \{\n\s+#trait-selection)', sect)
        if len(trt_names) > 0:
            trt_names = [re.sub("'", '"', n) for n in trt_names]
            trt_name_cts = C(trt_names)
            sect_pop_name = re.findall(
                        '\S+(?=: \{\n\n\s+#*\n\s+#### pop num\.)', txt)[0]
            assert set([*trt_name_cts.values()]) == {1}, ("At least one of the"
                " Trait names provided in the parameters for Population "
                "%s appears to be used more than once. "
                "Violating names include: %s") % (sect_pop_name,
                ';'.join([("'%s', used %i times.") % (str(k),
                v) for k, v in trt_name_cts.items() if v>1]))



    #now read the file in as a ParametersDict object
    params = par._read(filepath)
    return(params)


#function to create a model from a ParametersDict object
def make_model(parameters=None):
    """
    Create a new Model object.

    Use either a ParametersDict object or the path to a valid Geonomics
    parameters file (whichever is provided to the 'parameters' argument) to
    create a new Model object.

    Parameters
    ----------
    parameters : {ParametersDict, str}, optional
        The parameters to be used to make the Model object.
        If `parameters` is a ParametersDict object, the object will be used to
        make the Model.
        If `parameters` is a string, Geonomics will call
        `gnx.read_parameters_file` to make a ParametersDict object, then use
        that object to make the Model.
        If `parameters` is None, or is not provided, then Geonomics will
        attempt to find a single parameters file in the current working
        directory with the filename "GEONOMICS_params_<...>.py", will use that
        file to make a ParametersDict object, then will use that object to
        make the Model.

    Returns
    -------
    out : Model
        An object of the Model class

    Raises
    ------
    ValueError
        If the `parameters` argument was not provided and a single, valid
        Geonomics parameters file could not be identified in the current
        working directory
    ValueError
        If the `parameters` arugment was given a string that does not point
        to a valid parameters file
    ValueError
        If the ParametersDict provided to the `parameters` argument, or created
        from the parameters file being used, cannot be successfully made into a
        Model

    See Also
    --------
    gnx.read_parameters_file
    sim.model.Model

    Examples
    --------
    Make a Model from a single, valid "GEONOMICS_params_<...>.py" file that can
    be found in the current working directory (such as a file that would be
    produced by calling gnx.make_parameters_file without any arguments).

    >>> gnx.make_model()
    <class 'sim.model.Model'>
    Model name:                                     GEONOMICS_params_13-10-2018_15:54:03
    Layers:                                         0: '0'
    Populations:                                    0: '0'
    Number of iterations:                           1
    Number of burn-in timesteps (minimum):          30
    Number of main timesteps:                       100
    Geo-data collected:                             {}
    Gen-data collected:                             {}
    Stats collected:                                {}


    Make a Model from a file called 'null_model.py', in the current working
    directory.

    >>> gnx.make_model('null_model.py')
    <class 'sim.model.Model'>
    Model name:                                     null_model
    Layers:                                         0: 'tmp'
                                                    1: 'ppt'
    Populations:                                    0: 'C. fasciata'
    Number of iterations:                           2500
    Number of burn-in timesteps (mininum):          100
    Number of main timesteps:                       1000
    Geo-data collected:                             {csv, geotiff}
    Gen-data collected:                             {vcf, fasta}
    Stats collected:                                {maf, ld, mean_fit, het, Nt}

    """

    if parameters is None:
        try:
            params_files = [f for f in os.listdir('.') if (
                f.startswith('GEONOMICS_params_')
                and os.path.splitext(f)[1] == '.py')]
            assert len(params_files) == 1, ("The 'parameters' argument was not"
                " provided, and it appears that the current working directory "
                "contains more than one 'GEONOMICS_params_<...>.py' file. "
                "Please run again, providing a valid value for the "
                "'parameters' argument.")
            parameters = params_files[0]
            print(("\n\nUsing the following file, in the current working "
              "directory to create the Model object:\n\t%s\n\n") % parameters)
        except Exception as e:
            raise ValueError(("The 'parameters' argument was not provided, "
                "and Geonomics could not identify a single "
                "'GEONOMICS_params_<...>.py' file in the current working "
                "directory from which to create the Model object. The "
                "following error was thrown: %s") % e)

    assert ( (type(parameters) is str and os.path.isfile(parameters))
        or str(type(parameters)) == "<class 'sim.params.ParametersDict'>"),(
        "If the 'parameters' argument is provided, its value must be either a "
        "string pointing to a valid Geonomics parameters file or an object of "
        "the ParametersDict class. If it is not provided, the current working "
        "directory must contain a single 'GEONOMICS_params_<...>.py' file "
        "from which to create the Model object.")

    if type(parameters) is str:
        try:
            parameters = read_parameters_file(parameters)
        except Exception as e:
            print(("Failed to read the parameters file at the "
                "filepath that was provided. The following error was raised: "
                "\n\t%s\n\n") % e)
            print('Traceback:')
            traceback.print_exc(file = sys.stdout)
            raise ValueError()
    elif str(type(parameters)) == "<class '__main__.Parameters_Dict'>":
        pass
    try:
        name = parameters.model.name
        mod = model.Model(name, parameters)
        return(mod)
    except Exception as e:
            print(("Failed to create a Model object from the "
                "ParametersDict object being used. "
                "The following error was raised: \n\t%s\n\n") % e)
            print('Traceback:')
            traceback.print_exc(file = sys.stdout)
            raise ValueError()


#convenience function for creating a parameters-file for, instantiating, and
#running the default model
def run_default_model():
    #get filenames before creating the default params file
    filenames = set(os.listdir('.'))
    #make the default params file
    make_parameters_file()
    #get filenames after creating the default params file
    new_filenames = set(os.listdir('.'))
    #take set-difference to get the new file (better than just calling
    #make_model without any arguments, since there's no guarantee that there
    #wasn't already a params file in this directory
    filename = [*new_filenames - filenames][0]
    #create the default model
    mod = make_model(params = filename)
    #run the default model in verbose mode
    mod.run(verbose = True)

#wrapper around landscape.make_landscape
def make_landscape(params):
    landscape = landscape._make_landscape(params)
    return landscape


#wrapper around genome.make_genomic_architecture
def make_genomic_architecture(params, landscape):
    gen_arch = genome.make_genomic_architecture(params, landscape)
    return gen_arch


#wrapper around individual.make_individual
    #should provide either a new genome for the individual, or a
    #genomic_architecture to use to draw its genome;
    #and should provide either a parental centerpoint to disperse from, or a
    #landscape.dim tuple within whihc to choose a location;
    #burn can be True (i.e. then the individual will have a [[0,0]] genome)
def make_individual(idx, genomic_architecture=None, new_genome=None, dim=None,
    parental_centerpoint=None, sex=None, age=0, burn=False):
    assert (genomic_architecture is not None
        or new_genome is not None), ("Either a new genome must be provided "
        "(i.e. 'new_genome' must not be None) or a genomic architecture from "
        "which to draw a new genome must be provided (i.e. "
        "'genomic_architecture' must not be None.")
    assert (parental_centerpoint is not None
            or dim is not None), ("Either a Landscape-dimension tuple must be "
            "provided (i.e. 'dim' must not be None) or a parental centerpoint "
            "from which to disperse the individual must be provided (i.e. "
            "'parental_centerpoint' must not be None).")
    ind = individual.make_individaul(idx = idx, offspring = False,
            dim = dim, genomic_architecture = genomic_architecture,
            new_genome = new_genome, sex = sex,
            parental_centerpoint = parental_centerpoint, age = age,
            burn = burn)
    return ind


#wrapper around population.make_population
    #burn can be True (i.e. then the individuals will have a [[0,0]] genome)
def make_population(landscape, pop_params, burn=False):
    pop = population.make_population(landscape, pop_params, burn = burn)
    return(pop)


#wrapper around community.make_comunity
    #burn can be True (i.e. then the individuals will have a [[0,0]] genome)
def make_community(landscape, params, burn=False):
    comm = community.make_community(landscape, params, burn = burn)
    return comm

