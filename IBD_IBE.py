#!/usr/bin/python
# IBD_IBE_test.py

# import geonomics
import geonomics as gnx

# other imports
from copy import deepcopy
# from itertools import chain
import numpy as np
from sklearn.decomposition import PCA
# import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import time

# set some plotting params
img_dir = ('/home/drew/Desktop/stuff/berk/research/projects/sim/methods_paper/'
           'img/final/')
ax_fontdict = {'fontsize': 12,
               'name': 'Bitstream Vera Sans'}
ttl_fontdict = {'fontsize': 15,
                'name': 'Bitstream Vera Sans'}


# function for running and plotting genetic PCA
def plot_genetic_PCA(species):
    # get array of resulting genomic data (i.e. 'speciome'),
    # genotypes meaned by individual
    speciome = np.mean(np.stack([i.g for i in species.values()]), axis=2)
    # run PCA on speciome
    pca = PCA(n_components=3)
    PCs = pca.fit_transform(speciome)
    # normalize the PC results
    norm_PCs = (PCs - np.min(PCs,
                             axis=0)) / (np.max(PCs,
                                                axis=0) - np.min(PCs,
                                                                 axis=0))
    # use first 3 PCs to get normalized values for R, G, & B colors
    PC_colors = norm_PCs * 255
    # scatter all individuals on top of landscape, colored by the
    # RBG colors developed from the first 3 geonmic PCs
    xs = mod.comm[0]._get_xs()
    ys = mod.comm[0]._get_ys()
    # get environmental raster, with barrier masked out
    masked_env = deepcopy(mod.land[0].rast)
    masked_env[mod.land[1].rast == 0] = np.nan
    # create light colormap for plotting landscape
    # bot = plt.cm.get_cmap('Blues', 256)(np.linspace(0.4, 0.45, 2))[0]
    # top = plt.cm.get_cmap('Reds', 256)(np.linspace(0.4, 0.45, 2))[0]
    # cols = np.vstack((top, bot))
    # cmap = mpl.colors.ListedColormap(cols, name='OrangeBlue')
    cmap = plt.cm.coolwarm
    cmap.set_bad(color='#8C8C8C')
    # plot landscape
    plt.imshow(masked_env, cmap=cmap, alpha=0.8)
    # scatter plot of individuals, colored by composite PC score
    plt.scatter([x - 0.5 for x in xs],
                [y - 0.5 for y in ys],
                c=PC_colors/255.0,
                s=25, edgecolors='black')
    # fix x and y limits
    [f([dim - 0.5 for dim in (0, mod.land.dim[0])]) for f in (plt.xlim,
                                                              plt.ylim)]
    # get rid of x and y ticks
    [f([]) for f in (plt.xticks, plt.yticks)]


# calculate euclidean distance from two n-length vectors
def calc_euc(x, y):
    euc = np.sqrt(sum([(n-m)**2 for n, m in zip(x, y)]))
    return euc


# calculate lower-triangular of PCA-bsaed Euclidean genetic distances between
# all individuals, using a 'speciome' (2d array of all individs' genomes)
def calc_dists(species, dist_type='gen', env_lyrs=None):
    # calculate genetic distance as the euclidean distance between individuals
    # in genetic PC space
    if dist_type == 'gen':
        speciome = np.mean(np.stack([i.g for i in species.values()]), axis=2)
        pca = PCA()
        vals = pca.fit_transform(speciome)
    # calculate geographic distance as the linear euclidean distance between
    # individuals
    elif dist_type == 'geo':
        vals = np.stack([np.array((i.x, i.y)) for i in species.values()])
    # calculate environmental distance as the euclidean distance between
    # individuals' environments, for all environmental layers specified by
    # the 'env_lyrs' argument
    elif dist_type == 'env':
        vals = np.stack([np.array(i.e)[env_lyrs] for i in species.values()])
    # print(vals)
    # print(vals.shape)
    n_ind = vals.shape[0]
    dist_mat = np.ones([n_ind] * 2) * -999
    # dist_vals = [[calc_euc(i, j) for j in vals[n:,
    #                                        :]] for n, i in enumerate(vals)]
    for i in range(n_ind):
        for j in range(0, i+1):
            dist_mat[i, j] = calc_euc(vals[i, :], vals[j, :])
    # check that all diagonal values are 0
    assert np.all(np.diag(dist_mat) == 0), "Not all diagonal values are 0!"
    # print(dist_vals)
    # for item in dist_vals:
    #    assert item[0] == 0, "Not all diagonal values are 0!"

    dists = dist_mat[np.tril_indices(dist_mat.shape[0], -1)]
    # dist_vals = [item[1:] for item in dist_vals]
    # dists = [*chain.from_iterable(dist_vals)]
    # assert that the length is correct
    assert len(dists) == (n_ind**2 - n_ind)/2, "Length not equal to n(n-1)/2!"
    return dists


# make empty figure
fig = plt.figure()

#start timer
start = time.time()

# make model
mod = gnx.make_model('./geonomics/example/IBD_IBE/IBD_IBE_params.py')

# define number of timesteps
T = 1000

# burn model in
mod.walk(20000, 'burn')

# plot genetic PCA before genomic evolution begins
ax1 = fig.add_subplot(221)
ax1.set_title('t = 0')
plot_genetic_PCA(mod.comm[0])

# plot phenotypes before genomic evolution begins
ax3 = fig.add_subplot(223)
mask = np.ma.masked_where(mod.land[1].rast == 0, mod.land[1].rast)
mod.plot_phenotype(0, 0, mask_rast=mask)
[f((-0.5, 39.5)) for f in [plt.xlim, plt.ylim]]

# run model for T timesteps
mod.walk(T)

#finish timer
stop = time.time()
tot_time = start - stop

# plot genetic PCA after 1/4T timesteps
ax2 = fig.add_subplot(222)
ax2.set_title('t = %i' % T)
plot_genetic_PCA(mod.comm[0])

# plot the individuals' phenotypes
ax3 = fig.add_subplot(224)
mod.plot_phenotype(0, 0, mask_rast=mask)
[f((-0.5, 39.5)) for f in [plt.xlim, plt.ylim]]

# add title
# plt.suptitle(('Neutral genomic evolution across complex landscape with '
#              '_MovementSurface,\n(for a ~%i-individual species with 100 '
#              'loci') % int(np.mean(mod.comm[0].Nt)))
plt.show()
plt.savefig(os.path.join(img_dir, 'IBD_IBE_PCA.png'))


spp_subset = {ind: mod.comm[0][ind] for ind in np.random.choice([*mod.comm[0]],
                                                                100)}
gen_dists = calc_dists(spp_subset)
geo_dists = calc_dists(spp_subset, 'geo')
env_dists = calc_dists(spp_subset, 'env', [0])
fig2 = plt.figure()
ax1 = fig2.add_subplot(121)
plt.scatter(geo_dists, gen_dists, alpha=0.05, c='black')
ax1.set_xlabel('geographic distance')
ax1.set_ylabel('genetic distance')
ax2 = fig2.add_subplot(122)
plt.scatter(env_dists, gen_dists, alpha=0.05, c='black')
ax2.set_xlabel('environmental distance')
ax2.set_ylabel('genetic distance')

# TODO: add regression line to each plot

plt.show()
plt.savefig(os.path.join(img_dir, 'IBD_IBE_scatter.png'))

# print out time
print("\n\nModel ran in %0.2f seconds." % tot_time)
