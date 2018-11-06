################################################################################
#                                                                              #
#  GENERATE MOVIES FROM SIMULATION OUTPUT                                      #
#                                                                              #
################################################################################

import hdf5_to_dict as io
import plot as bplt
from analysis_fns import *
import util

import sys; sys.dont_write_bytecode = True
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import os
import pickle

# Movie size in inches. Keep 16/9 for standard-size movies
FIGX = 16
FIGY = FIGX*9/16

# For plotting debug, "array-space" plots
# Certain plots can override this below
USEARRSPACE = False

MAD = True
LOG_MDOT = False
LOG_PHI = False

# Choose between several predefined layouts below
# For keeping around lots of possible movies with same infrastructure
# simplest simpler simple traditional e_ratio conservation floors
movie_type = "traditional"

FRAMEDIR = "FRAMES"

# Load diagnostic data from post-processing (eht_out.p)
diag_post = True

def plot(n):
  imname = os.path.join(FRAMEDIR, 'frame_%08d.png' % n)
  print '%08d / ' % (n+1) + '%08d' % len(files)

  fig = plt.figure(figsize=(FIGX, FIGY))

  if movie_type not in ["simplest", "simpler", "simple"]:
    dump = io.load_dump(files[n], hdr, geom, derived_vars=True, extras=False)
    fig.suptitle("t = %d"%dump['t']) # TODO put this at the bottom somehow?
  else:
    # Simple movies don't need derived vars
    dump = io.load_dump(files[n], hdr, geom, derived_vars=False, extras=False)

  # Zoom in for SANEs
  if MAD:
    window = [-40,40,-40,40]
    nlines = 20
    rho_l, rho_h = -3, 2
  else:
    window = [-20,20,-20,20]
    nlines = 5
    rho_l, rho_h = -3, 1

  if movie_type == "simplest":
    # Simplest movie: just RHO
    ax_slc = plt.subplots(1,2)
    bplt.plot_slices(ax_slc[0], ax_slc[1], dump, np.log10(dump['RHO']),
                     label=r"$\log_{10}(\rho)$", vmin=rho_l, vmax=rho_h, window=window, cmap='jet')
  elif movie_type == "simpler":
    # Simpler movie: RHO and phi
    gs = gridspec.GridSpec(2, 2, height_ratios=[6, 1], width_ratios=[16,17])
    ax_slc = [fig.subplot(gs[0,0]), fig.subplot(gs[0,1])]
    ax_flux = [fig.subplot(gs[1,:])]
    bplt.plot_slices(ax_slc[0], ax_slc[1], dump, np.log10(dump['RHO']),
                     label=r"$\log_{10}(\rho)$", vmin=rho_l, vmax=rho_h, window=window, cmap='jet')
    bplt.diag_plot(ax_flux[0], diag, 'phi', dump['t'], ylabel=r"$\phi_{BH}$", logy=LOG_PHI, xlabel=False)
  elif movie_type == "simple":
    # Simple movie: RHO mdot phi
    gs = gridspec.GridSpec(3, 2, height_ratios=[4, 1, 1])
    ax_slc = [fig.subplot(gs[0,0]), fig.subplot(gs[0,1])]
    ax_flux = [fig.subplot(gs[1,:]), fig.subplot(gs[2,:])]
    bplt.plot_slices(ax_slc[0], ax_slc[1], dump, np.log10(dump['RHO']),
                     label=r"$\log_{10}(\rho)$", vmin=rho_l, vmax=rho_h, window=window, cmap='jet')
    bplt.diag_plot(ax_flux[0], diag, 'mdot', dump['t'], ylabel=r"$\dot{M}$", logy=LOG_MDOT)
    bplt.diag_plot(ax_flux[1], diag, 'phi', dump['t'], ylabel=r"$\phi_{BH}$", logy=LOG_PHI)
  else: # All other movie types share a layout
    ax_slc = lambda i: plt.subplot(2, 4, i)
    ax_flux = lambda i: plt.subplot(4, 2, i)
    if movie_type == "traditional":
      # Usual movie: RHO beta fluxes
      # CUTS
      bplt.plot_slices(ax_slc(1), ax_slc(2), dump, np.log10(dump['RHO']),
                       label=r"$\log_{10}(\rho)$", vmin=-3, vmax=2, cmap='jet')
      bplt.plot_slices(ax_slc(5), ax_slc(6), dump, np.log10(dump['beta']),
                       label=r"$\beta$", vmin=-2, vmax=2, cmap='RdBu_r')
      # FLUXES
      bplt.diag_plot(ax_flux(2), diag, 'mdot', dump['t'], ylabel=r"$\dot{M}$", logy=LOG_MDOT)
      bplt.diag_plot(ax_flux(4), diag, 'phi', dump['t'], ylabel=r"$\phi_{BH}$", logy=LOG_PHI)
      # Mixins:
      # Zoomed in RHO
      bplt.plot_slices(ax_slc(7), ax_slc(8), dump, np.log10(dump['RHO']),
                       label=r"$\log_{10}(\rho)$", vmin=-3, vmax=2, window=[-10,10,-10,10], field_overlay=False)
      # Bsq
#       bplt.plot_slices(ax_slc[6], ax_slc[7], dump, np.log10(dump['bsq']),
#                        label=r"$b^2$", vmin=-5, vmax=0, cmap='Blues')
      # Failures: all failed zones, one per nonzero pflag
#       bplt.plot_slices(ax_slc[6], ax_slc[7], dump, dump['fail'] != 0,
#                        label="Failed zones", vmin=0, vmax=20, cmap='Reds', int=True) #, arrspace=True)
      # 2D histograms
#       bplt.hist_2d(ax_slc[6], np.log10(dump['RHO']), np.log10(dump['UU']),r"$\log_{10}(\rho)$", r"$\log_{10}(U)$", logcolor=True)
#       bplt.hist_2d(ax_slc[7], np.log10(dump['UU']), np.log10(dump['bsq']),r"$\log_{10}(U)$", r"$b^2$", logcolor=True)
      
      # Extra fluxes:
#       bplt.diag_plot(ax_flux[1], diag, dump, 'edot', r"\dot{E}", logy=LOG_PHI)
    elif movie_type == "e_ratio":
      # Energy ratios: difficult places to integrate, with failures
      bplt.plot_slices(ax_slc[0], ax_slc[1], dump, np.log10(dump['UU']/dump['RHO']),
                       label=r"$\log_{10}(U / \rho)$", vmin=-3, vmax=3, average=True)
      bplt.plot_slices(ax_slc[2], ax_slc[3], dump, np.log10(dump['bsq']/dump['RHO']),
                       label=r"$\log_{10}(b^2 / \rho)$", vmin=-3, vmax=3, average=True)
      bplt.plot_slices(ax_slc[4], ax_slc[5], dump, np.log10(1/dump['beta']),
                       label=r"$\beta^{-1}$", vmin=-3, vmax=3, average=True)
      bplt.plot_slices(ax_slc[6], ax_slc[7], dump, dump['fail'] != 0,
                       label="Failures", vmin=0, vmax=20, cmap='Reds', int=True) #, arrspace=True)
    elif movie_type == "conservation":
      # Continuity plots to verify local conservation of energy, angular + linear momentum
      # Integrated T01: continuity for momentum conservation
      bplt.plot_slices(ax_slc[0], ax_slc[1], dump, Tmixed(dump, 1, 0),
                       label=r"$T^1_0$ Integrated", vmin=0, vmax=600, arrspace=True, integrate=True)
      # integrated T00: continuity plot for energy conservation
      bplt.plot_slices(ax_slc[4], ax_slc[5], dump, np.abs(Tmixed(dump, 0, 0)),
                       label=r"$T^0_0$ Integrated", vmin=0, vmax=3000, arrspace=True, integrate=True)

      # Usual fluxes for reference
      bplt.diag_plot(ax_flux[1], diag, 'mdot', dump['t'], ylabel=r"$\dot{M}$", logy=LOG_MDOT)
      #bplt.diag_plot(ax_flux[3], diag, 'phi', dump['t'], ylabel=r"$\phi_{BH}$", logy=LOG_PHI)

      # Radial conservation plots
      E_r = sum_shell(geom,Tmixed(dump,0,0))
      Ang_r = sum_shell(geom,Tmixed(dump,0,3))
      mass_r = sum_shell(dump['ucon'][:,:,:,0]*dump['RHO'])

      # TODO arrange legend better -- add labels when radial/diag plotting
      bplt.radial_plot(ax_flux[3], np.abs(E_r), 'Conserved vars at R', ylim=(0,1000), rlim=(0,20), arrayspace=True)
      bplt.radial_plot(ax_flux[3], np.abs(Ang_r)/10, '', ylim=(0,1000), rlim=(0,20), col='r', arrayspace=True)
      bplt.radial_plot(ax_flux[3], np.abs(mass_r),   '', ylim=(0,1000), rlim=(0,20), col='b', arrayspace=True)
      
      # Radial energy accretion rate
      Edot_r = sum_shell(geom, Tmixed(dump,1,0))
      bplt.radial_plot(ax_flux[5], np.abs(Edot_r), 'Edot at R', ylim=(0,200), rlim=(0,20), arrayspace=True)

      # Radial integrated failures
      bplt.radial_plot(ax_flux[7], (dump['fail'] != 0).sum(axis=(1,2)), 'Fails at R', arrayspace=True, rlim=[0,50], ylim=[0,1000])

    elif movie_type == "floors":
      # TODO add measures of all floors' efficacy.  Record ceilings in header or extras?
      bplt.plot_slices('sigma ceiling', dump['bsq']/dump['RHO'] - 100, dump, -100, 100, 5, cmap='RdBu_r')
      bplt.diag_plot(ax, diag, dump, 'sigma_max', 'sigma_max')

  # TODO enlarge plots w/o messing up even pixel count
  pad = 0.05
  plt.subplots_adjust(left=2*pad, right=1-2*pad, bottom=pad, top=1-pad)

  plt.savefig(imname, dpi=1920/FIGX)
  plt.close(fig)

if __name__ == "__main__":
  # PROCESS ARGUMENTS
  if sys.argv[1] == '-d':
    debug = True
    path = sys.argv[2]
  else:
    debug = False
    path = sys.argv[1]
  
  # LOAD FILES
  files = io.get_dumps_list(path)
  if len(files) == 0:
      util.warn("INVALID PATH TO DUMP FOLDER")
      sys.exit(1)

  util.make_dir(FRAMEDIR)

  hdr = io.load_hdr(files[0])
  geom = io.load_geom(hdr, path)

  if diag_post:
    # Load fluxes from post-analysis: more flexible
    diag = pickle.load(open("eht_out.p", 'rb'))
  else:
    # Load diagnostics from HARM itself
    diag = io.load_log(path)

  nthreads = util.calc_nthreads(hdr)
  if debug:
    # Run sequentially to make backtraces work
    for i in range(len(files)):
      plot(i)
  else:
    util.run_parallel(plot, len(files), nthreads)
