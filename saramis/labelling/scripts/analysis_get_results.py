# coding = utf-8

"""
Code to replicate results in SARAMIS
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

### AMOS
df_old_f = pd.read_csv("./amos_old.csv")
df_new_f  = pd.read_csv("./amos_new.csv")


df_data_old = df_old_f[df_old_f.columns[4:].tolist()]
df_data_new = df_new_f[df_new_f.columns[4:].tolist()]
df_diff = df_data_new.values - df_data_old.values
df_data_pixels_amos = df_new_f[df_new_f.columns[1:4].tolist()]
df_diff_amos = df_diff
df_data_new_exist = df_data_new>1
abs_num = df_data_new_exist.sum(axis=0)
num_organs_amos = abs_num.values.tolist()

print("Number of organs in amos: ", np.sum(num_organs_amos))
print("Number of pixels corrected: ", np.abs(df_diff_amos).sum().sum())
print("Mean voxel size for amos; ", df_data_pixels_amos.abs().mean(axis=0))

### Abdomen-1k
df_old_f = pd.read_csv("./abdomen_old.csv")
df_new_f  = pd.read_csv("./abdomen_new.csv")

df_data_old = df_old_f[df_old_f.columns[4:].tolist()]
df_data_new = df_new_f[df_new_f.columns[4:].tolist()]
df_diff = df_data_new.values - df_data_old.values
df_data_pixels_abdomen = df_new_f[df_new_f.columns[1:4].tolist()]
df_diff_abd = df_diff
df_data_new_exist = df_data_new>1
abs_num = df_data_new_exist.sum(axis=0)
num_organs_abd = abs_num.values.tolist()

print("Number of organs in abdomen1k: ", np.sum(num_organs_abd))
print("Number of pixels corrected: ", np.abs(df_diff_abd).sum().sum())
print("Mean voxel size for abdomen; ", df_data_pixels_abdomen.abs().mean(axis=0))


arr_calc = np.vstack([df_diff_abd, df_diff_amos])
arr_calc = np.abs(arr_calc)

arr_calc_abd = np.abs(df_diff_abd)
arr_calc_amos = np.abs(df_diff_amos)
arr_calc_abd_no = np.sum(np.sum(arr_calc_abd, axis=1)==0)
arr_calc_amos_no = np.sum(np.sum(arr_calc_amos, axis=1)==0)

print("Number of scans that weren't corrected abdomen1k: ", arr_calc_abd_no)
print("Number of scans that weren't corrected amos: ", arr_calc_amos_no)

# scans where there are corrections
arr_calc_positive = np.sum(arr_calc, axis=1) >0
# NUmber of scans that are corrected = 
print("Number of scans that are corrected: ", np.sum(arr_calc_positive))
# Where corrections are necessary, how many voxels are corrected?
arr_calc_corrected = arr_calc[arr_calc_positive]
from scipy import stats
print("Median number of voxels corrected where corrections are necessary: ", np.median(arr_calc_corrected.sum(axis=1)))
print("IQR of voxels corrected where corrections are necessary: ", np.percentile(arr_calc_corrected.sum(axis=1), [25, 75]))
# Where corrections are necessary, how many structures are corrected?
arr_structure_corrected = (arr_calc_corrected>0).astype(np.int32)
print("Mean number of structures corrected where corrections are necessary: ", np.mean(arr_structure_corrected.sum(axis=1)))

print("IQR of structures corrected where corrections are necessary: ", np.percentile(arr_structure_corrected.sum(axis=1), [25, 75]))
num_corrections_organ_type = (arr_structure_corrected.sum(axis=0)).tolist()
cols = df_old_f.columns[4:].tolist()
print("Max number of corrections: ", np.max(num_corrections_organ_type), "organ: ", cols[np.argmax(num_corrections_organ_type)])
print("Min number of corrections: ", np.min(num_corrections_organ_type), "organ: ", cols[np.argmin(num_corrections_organ_type)])

min_vals = np.argwhere(num_corrections_organ_type == np.min(num_corrections_organ_type)).flatten().tolist()
print("Organs with min number of corrections: ", [cols[i] for i in min_vals])

### TOTAL
df_old = pd.read_csv("./total.csv")

df_data_pixels_total = df_old[df_old.columns[1:4].tolist()]
df_data_new_exist = df_data_new>1
abs_num = df_data_new_exist.sum(axis=0)
num_organs_tot = abs_num.values.tolist()

print("Number of organs in total: ", np.sum(num_organs_tot))
print("Mean pixel size for total; ", df_data_pixels_total.abs().mean(axis=0))


### Plotting
# Abs difference
df_diff_abs = np.abs(df_diff)
df_mean = np.mean(df_diff_abs, axis=0)
df_mean_scan = np.mean(df_diff_abs, axis=1)
df_std = np.mean(df_diff, axis=0)

list_cols = df_data_new.columns.tolist()

print("Mean pixel size: ", np.abs(np.vstack([df_data_pixels_amos.values, df_data_pixels_total.values, df_data_pixels_abdomen   ])).mean(axis=0))
print("Mean pixel size: ", np.abs(np.vstack([df_data_pixels_amos.values, df_data_pixels_total.values, df_data_pixels_abdomen   ])).std(axis=0))


organs_corrected = [228, 308, 262] # the procedurally generated colons.
df = pd.DataFrame({'AMOS': num_organs_amos,
                   'Abdomen-1k': num_organs_abd,
                   'TotalSegmentator': num_organs_tot },
                  index=[item.replace("portal vein and splenic vein", "PVSV") for item in [item.replace("_", " ") for item in list_cols]],
                  )
df["AMOS"]["colon"] = organs_corrected[0]
df["Abdomen-1k"]["colon"] = organs_corrected[1]
df["TotalSegmentator"]["colon"] = organs_corrected[2]

df['Total'] = df['AMOS'] + df['Abdomen-1k'] + df['TotalSegmentator']
df = df.sort_values(by='Total', ascending=False)
df = df.drop('Total', axis=1)


plt.rcParams["figure.figsize"] = (8,4)
fig, ax = plt.subplots(layout="constrained")
ax.tick_params(axis='x', labelsize=8)
ax.tick_params(axis='y', labelsize=12)
ax.set_ylabel('Number of meshes', fontsize=12)
ax.set_xlabel('Anatomical Structure', fontsize=12)
# create stacked bar chart for monthly temperatures
df.plot(kind='bar', stacked=True, color=["#c2e8d4", "#67c694", "#0ba353"], ax=ax)
plt.show()
plt.savefig("./organ_volume_2.png", bbox_inches='tight')

# RL plot
plt.rcParams["figure.figsize"] = (5,5)
plt.rcParams.update({'font.size': 14})
fig, ax = plt.subplots(layout="constrained")
df = pd.DataFrame({'Human': [58.1, 74.3, 82.0, 89.7],
                   'RL Agent': [64.2, 83.1, 60.8, 86.3] },
                  index=["Case {}".format(i) for i in range(1, 5)],
                  )

df.plot(kind='bar',  color=["#67c694", "#0ba353"], ax=ax)
plt.ylabel("Avg. Number of Steps to Find Target")
plt.savefig("./RL_plot.png", dpi=300)
plt.show()