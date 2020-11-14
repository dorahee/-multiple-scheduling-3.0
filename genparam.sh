#!/bin/bash

### run this as follows:

### sh genparam.sh > PLIST

# household == 10 cases (50, 100, 500, 1000, 2000, 4000, 6000, 8000, 10000, 15000)
# dependent ==  4 cases (0, 3, 6, 9)
# penalty   == 10 cases (1, 10, 50, 100, 500, 1000, 5000)

for h in 50 100 500 1000 2000 4000 6000 8000 10000 15000
do
  for d in 0 3 6 9
  do
     for p in 1 10 50 100 500 1000 5000
     do
        echo "$h $d $p"
     done
  done
done

exit 0
