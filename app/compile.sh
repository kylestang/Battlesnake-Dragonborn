rm decision.so
gcc -O3 -fopenmp -shared -Wall -g -o decision.so -fPIC *.c
