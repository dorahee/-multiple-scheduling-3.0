#!/bin/bash

### run this as follows:

### sh genparam.sh > PLIST

# household == 9 cases (50, 100, 500, 1000, 2000, 4000, 6000, 8000, 10000)
# dependent ==  4 cases (0, 3, 6, 9)
# penalty   == 5 cases (1, 1, 1, 1, 1)

for h in 5000
do
  for d in 0 3 6 9
  do
     for p in 1 1 1 1 1
     do
        echo "$h $d $p"
     done
  done
done

exit 0
