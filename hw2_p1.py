import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
# get_ipython().run_line_magic('matplotlib', 'inline')

# Problem A: Load all FPGA data

data_path = "fullFreqData"

filenames = [filename for filename in sorted(os.listdir(data_path))] 
FPGAs = {}

for filename in filenames:
    if filename.endswith(".csv"):
        file_path = os.path.join(data_path,filename)
        raw_data = pd.read_csv(file_path, sep=',', header=None)
        FPGAs[filename] = raw_data

# Problem B: Plot the mean of average RO frequency

avg_ROfreq = {}

for key,value in FPGAs.items():
    avg_ROfreq[key] = np.mean(value, axis=1)

avg_ROfreq_list = []

for _,value in avg_ROfreq.items():
    avg_ROfreq_list.append(value)

mean_ROfreq_across_FPGAs = np.mean(np.asarray(avg_ROfreq_list), axis=0)
mean_ROfreq_mapping = mean_ROfreq_across_FPGAs.reshape(32,16)

print("Problem B: Figure 1")
fig1 = plt.figure(1)
plt.pcolor(mean_ROfreq_mapping, cmap=cm.rainbow)
plt.colorbar(orientation='vertical')
plt.show()


X = np.arange(0, 16)
Y = np.arange(0, 32)
X, Y = np.meshgrid(X, Y)

print("Problem B: Figure 2")
fig2 = plt.figure(2)
ROfreq_plot_3d = fig2.gca(projection='3d')
surf = ROfreq_plot_3d.plot_surface(X, Y, mean_ROfreq_mapping, cmap=cm.rainbow)
fig2.colorbar(surf)
plt.show()

# Problem C: Compute PUF response

# helper functions
def bin_to_dec(binary):
    dec = 0
    for i in range(len(binary)):
        dec += binary[i]*2**(len(binary)-1-i)
    return dec

def PUF_response(hex_dict,bin_dict,RO_freqs,skip=1):
    if isinstance(RO_freqs,dict):
        for key,value in RO_freqs.items():
            PUF_resp = [1 if value[i+j]>value[(i+j+skip)%512] else 0 for j in range(skip) for i in range(0,512,skip*2)]
            bin_dict[key] = PUF_resp
            hex_dict[key] = hex(bin_to_dec(PUF_resp))
    else:
        for value in RO_freqs:
            PUF_resp = [1 if value[i+j]>value[(i+j+skip)%512] else 0 for j in range(skip) for i in range(0,512,skip*2)]
            bin_dict.append(PUF_resp)
            hex_dict.append(hex(bin_to_dec(PUF_resp)))

PUF_response_hex = {}
PUF_response_bin = {}    
PUF_response(PUF_response_hex, PUF_response_bin, avg_ROfreq)

print("Problem C: The 256-bit PUF response is ", PUF_response_hex)

# Problem D: Plot the response from "C"

PUF_response_avg = []

for value in PUF_response_bin.values():
    PUF_response_avg.append(value)

PUF_response_avg = np.mean(np.asarray(PUF_response_avg), axis=0)
PUF_response_avg = PUF_response_avg.reshape(32,8)

print("Problem D: Figure 3")
fig3 = plt.figure(3)
plt.pcolor(PUF_response_avg, cmap=cm.rainbow)
plt.colorbar(orientation='vertical')
plt.show()

# Problem E: Compute and plot the inter Hamming distance from "C"

def hd(value1, value2):
    hd_cnt = 0
    xor_res = int(value1,base=16) ^ int(value2,base=16)
    for i in range(256):
        xor_res = xor_res >> 1
        if xor_res % 2 == 1:
            hd_cnt += 1
    return hd_cnt


hamming_distance = []
used_key = []

for key1,value1 in PUF_response_hex.items():
    used_key.append(key1)
    for key2,value2 in PUF_response_hex.items():
        if key2 not in used_key:
            hamming_distance.append(hd(value1,value2))

hamming_distance = np.asarray(hamming_distance)
print("Problem E: Figure 4 inter-HD histogram")
fig4 = plt.figure(4)
plt.hist(hamming_distance)
plt.show()

hamming_distance_mean = np.mean(hamming_distance) 
hamming_distance_std = np.std(hamming_distance)
print("Problem E: Mean of the Hamming distance is: ", hamming_distance_mean)
print("           Standard deviation of the Hamming distance is: ", hamming_distance_std)

# Problem F: Compute and plot intra Hamming distance

# Compute PUF response for 100 measurements in all FPGAs
PUF_response_all_FPGA_hex = [[] for i in range(193)]
PUF_response_all_FPGA_bin = [[] for i in range(193)]    

i = 0
for key,value in FPGAs.items():
    value_list = list(np.asarray(value).T)
    PUF_response(PUF_response_all_FPGA_hex[i], PUF_response_all_FPGA_bin[i], value_list)
    i += 1   

# Calculate average intra-HD

used_resp = []
intra_hd = []
fpga_idx = 0
animation = ['.  ','.. ','...']
for responses in PUF_response_all_FPGA_hex:
    print("calculating intra-HD for FPGA[{0}/193] {1}".format(fpga_idx+1, animation[fpga_idx%3]), end='\r')
    fpga_idx += 1
    for resp1 in responses:
        used_resp.append(resp1)
        for resp2 in responses:
            if resp2 not in used_resp: 
                intra_hd.append(hd(resp1, resp2))

intra_hd = np.asarray(intra_hd)
print("Problem F: Figure 5 intra-HD histogram")
fig5 = plt.figure(5)
plt.hist(intra_hd)
plt.show()

intra_hd_mean = np.mean(intra_hd) 
intra_hd_std = np.std(intra_hd)
print("Problem F: Mean of the intra Hamming distance is: ", intra_hd_mean)
print("           Standard deviation of the intra Hamming distance is: ", intra_hd_std)

# Problem G: Compute PUF response by forming a non-overlapping set of RO pairs using
# the following methodology RO1 with RO17, RO2 with RO18, etc.

PUF_response_hex_skip16 = {}
PUF_response_bin_skip16 = {}
PUF_response(PUF_response_hex_skip16, PUF_response_bin_skip16, avg_ROfreq, skip=16)

# Problem H: plot the new average PUF response

PUF_response_all_FPGA_bin_skip16 = []

for value in PUF_response_bin_skip16.values():
    PUF_response_all_FPGA_bin_skip16.append(value)
    
PUF_response_all_FPGA_bin_skip16 = np.asarray(PUF_response_all_FPGA_bin_skip16)
PUF_response_avg_skip16 = np.mean(PUF_response_all_FPGA_bin_skip16, axis=0).reshape(32,8)

print("Problem H: Figure 6")
fig6 = plt.figure(6)
plt.pcolor(PUF_response_avg_skip16, cmap=cm.rainbow)
plt.colorbar(orientation='vertical')
plt.show()

# Problem I: Compute and plot inter Hamming distance

hd_inter_skip16 = []
used_key_skip16 = []

for key1,value1 in PUF_response_hex_skip16.items():
    used_key_skip16.append(key1)
    for key2,value2 in PUF_response_hex_skip16.items():
        if key2 not in used_key_skip16:
            hd_inter_skip16.append(hd(value1,value2))

hd_inter_skip16 = np.asarray(hd_inter_skip16)
print("Problem I: Figure 7 inter-HD histogram")
fig7 = plt.figure(7)
plt.hist(hd_inter_skip16)
plt.show()

hd_inter_skip16_mean = np.mean(hd_inter_skip16) 
hd_inter_skip16_std = np.std(hd_inter_skip16)
print("Problem I: Mean of the Hamming distance is: ", hd_inter_skip16_mean)
print("           Standard deviation of the Hamming distance is: ", hd_inter_skip16_std)

