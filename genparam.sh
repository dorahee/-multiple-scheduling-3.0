#!/bin/bash

### run this as follows:

### sh genparam.sh > PLIST

# household == 9 cases (50, 100, 500, 1000, 2000, 4000, 6000, 8000, 10000)
# dependent ==  4 cases (0, 3, 6, 9)
# penalty   == 5 cases (1, 1, 1, 1, 1)

for h in 1000
do
  for p in 1
  do
     for d in 0 3 9
     do
        echo "$h $p $d"
     done
  done
done

exit 0
