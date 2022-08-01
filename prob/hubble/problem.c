/******************************************************************************
 *                                                                            *
 * PROBLEM.C                                                                  *
 *                                                                            *
 * INITIAL CONDITIONS FOR HUBBLE TEST                                         *
 *                                                                            *
 ******************************************************************************/

#include "decs.h"
#include "hdf5_utils.h"

static double rho0;
static double v0;
static double ug0;
static int set_tlim;
static double dyntimes;

void set_problem_params()
{
  set_param("rho0", &rho0);
  set_param("v0", &v0);
  set_param("ug0", &ug0);
  set_param("set_tlim", &set_tlim);
  set_param("dyntimes", &dyntimes);
}

void save_problem_data(hid_t string_type){
        hdf5_write_single_val("hubble", "PROB", string_type);
        hdf5_write_single_val(&rho0, "rho0", H5T_IEEE_F64LE);
        hdf5_write_single_val(&v0, "v0", H5T_IEEE_F64LE);
        hdf5_write_single_val(&ug0, "ug0", H5T_IEEE_F64LE);
        hdf5_write_single_val(&set_tlim, "set_tlim", H5T_STD_I32LE);
        hdf5_write_single_val(&dyntimes, "dyntimes", H5T_IEEE_F64LE);
}

void get_prim_hubble(int i, int j, int k, GridPrim P)
{
    P[RHO][k][j][i] = rho0;
    P[UU][k][j][i]  = ug0;
    P[U1][k][j][i]  = v0;
}

void init(struct GridGeom *G, struct FluidState *S)
{
  set_grid(G);
  if (set_tlim == 1) tf = dyntimes / v0;
  LOG("Set grid");

  ZLOOPALL {
    get_prim_hubble(i, j, k, S->P);
  } // ZLOOP

  //Enforce boundary conditions
  set_bounds(G, S);
}
