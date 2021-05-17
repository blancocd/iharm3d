#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

source ../test_common.sh

PROB=${1:-torus}

# Must be just a name for now
OUT_DIR=results_$PROB

# Initial clean and make of work area
rm -rf build_archive param.dat harm
make_harm_here $PROB

rm -rf $OUT_DIR
mkdir -p $OUT_DIR

# Give the system a reasonable size to limit runtime
# Bondi problem is 2D
if [ "$PROB" == "bondi" ]; then
  set_problem_size 128 128 1
else
  set_problem_size 96 32 16
fi

# Give a relatively short endpoint
# We're testing init and basic propagation
set_run_dbl tf 1.0
set_run_dbl DTd 1.0
if [ $PROB == "torus" ]
then
  set_run_dbl u_jitter 0.0
fi

for i in 0 1
do

  rm -rf $OUT_DIR/dumps $OUT_DIR/restarts $OUT_DIR/*.h5

  set_cpu_topo 1 1 1

  make_harm_here $PROB

  if [ $PROB == "torus" ]
  then 
    set_run_int mad_type $i
    echo "First run of $PROB problem, mad_type $i..."
  elif [ $PROB == "mhdmodes" ]
  then
    echo "First run of $PROB problem, mode $i..."
  else
    echo "First run of $PROB problem..."
  fi
  run_harm $OUT_DIR firsttime
  echo "Done!"

  cd $OUT_DIR
  mv dumps/dump_00000000.h5 ./first_dump_gold.h5
  if [ $PROB == "mhdmodes" ]; then
    mv dumps/dump_00000005.h5 ./last_dump_gold.h5
  else
    mv dumps/dump_00000001.h5 ./last_dump_gold.h5
  fi
  mv restarts/restart_00000001.h5 ./first_restart_gold.h5
  rm -rf dumps restarts
  cd ..

  sleep 1

  echo "Second run..."
  run_harm $OUT_DIR secondtime
  echo "Done!"

  verify $PROB

done
