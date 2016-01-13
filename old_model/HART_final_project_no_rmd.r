#TODO:

# calculate num pops and other metrics at outset, to ensure that two separate populations are determined


# possibly use Geneland's simdata function to make data their way and compare them to my data, to see how well
# I've simulated my data??

# assess metrics with starting population and store in object, to make first point (at left of graph) for all
# p.cross-value lines

#wrap whole thing in RMarkdown, add blocks of text for writeup, and run officially

#PRESENTATION!

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


#load necessary pacakges
library(raster)
library(rgeos)
library(kriging)
library(spatstat)
library(circular)
library(poppr)
library(mmod)
library(adegenet)
#library(Geneland)
#library(ggplot2)



#set seed, to make results reproducible
set.seed(1)


#Run in 'debugging mode'?
#debug = T
debug = F



#Create running plot (T) or output PDF of plot (F)?
#running.plot = T
running.plot = F

#Create PDF (T) or plot to active device (F)?  (Only utilized if running.plot = F)
#PDF = T
PDF = F


########
#Colors for points
invisible(palette(c('#f03b20', '#ffeda0', '#feb24c'))); invisible(dev.off())
#palette(c('#2710DF', '#F6FF3D', '#60FFAE')); dev.off() 


#Colors for raster
Blues = c('#deebf7', '#9ecae1', '#3182bd')
ramp = colorRampPalette(Blues, space = 'Lab', bias = 0.5)


##############
#Plotting params
PCH = 21
FG = '#4C4C4C'
CEX = 1.5

p.cross = 0.8
#p.cross = c(0.0, 0.5, 1.0)
#p.cross = c(0.0005, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.90, 1.0)

num.loci = c(5,10,15,20, 50)

R.DIM = 30
SIZE.POP = 15
N.LOCI = 10
N.TIME = 400

D.PAIR = 0.005
REPRO.CYCLE = 5
FOR.AVG = 6 
MEAN.OFF = 0.5
SD.OFF = 0.1
FIT.ADVNTG = 1.0
MEAN.DISP.DIST = 7
MEAN.D.MOVE = 0.01








#create landscape layer 1 (heterogeneously distributed resource layer)
pts <- data.frame(cbind(xCoord = runif(25,0,R.DIM), yCoord = runif(25,0,R.DIM), habitat = runif(25, 0, 1)))
env <- kriging(x=round(pts$xCoord), y=round(pts$yCoord), response = pts$habitat)
env <- 0.7*rasterFromXYZ(env$map)
env@data@values = env@data@values/max(env@data@values) #normalize to 0 < cell_value < 1
invisible(setExtent(env, extent(0,100,0,100)))









#calculate mean.d.move from env and MEAN.D.MOVE
MEAN.D.MOVE = MEAN.D.MOVE*sqrt((env@extent@xmax-env@extent@xmin)^2 + (env@extent@ymax-env@extent@ymin)^2)
D.PAIR = D.PAIR*sqrt((env@extent@xmax-env@extent@xmin)^2 + (env@extent@ymax-env@extent@ymin)^2)

hab.x = sort(runif(24,env@extent@xmin, env@extent@xmax))
hab.y = sort(runif(24,env@extent@ymin, env@extent@ymax))
hab.x = c(env@extent@xmin, env@extent@xmin, hab.x, env@extent@xmax, env@extent@xmax, env@extent@xmin)
hab.y = c(env@extent@ymin, hab.y[1], hab.y, hab.y[length(hab.y)], env@extent@ymin, env@extent@ymin)
hab.poly = SpatialPolygons(list(Polygons(list(Polygon(matrix(cbind(hab.x, hab.y), ncol = 2))), c('polygon'))))
hab = rasterize(hab.poly, env)  #NOTE: let 1's = hab A (i.e. pop 'p1') and 0's = B (i.e. pop 'p2')
hab@data@values[which(is.na(hab@data@values), arr.ind = TRUE)] = 0









#Define function to simulate a dataset of two populations of individuals
#each individual will be characterized by: 
  #a.) genotype (homozygous or heterozygous for each of a set of codominant loci (i.e. SNPs)
      #NOTE: allele frequency pairs differ between the two populations for each locus
      #NOTE: allele frequencies differ across loci within each population 
  #b.) starting coordinate (within the tessellated portion of the landscape corresponding to its population)
sim.pop  = function(n.loci, size.pop, for.avg){
    assign("pop.names", c('p1', 'p2', 'h'), envir = .GlobalEnv)
    assign("pop.hab.values", list('p1' = 1, 'p2' =  0, 'h' = 0.5), envir = .GlobalEnv)

    my.letters = c()
    for (l in letters){ my.letters = c(my.letters, paste(l, letters, sep = ''))}
    my.letters = unique(my.letters)
    assign('my.letters', my.letters, envir = .GlobalEnv)
    
    start.pops = list()
    #assign("allele.freqs", data.frame('locus' = my.letters[seq(n.loci)], 'p1' = rep(0, N.LOCI), 'p2' = rep(0, n.loci)), envir = .GlobalEnv)
    allele.freqs = data.frame('locus' = my.letters[seq(n.loci)], 'p1' = rep(0, N.LOCI), 'p2' = rep(0, n.loci))
    assign("allele.cols", sort(c(paste(my.letters[1:n.loci], sep = '', rep(1,n.loci)), paste(my.letters[1:n.loci], sep = '', rep(2,n.loci)))), envir = .GlobalEnv)
    
    allele.pairs = list()
    for (i in 1:(length(allele.cols)/2)){
        allele.pairs[[gsub('[0-9]', '', allele.cols[i*2])]] = c(allele.cols[i*2-1], allele.cols[i*2])
      }
    
    allele.cols = sort(c(paste(my.letters[1:n.loci], sep = '', rep(1,n.loci)), paste(my.letters[1:n.loci], sep = '', rep(2,n.loci))))
    
    for (pop in pop.names) {
      if (pop != 'h'){
      df = data.frame('pop' = rep(pop, size.pop), 'ind' = seq(size.pop), 'for.avg' = rep(0, size.pop))
      #df = data.frame('pop' = rep(pop, size.pop), 'pop.hab.values' = rep(pop.hab.values[[pop]], size.pop), 'ind' = seq(size.pop), 'for.avg' = rep(0, size.pop))
      forage = matrix(0, nrow = size.pop, ncol = for.avg)
      #for.avg = matrix(0,nrow = SIZE.POP, ncol = 1)
      for (locus in 1:n.loci) {
        allele.freqs[locus, pop] = round(runif(1, 0, 1), 2)
        df[sprintf("%s1", my.letters[locus])] = ifelse(rbinom(SIZE.POP, 1, allele.freqs[locus, pop]), toupper(my.letters[locus]) , tolower(my.letters[locus]) )
        df[sprintf("%s2", my.letters[locus])] = ifelse(rbinom(SIZE.POP, 1, allele.freqs[locus, pop]), toupper(my.letters[locus]) , tolower(my.letters[locus]) )
      }
      
    
      hab_indices = which(hab@data@values == pop.hab.values[[pop]], arr.ind = TRUE)
      individ_cells = sample(hab_indices, size.pop, replace = TRUE)
      df = as.data.frame(cbind(df, xyFromCell(hab, individ_cells)))
      #df['x'] = as.data.frame(xyFromCell(hab, individ_cells))$x
      #df['y'] = as.data.frame(xyFromCell(hab, individ_cells))$y
      #df['x'] = runif(SIZE.POP, env@extent@xmin, env@extent@xmax)  
      #df['y'] = runif(SIZE.POP, env@extent@ymin, env@extent@ymax)
      start.pops[[pop]] = list(df, forage)
      #pops[[pop]] = list(df, forage, for.avg)
      }
    }
    assign("allele.freqs", allele.freqs, envir = .GlobalEnv)
    #start.pops[['h']] = list(start.pops[['p1']][[1]][0,], start.pops[['p2']][[2]][0,])
    return(start.pops)
}









new.loc = function(new.x, new.y){ 
    stopifnot(length(new.x) == length(new.y))
    xmin = min(as.data.frame(xyFromCell(env, seq(length(env@data@values))))$x)
    xmax = max(as.data.frame(xyFromCell(env, seq(length(env@data@values))))$x)
    ymin = min(as.data.frame(xyFromCell(env, seq(length(env@data@values))))$y)
    ymax = max(as.data.frame(xyFromCell(env, seq(length(env@data@values))))$y)
    output.x = ifelse((new.x > xmin & new.x < xmax), new.x, ifelse(new.x < xmin, xmin, xmax))
    output.y = ifelse((new.y > ymin & new.y < ymax), new.y, ifelse(new.y < ymin, ymin, ymax))
    #output.x = ifelse((new.x > env@extent@xmin & new.x < env@extent@xmax), new.x, ifelse(new.x < env@extent@xmin, env@extent@xmin, env@extent@xmax))
    #output.y = ifelse((new.y > env@extent@ymin & new.y < env@extent@ymax), new.y, ifelse(new.y < env@extent@ymin, env@extent@ymin, env@extent@ymax))
    output = as.data.frame(matrix(data = c(output.x, output.y), nrow = length(new.x), ncol = 2))
    colnames(output) = c('x', 'y')
    return(output)
}






displace = function(curr, twd, dist){
    angle = coord2rad(twd$x-curr$x, twd$y-curr$y) 
    new.x = (dist * cos(angle)) + curr$x 
    new.y = (dist * sin(angle)) + curr$y
    out = as.data.frame(cbind(new.x, new.y))
    colnames(out) = c('x', 'y')
    return(out)
}







burn.in = function(start.pops, size.pop, mean.d.move, for.avg){
for (pop in pop.names) {

  if (pop != 'h'){

  for (burn in 1:for.avg) {
    #randomly move all individuals and have them forage, same as below in actual model, and add foraging value
    #to their foraging-history vector, to create a starting rolling-average foraging value for all individuals
    
    #create vector of stochastically varying step distances, and vector of randomly chosen directions
    dirs = as.numeric(suppressWarnings(rvonmises(size.pop, 0, 0)))# * 360 / 2 / pi)
    dists = rlnorm(size.pop, meanlog = log(mean.d.move), sdlog = abs(log(mean.d.move))/10)   #NOTE: WANT A DIFFERENT DISTRIBUTION AND/OR PARAMETERIZATION??
    new.x = start.pops[[pop]][[1]]$x + base::cos(dirs)*dists
    new.y = start.pops[[pop]][[1]]$y + base::sin(dirs)*dists

    new.coords = new.loc(new.x, new.y)


    crossed = which( !(extract(hab, new.coords) == pop.hab.values[[pop]]) )
    sprintf('burn = %i', burn)
    if (debug){ print(crossed)}
    if (length(crossed) > 0){
      if(debug){assign('crossed', crossed, envir = .GlobalEnv)}
    decisions = rbinom(length(crossed), 1, 0)   #NOTE: for simulation of the starting population, I am setting p = 0, so that no individuals will cross the habitat boundary prior to the main simulation)
      if (length(which(decisions == 0)) > 0){
    loc.cells = new.coords[crossed[decisions == 0], ]
    possible.reloc.cells = as.data.frame(xyFromCell(hab, which(hab@data@values == pop.hab.values[pop])))


    #Find nearest neighboring cells within native habitat
    gd = gDistance(SpatialPoints(loc.cells), SpatialPoints(possible.reloc.cells), byid = T)
    mins = apply(gd, MARGIN = 2, FUN = min)
    min.cells = c()
    for (i in 1:ncol(gd)){
      min.cells = c(min.cells, as.numeric(which(gd[,i] == mins[i])[1]))
    }
    reloc.direc.cells = possible.reloc.cells[min.cells,]
    
    new.coords[crossed[decisions ==0], ] = reloc.direc.cells
    new.coords = new.loc(new.coords$x, new.coords$y)
    
    if (debug) {print(reloc.direc.cells)}

    }
   }

    if (debug) {print('---------------------')}


    #relocate each individual to new cell using these two vectors
    start.pops[[pop]][[1]]$x = new.coords$x
    start.pops[[pop]][[1]]$y = new.coords$y

    
    #extract resource layer values to each individual's points (i.e. 'forage')
    if (debug) {print(new.coords[c('x', 'y')])}
    if (debug) {assign('new.coords', new.coords, envir = .GlobalEnv)}
    start.pops[[pop]][[2]][,burn] = extract(env, new.coords[c('x', 'y')], method = 'bilinear') 


      }
  #calculate starting rolling average for each pop, and load into third object in population's list object
  start.pops[[pop]][[1]]$for.avg = rowMeans(start.pops[[pop]][[2]])
    }
  }
return(start.pops)
}








core.model = function(p.cross,
                      start.pops, 
                      n.time, 
                      size.pop, 
                      mean.d.move,
                      for.avg, 
                      repro.cycle, 
                      d.pair,
                      n.loci, 
                      fit.advntg,
                      mean.off, 
                      sd.off,
                      mean.disp.dist, 
                      sd.disp.dist){


  pops = start.pops
  all.pops = rbind(pops[['p1']][[1]], pops[['p2']][[1]], pops[['h']][[1]])
  
  all.pops$x = as.numeric(all.pops$x)
  all.pops$y = as.numeric(all.pops$y)
  all.pops$for.avg = as.numeric(all.pops$for.avg)
  levels(all.pops$pop) = c(levels(all.pops$pop), 'h')  #Add factor level for 'hybrid' individuals


  all.pops.for = rbind(pops[['p1']][[2]], pops[['p2']][[2]], pops[['h']][[2]])


  G.1 = c()
  G.2 = c()
  G.h = c()
  k = c()
  #Fst = c()
  #Fst.2 = c()
  Gst = c()
  prop.h = c()

  
  for (t in 1:n.time) {

      #create vector of stochastically varying step distances, and vector of randomly chosen directions
      dirs = as.numeric(suppressWarnings(rvonmises(nrow(all.pops), 0, 0)))# * 360 / 2 / pi)
      dists = rlnorm(nrow(all.pops), meanlog = log(mean.d.move), sdlog = abs(log(mean.d.move))/10)   #NOTE: WANT A DIFFERENT DISTRIBUTION AND/OR PARAMETERIZATION??
      new.x = all.pops$x + base::cos(dirs)*dists
      new.y = all.pops$y + base::sin(dirs)*dists
      
      new.coords = new.loc(new.x, new.y)
     
      if(debug){
        assign('dirs', dirs, envir = .GlobalEnv)
        assign('dists', dists, envir = .GlobalEnv)
        assign('new.x', new.x, envir = .GlobalEnv)
        assign('new.y', new.y, envir = .GlobalEnv)
        assign('new.coords', new.coords, envir = .GlobalEnv)
      }

      
      #----------------------------------------------------------------------------------------------
      #KEY PART: decide if 'allowed' to cross the habitat boundary
      for (pop in pop.names){
        new.coords.pop = new.coords[all.pops$pop == pop,]
        if (length(new.coords.pop) >0){
        if (pop != 'h'){
        #crossed = which( !(extract(hab, new.coords.pop) == all.pops$pop.hab.values) )
        crossed = which(extract(hab, new.coords.pop) != pop.hab.values[[pop]]) 
        if (length(crossed) > 0){
          if(debug){assign('crossed', crossed, envir = .GlobalEnv)
                    assign('new.coords.pop', new.coords.pop, envir = .GlobalEnv)
          }

          decisions = rbinom(length(crossed), 1, p.cross)   #KEY SPOT: implementing p.cross value in decision of whether or not individual 'allowed' to cross
          if(debug){assign('decisions', decisions, envir = .GlobalEnv)}
          if (length(which(decisions == 0)) > 0){
            loc.cells = new.coords.pop[crossed[decisions == 0], ]
            possible.reloc.cells = as.data.frame(xyFromCell(hab, which(hab@data@values == pop.hab.values[pop])))


   
            #Find nearest neighboring cells within native habitat
            gd = gDistance(SpatialPoints(loc.cells), SpatialPoints(possible.reloc.cells), byid = T)
            min.cells = as.vector(apply(gd, MARGIN = 2, FUN = which.min))
            reloc.direc.cells = possible.reloc.cells[min.cells,]
 
          if(debug){
            assign('possible.reloc.cells', possible.reloc.cells, envir = .GlobalEnv)
            assign('gd', gd, envir = .GlobalEnv)
            assign('min.cells', min.cells, envir = .GlobalEnv)
            assign('reloc.direc.cells', reloc.direc.cells, envir = .GlobalEnv)
            assign('loc.cells', loc.cells, envir = .GlobalEnv)
          }

            #NOTE: CHANCE OF PLACING INDIVIDUAL BACK IN NON-NATIVE HABITAT BY NOT LETTING THEM OUTSIDE RASTER, BUT PROBABLY SMALL RISK...
            #reloc.direc.cells.coords = new.loc(reloc.direc.cells['x'], reloc.direc.cells['y'])
            #reloc.direc.cells = cbind(reloc.direc.cells.coords['x'], reloc.direc.cells.coords['y'])

            if (debug) {assign('loc.cells', loc.cells, envir = .GlobalEnv)}

            reloc.cells = displace(loc.cells, reloc.direc.cells, mean.d.move)

            new.coords.pop[crossed[decisions ==0], ] = reloc.cells
          }
        }
      }
            new.coords.pop$x = new.loc(new.coords.pop$x, new.coords.pop$y)$x
            new.coords.pop$y = new.loc(new.coords.pop$x, new.coords.pop$y)$y

     
      #relocate each individual to new cell using these two vectors
      all.pops[all.pops$pop == pop, ]$x = new.coords.pop$x
      all.pops[all.pops$pop == pop, ]$y = new.coords.pop$y

     }

    }

      
      #extract resource layer values to each individual's points (i.e. 'forage')
      all.pops.for[, ] = cbind(all.pops.for[, 2:for.avg], extract(env, all.pops[,c('x', 'y')], method = 'bilinear'))
      if (debug) {print(cbind(all.pops.for[, 2:for.avg], extract(env, all.pops[,c('x', 'y')], method = 'bilinear')))}

      #recalculate rolling average of foraging for last FOR.AVG timesteps
      all.pops$for.avg = rowMeans(all.pops.for)
      if(debug){sprintf('pop = %s', pop)}
      if(debug){assign('all.pops', all.pops, envir = .GlobalEnv)}
      if(debug){assign('all.pops.for', all.pops.for, envir = .GlobalEnv)}
      if (debug) {print(rowMeans(all.pops.for[1:3,]))}

  
      if (t%%repro.cycle == 0) {
        #every m timesteps, species reproduces simultaneously across landscape
        #reproductive pairs selected randomly from among all pairs within D.PAIR distance of one another
        #NOTE: do not allow individuals to reproduce >1x 
  
         tot.off = 0


        mate1 = which(nndist(all.pops[c('x', 'y')]) <= (d.pair))
        if (length(mate1) >0){
        #NOTE: NON-RECIPROCAL NEAREST NEIGHBORS POSSIBLE! (e.g. if 1 is nn to 2, 2 is nn to 1 and to 3 but closer to 1); THUS, NEED TO FILTER OUT NON-REPEATS!
        mate2 = nnwhich(all.pops[c('x', 'y')])[mate1]

        #NOTE: CAN'T FIGURE OUT HOW TO LIMIT TO SINGLE MATING PER INDIVIDUAL, SO FOR NOW ALLOWING MULTIPLE (reasonable for males, females for some spp, but my species is currently sexless anyhow)
        ##CHECK THAT THE MATE LISTS HAVE THE SAME LENGTH
        #stopifnot(length(mate1) == length(mate2))
        pairs = list()
        for (m in 1:length(mate1)){
          pairs[[m]] = sort(c(mate1[m], mate2[m]))
        }
        final.pairs = base::unique(pairs)
        if(debug){assign('final.pairs', final.pairs, envir = .GlobalEnv)} 

        #CHECK THAT length of FINAL PAIRS IS HALF OF THE pairs LIST (B/C EACH PAIR REPEATED)
        #BECUASE I CAN'T GET THE SINGLE-MATING-PER-INDIVID RULE WORKING, NOT USING NEXT stopifnot
        #stopifnot(length(final.pairs) == length(pairs)/2)

        
        #per reproductive event, draw number of offspring from:
        for (pair in 1:length(final.pairs)) {
          new.pop = ifelse(sum(as.numeric(all.pops[final.pairs[[pair]],]$pop == 'p1')) == 2, 'p1', ifelse(sum(as.numeric(all.pops[final.pairs[[pair]],]$pop == 'p2')) == 2, 'p2', 'h'))
          #NOTE: How to allow hybrids to be unaffected??
          hab.loc = as.numeric(pop.hab.values[all.pops[final.pairs[[pair]],'pop']] == extract(hab, all.pops[final.pairs[[pair]],c('x', 'y')]))
          fit.advntg.pair = all.pops[final.pairs[[pair]], 'for.avg'] * hab.loc * fit.advntg
          if (debug) {print(head(all.pops))}
          if (debug) {print(final.pairs[[pair]])}
          num.off = round(rlnorm(1, mean.off, sd.off + sd.off*mean(all.pops[final.pairs[[pair]], 'for.avg'] + fit.advntg.pair)))
          tot.off = tot.off + num.off

          #NOTE: also allow pair's genotypes to impact fitness??
          if (num.off > 0){
          for (offspring in 1:num.off) {
            zygote = c()
            for (mate in 1:2){
              chromosomes = matrix(all.pops[final.pairs[[pair]][[mate]], allele.cols], nrow = n.loci, ncol = 2, byrow = TRUE)
              gamete = c()
              for (locus in 1:n.loci) {
                gamete = c(gamete, chromosomes[[locus, rbinom(1,1,0.5)+1]])
              }
              zygote = c(zygote, gamete)
            }
          
              #choose dispersal location for offspring (using same manner as above, both from centroid of parents)
              dir = as.numeric(suppressWarnings(rvonmises(1, 0, 0)))# * 360 / 2 / pi)
              dist = rexp(1, rate = (1/mean.disp.dist))   #NOTE: WANT A DIFFERENT DISTRIBUTION AND/OR PARAMETERIZATION??
              off.x = mean(all.pops[final.pairs[[pair]], 'x']) + base::cos(dir)*dist
              off.y = mean(all.pops[final.pairs[[pair]], 'y']) + base::sin(dir)*dist
              off.new.coords = new.loc(new.x, new.y)

              #get offspring foraging average (straight average of two parents)
              off.for.avg = mean(all.pops[final.pairs[[pair]],]$for.avg)

              if(debug){print('HAPPY BIRTHDAY!!!!!')
              print(zygote)
              assign('zygote', zygote, envir = .GlobalEnv)
              }

              all.pops = rbind(all.pops, as.vector(c(new.pop, nrow(all.pops)+1, off.for.avg, sort(zygote), off.new.coords$x, off.new.coords$y)))
              all.pops$x = as.numeric(all.pops$x)
              all.pops$y = as.numeric(all.pops$y)
              all.pops$for.avg = as.numeric(all.pops$for.avg)


            }
          }
        }
     }

        #mortality (for now, just a simple rule randomly culling old individuals, some number drawn from a poisson with lambda = num born this 'generation'
        #FOR NOW, ACTUALLY, JUST MAKE NUM.DEAD == TOT.OFF
        num.dead = tot.off
        dead.rows = sample(seq(nrow(all.pops)-tot.off), num.dead, replace = F)

        all.pops = all.pops[seq(nrow(all.pops))[!(seq(nrow(all.pops)) %in% dead.rows)], ]

        row.names(all.pops) = as.character(seq(nrow(all.pops)))


      #push all.pops to .GlobalEnv, for debugging
      if (debug) {assign('all.pops', all.pops, envir = .GlobalEnv)}
    }


  if (running.plot){
  if ((t == 1 || t %%10 == 0)) {
    plot(env, col = ramp(5), main = list(sprintf('p = %0.4f; t = %i', p, t)), cex.lab = CEX, cex.axis = CEX)
    lines(hab.x, hab.y, lwd = 1.5)
    points(all.pops[, c('x', 'y')], bg = all.pops$pop , pch = PCH, fg = FG, cex = CEX)
  }
  }


 if ((t==1 || t%%5 == 0)){ 


     #TODO: figure out how to calculate Moran's G based on variable values, not simply on location clustering
#    #calculate metrics on resulting dataset
    G.1 = c(G.1, Moran(rasterize(SpatialPoints(all.pops[all.pops$pop == 'p1', c('x', 'y')]), env))) #Moran's G (or some autocorrelation metric)
    G.2 = c(G.2, Moran(rasterize(SpatialPoints(all.pops[all.pops$pop == 'p2', c('x', 'y')]), env))) #Moran's G (or some autocorrelation metric)
    if (nrow(all.pops[all.pops$pop == 'h',])>0){
      G.h = c(G.h, Moran(rasterize(SpatialPoints(all.pops[all.pops$pop == 'h', c('x', 'y')]), env))) #Moran's G (or some autocorrelation metric)
    }

     #G = c(G, Moran(rasterize(x = all.pops[,c('x', 'y')], y = env, field = as.numeric(all.pops$pop))))
#
#    #estimate of n number of pops in resulting dataset (using Geneland)
#    #k = print()  #REMOVE print(); how to do using Geneland??
#
#    #Fst for the n estimated pops in the resulting dataset (using Geneland)
    #Fst = Fstat(all.pops[, c('a1', 'a2')], 2, as.numeric(gsub('h', 3, gsub('p', '', all.pops$pop))), 3)
#    #Fst = Fstat(all.pops, 2, all.pops$pop, 2 ) #figure out how to extract Fst value from resulting data structure
      #Fst = c(Fst, mean(Fst(as.loci(gen.ind))[,'Fst']))

  #create genind object from data
  all.pops.2 = all.pops[,c('x', 'y')]
  for (locus in 1:N.LOCI){
    all.pops.2[toupper(my.letters[locus])] = paste(all.pops[,allele.cols[(locus-1)*2+1]], all.pops[,allele.cols[(locus-1)*2+2]], sep = ',')
  }
  all.pops.2$pop = extract(hab, all.pops.2[,c('x','y')])
  gen.ind = df2genind(as.matrix(all.pops.2[toupper(my.letters[1:N.LOCI])]), sep = ',', ncode =2, pop = extract(hab, all.pops.2[,c('x','y')]))
  if(debug){assign('gen.ind', gen.ind, envir = .GlobalEnv)}
  #poppr(gen.ind)
  #H.obs = summary(gen.ind)$Hobs
  #H.exp = summary(gen.ind)$Hexp
  #Fst.2 = c(Fst.2, pairwise.fst(gen.ind)[1])
  Gst = c(Gst, Gst_Hedrick(gen.ind)$global)

#    
#    diseq_values = list()
#    for (locus in 1:N.LOCI) {
#      diseq.p.values[[my.letters[locus]]] = HWE.test(makeGenotypes(all.pops, convert = allele.pairs)[, paste(my.letters[locus], '1/', my.letters[locus], '2', sep = '')])$test$p.value
#      #diseq.values[[my.letters[locus]]] = diseq(makeGenotypes(all.pops, convert = allele.pairs)[, paste(my.letters[locus], '1/', my.letters[locus], '2', sep = '')])
#    }
#

  prop.h = c(prop.h, (nrow(all.pops[all.pops$pop == 'h',])/(nrow(all.pops))))
  }
 }

 if(!running.plot){ 
   #add resulting dataset to tiled plots
    par(mar = c(1,1,1,1))

    plot(env, col = ramp(5), main = list(sprintf('Ending locations; p.cross = %0.4f', p.cross), cex = CEX),
         cex.lab = CEX, cex.axis = CEX, axis = F)
    lines(hab.x, hab.y, lwd = 1.5)
    points(all.pops[, c('x', 'y')], bg = all.pops$pop, pch = PCH, fg = FG, cex = CEX)

 }


    assign('p', p.cross, envir = .GlobalEnv)
    assign('all.pops', all.pops, envir = .GlobalEnv)

#write data to csv file, with two line header containing:
    #line 1: echo of command-line args
    #line 2: csv header
#and data containing:
    #some dataframe resulting from an ldply() call on the list of simulated pops for all p.cross values
#NOTE: this file will allow me to run the model multiple times, varying whichever command-line args of
    #interest, and then analyze how those args influence output as well


    write.csv(all.pops, sprintf('all.pops_%0.4f.csv', p.cross), row.names = F)

    #Add metric vectors to list of results
  #return(list('G.1' = G.1, 'G.2' = G.2, 'G.h' = G.h, 'Gst' = Gst, 'Fst' = Fst, 'Fst.2' = Fst.2, 'prop.h' = prop.h))
  return(list('G.1' = G.1, 'G.2' = G.2, 'G.h' = G.h, 'Gst' = Gst, 'prop.h' = prop.h))

}




START.POPS = sim.pop(n.loci = N.LOCI, size.pop = SIZE.POP, for.avg = FOR.AVG)

START.POPS = burn.in(start.pops = START.POPS, size.pop = SIZE.POP, mean.d.move = MEAN.D.MOVE, for.avg = FOR.AVG)












results = list()

#And create timestep vector (for plotting output)
TIME = c(1,seq(1:N.TIME)[which(seq(1:N.TIME) %% 5 ==0)])








#Create device for plotting maps of populations and plot starting population
if (!running.plot){
  if(!PDF){
dev.new()}
  else{pdf('output.pdf')}
    

#par(mfrow = c((1+length(p.cross) + (1+length(p.cross))%%2)/2, 2), oma = c(0,0,2,0))
par(mfrow = c((1+length(p.cross) + (1+length(p.cross))%%2)/2, 2))
    
par(mar = c(1,1,1,1))    

plot(env, col = ramp(5), main = list('Starting locations', cex = CEX), cex.lab = CEX, cex.axis = CEX)
lines(hab.x, hab.y, lwd = 1.5)
points(START.POPS[['p1']][[1]][, c('x', 'y')], bg = palette()[1], pch = PCH, fg = FG, cex = CEX)
points(START.POPS[['p2']][[1]][, c('x', 'y')], bg = palette()[2], pch = PCH, fg = FG, cex = CEX)

}











#for (p in p.cross){
#
#  results[[as.character(p)]] = core.model(p.cross = p,
#                                          start.pops = START.POPS, 
#                                          n.time = N.TIME, 
#                                          size.pop = SIZE.POP, 
#                                          mean.d.move = MEAN.D.MOVE, 
#                                          for.avg = FOR.AVG, 
#                                          repro.cycle = REPRO.CYCLE, 
#                                          d.pair = D.PAIR,
#                                          n.loci = N.LOCI, 
#                                          fit.advntg = FIT.ADVNTG,
#                                          mean.off = MEAN.OFF,
#                                          sd.off = SD.OFF,
#                                          mean.disp.dist = MEAN.DISP.DIST, 
#                                          sd.disp.dist = SD.DISP.DIST)
#
#   # #add resulting dataset to tiled plots
#   # par(mar = c(1,1,1,1))
#
#   # plot(env, main = sprintf('Ending locations; p.value = %0.2f', p))
#   # lines(hab.x, hab.y)
#   # points(all.pops[, c('x', 'y')], col = all.pops$pop, pch = 19)
#
#
#}




results[[as.character(p.cross)]] = core.model(p.cross = p.cross,
                                        start.pops = START.POPS, 
                                        n.time = N.TIME, 
                                        size.pop = SIZE.POP, 
                                        mean.d.move = MEAN.D.MOVE, 
                                        for.avg = FOR.AVG, 
                                        repro.cycle = REPRO.CYCLE, 
                                        d.pair = D.PAIR,
                                        n.loci = N.LOCI, 
                                        fit.advntg = FIT.ADVNTG,
                                        mean.off = MEAN.OFF,
                                        sd.off = SD.OFF,
                                        mean.disp.dist = MEAN.DISP.DIST, 
                                        sd.disp.dist = SD.DISP.DIST)

 # #add resulting dataset to tiled plots
 # par(mar = c(1,1,1,1))

 # plot(env, main = sprintf('Ending locations; p.value = %0.2f', p))
 # lines(hab.x, hab.y)
 # points(all.pops[, c('x', 'y')], col = all.pops$pop, pch = 19)












#metrics = c('Gst', 'Fst', 'prop.h')
metrics = c('prop.h', 'G.1', 'G.2', 'Gst', 'Fst', 'Fst.2')

#max.prop.h = 0
#for (p in p.cross) { if (max(results[[as.character(p)]]$prop.h) > max.prop.h){max.prop.h = max(results[[as.character(p)]]$prop.h)}}

for (metric in metrics){

  #pdf(sprintf('%s.pdf', metric))
  
  colors = rainbow(length(p.cross))
  for(p in 1:length(p.cross)){
    if(p == 1){
      #plot(TIME, results[[as.character(p.cross[p])]][[metric]], type = 'l', lty = p, col = colors[p], lwd = 2,
      #if (metric == 'prop.h') {
      #plot(TIME, results[[as.character(p.cross[p])]][[metric]], type = 'l', col = colors[p], lwd = 1.25, ymax = c(0,max.prop.h),
           #xlab = 'model time (timesteps)', ylab = metric, cex.lab = CEX, cex.axis = CEX,
           #main = list(sprintf('%s as a function of model time, for %i values of p.cross', metric, length(p.cross)), cex = CEX))
      #}
      #else {
      plot(TIME, results[[as.character(p.cross[p])]][[metric]], type = 'l', col = colors[p], lwd = 1.25,
           xlab = 'model time (timesteps)', ylab = metric, cex.lab = CEX, cex.axis = CEX, ylim = c(0,1),
           main = list(sprintf('%s as a function of model time, for %i values of p.cross', metric, length(p.cross)), cex = CEX))
      #}

    }
    else{
      lines(TIME, results[[as.character(p.cross[p])]][[metric]], col = colors[p], lwd = 1.25)
      #lines(TIME, results[[as.character(p.cross[p])]][[metric]], lty = p, col = colors[p], lwd = 2)
    }
  }
  legend('bottomright', legend = as.character(p.cross), 
         #lty = seq(length(p.cross)), 
         lwd = rep(1.25, length(p.cross)),  
         col = colors, cex = CEX)


  #dev.off()


}

if(!running.plot){
  dev.off()
}
