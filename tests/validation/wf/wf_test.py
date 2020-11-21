import geonomics as gnx


from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt
import os

orig_params = gnx.read_parameters_file(('/home/drew/Desktop/stuff/berk'
                                        '/research/projects/sim/geonomics/'
                                        'tests/validation/wf/wf_params.py'))

# set some image params
img_dir = ('/home/drew/Desktop/stuff/berk/research/projects/sim/'
           'methods_paper_images/final/')
ax_fontdict = {'fontsize': 18,
               'name': 'Bitstream Vera Sans'}
ttl_fontdict = {'fontsize': 20,
                'name': 'Bitstream Vera Sans'}
ticklabelsize=15

K_factors = [10, 20, 30]
persist_list = []
mean_t_persist_list = []
mean_pop_size_list = []
pop_Nts = []


def get_allele_freqs(spp):
    freqs = {i: freq for i,
             freq in enumerate(spp._get_genotypes().mean(axis=2).mean(axis=0))}
    return freqs


def calc_harmonic_mean(Nt):
    Ne_harm = 1 / ((1 / len(Nt)) * sum([1 / N for N in Nt]))
    return Ne_harm


# change plot dimensions
figsize = plt.rcParams['figure.figsize']
plt.rcParams['figure.figsize'] = [figsize[0], 2.5*figsize[1]]

fig = plt.figure()
# plt.suptitle(('1-allele trajectories in a Wright-Fisher approximation '
#              'with %i independent loci') % (
#                  orig_params.comm.species.spp_0.gen_arch.L))
max_x = 0
# NOTE: run through K_factors from greatest downward, to make it
# easier to set all x-axes to the same maximum x-limit
for n, K_fact in enumerate(K_factors[::-1]):
    params = deepcopy(orig_params)
    params.comm.species['spp_0'].init['K_factor'] = K_fact
    print("USING K_fact %0.2f" % params.comm.species['spp_0'].init.K_factor)

    mod = gnx.make_model(params)

    mod.walk(mode='burn', T=10000, verbose=True)

    freqs = {loc: [] for loc in range(mod.comm[0].gen_arch.L)}
    # run model until all loci have fixed
    while (False not in [len(f) == 0 for f in freqs.values()]
           or False in [f[-1] in (0, 1) for f in freqs.values()]):
        freqs_t = get_allele_freqs(mod.comm[0])
        for loc, freq in freqs_t.items():
            freqs[loc].append(freq)
        # instead of using Walk-based movement, just randomly replace
        # individuals all over the map
        new_xs = np.random.uniform(low=0, high=mod.land.dim[1],
                                   size=len(mod.comm[0]))
        new_ys = np.random.uniform(low=0, high=mod.land.dim[0],
                                   size=len(mod.comm[0]))
        [setattr(i, 'x', new_xs[n]) for n, i in enumerate(
                                                        mod.comm[0].values())]
        [setattr(i, 'y', new_ys[n]) for n, i in enumerate(
                                                        mod.comm[0].values())]
        # NOTE: make sure spp.cells and spp.coords attributes are set correctly
        mod.comm[0]._set_coords_and_cells()
        # run a model timestep
        mod.walk(mode='main', T=1, verbose=True)
        print('\n%i LOCI FIXED\n' % sum(
            [f[-1] in (0, 1) for f in freqs.values()]))

    # calculate average persistence time and average pop size, and record
    mean_pop_size = calc_harmonic_mean(mod.comm[0].Nt[-mod.t:])
    t_persist_list = [f.index(0) if 0 in f else f.index(
                                                1) for f in freqs.values()]
    mean_pop_size_list.append(mean_pop_size)
    mean_t_persist = np.mean(t_persist_list)
    persist_list.append(t_persist_list)
    mean_t_persist_list.append(mean_t_persist)
    pop_Nts.append(mod.comm[0].Nt[-mod.t:])

    ax = fig.add_subplot(313-n)
    ax.set_title(("K-factor = %i; mean population size = %0.1f") % (
        K_fact, mean_pop_size), fontdict=ttl_fontdict)
    if n == 1:
        ax.set_ylabel("frequency of '1' allele",
                      fontdict=ax_fontdict)
    if n == 0:
        ax.set_xlabel('model time (timesteps)', fontdict=ax_fontdict)

    max_x = max(max_x, mod.t)
    ax.set_xlim((0, max_x))
    plt.ylim(0, 1)
    for loc, freq_list in freqs.items():
        ax.plot(range(len(freq_list)), freq_list, '-', alpha=0.6)
    ax.tick_params(labelsize=ticklabelsize)
plt.subplots_adjust(hspace=0.35)
plt.show()
#plt.savefig(os.path.join(img_dir, 'WF_allele_trajectories.pdf'))

# reverse the lists I had appended to, since I went through the K_factors in
# reverse order
mean_t_persist_list = mean_t_persist_list[::-1]
mean_pop_size_list = mean_pop_size_list[::-1]
pop_Nts = pop_Nts[::-1]

# change plot dimensions
plt.rcParams['figure.figsize'] = [6, 6]
fig2 = plt.figure()
# plt.suptitle(("Mean population size and mean persistence time,\nas a "
#              "fn. of K_factor (a linear proxy of population size),\nfor %i "
#              "independent, neutral loci") % mod.comm[0].gen_arch.L)
# ax21 = fig2.add_subplot(1, 2, 1)
# plt.title('Mean population size')
# plt.xlabel('K_factor')
# plt.ylabel('mean population size')
# plt.plot(K_factors, mean_pop_size_list)
# ax22 = fig2.add_subplot(1, 2, 2)
# plt.title(('Mean persistence time (observed, blue;'
#           ' vs. expected, red)'))
plt.xlabel('mean population size', fontdict=ax_fontdict)
plt.ylabel('mean persistence time (timesteps)', fontdict=ax_fontdict)
# plot the data
plt.plot(mean_pop_size_list, mean_t_persist_list, 'ob', alpha=0.5)
# plot expected mean persistence according to W-F model
# (according to theory, expected persistence time for loci starting at 0.5/0.5
# allele freqs is 2.776N, i.e. -4N(log(p)p + log(q)q) solved for p = q = 0.5;
# here I expect some deviation from that because this
# is based on a single simulated instantiation, and also because my
# populations are approximating W-F populations but not perfectly, so most
# likely N_t > N_e)
plt.plot(mean_pop_size_list, [2.776*n for n in mean_pop_size_list], 'or',
         alpha=0.5)
ax = fig2.axes[0]
ax.tick_params(labelsize=ticklabelsize)
#plt.savefig(os.path.join(img_dir, 'WF_mean_persist_vs_pop_size.pdf'))

