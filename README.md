# RO_PUF_analysis
Hardware Security HW2

Problem 1:
Required libraries to run hw2_p1.py: python 3.6, numpy, pandas, matplotlib, mpl_toolkits
F: Based on the inter and intra hamming distance histogram, this PUF would be useful for chip identification because the mean of inter hamming distance is 118.3 out of 256 which is very close to 50%.
H: The distribution is slightly better than the previous one but still has an obvious pattern.
I: Based on the results, a better method for selecting RO pairs would be random selecting non-overlapping RO pairs instead of using a fixed pattern.
Problem 2:
A: System integrators would be interested in exploiting a hardware IP for overusage and cloning. Foundry would also be interested in overproduction and reverse engineering.
B: Watermarking provides ownership information that is hidden in the circuit and does not alter the function of the circuit. However, obfuscation denies unlicensed usage. The hardware will be usable only after applying a specific input sequence or key.

