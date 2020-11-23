rm decision.so
gcc -O3 -shared -fopenmp -Wall -g -o decision.so -fPIC *.c
