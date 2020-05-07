# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 13:57:44 2020

@author: molok
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
# import matplotlib.gridspec as gs
pd.set_option('display.max_columns', 500)

flash_GOR = 5006
liquid_density = 0.7976
gas_density = 1.031
c36_mw = 531

const_R = 8.3144
ambient_T_F = 60
ambient_P_Psi = 14.7
vol_m3 = 0.0283

convert_F_to_K = lambda x: (x - 32) * 5 / 9+273
convert_C_to_R = lambda x: (x + 273.15) * 9 / 5
convert_Psi_to_Pa = lambda x: (x * 6894.757)
convert_bar_to_Psi = lambda x: (x * 14.5038)

ambient_T_K = convert_F_to_K(ambient_T_F)
ambient_P_Pa = convert_Psi_to_Pa(ambient_P_Psi)

# Reading pure component molar weights
pc_db = pd.read_excel(r'.\DATA\Components.xlsx', sheet_name = 'Sheet1',
                   nrows = 53, usecols = 'A:G, I', header = 0, 
                   na_values = [''])

# Extracting flash data from Core Lab spreadsheet
df = pd.read_excel(r'C:\Users\molok\Documents\Work\Dorado\play.xlsm', sheet_name = 'C.1',
                   skiprows = 11, nrows = 52, usecols = 'B:I', header = None, 
                   names = ['Short Name', 'CoreLab Name', 'Flash Lqd MP', 'Flash Lqd WP', 
                            'Flash Gas MP', 'Flash Gas WP', 'Res Fluid MP', 'Res Fluid WP'],
                   na_values = ' ')

df['Short Name'] = df['Short Name'].ffill()

# Adding component molar weight to Core Lab compositions
df = df.merge(pc_db.iloc[:, [0, 2, 3, 5, 6, 7]], on = 'CoreLab Name', how='outer')

# print(df.columns)
# df.to_csv(r'.\test.csv')

# Deciding which components are hydrocarbon components assuming they
# are based on template C##H##
df['HC'] = df['Formula Name  10 char'].str.contains('C\d{0,2}H\d+')

# Calculating the number of moles of liquid per stb
df.iat[-1, 9] = c36_mw
mole_lq = df['Flash Lqd MP'].dot(df['Mol wt']) / 100
mole_stb_No = liquid_density * 1000 / mole_lq * 159

# # Calculating the number of moles of gas per scf
mole_scf_Ng = ambient_P_Pa * vol_m3 / (const_R * ambient_T_K)

mFg = flash_GOR * mole_scf_Ng / (flash_GOR * mole_scf_Ng + mole_stb_No)

print("Ng: ", mole_scf_Ng)

print('No: ', mole_stb_No)

print("MFg: ", mFg)

df['Res Fluid MP Calc'] = df['Flash Gas MP'] * mFg + ( 1 - mFg) * df['Flash Lqd MP']

df['yi/zi'] = df['Flash Gas MP']/df['Res Fluid MP']
df['xi/zi'] = df['Flash Lqd MP']/df['Res Fluid MP']
df['xi/yi'] = df['Flash Gas MP']/df['Flash Lqd MP']
# df['F'] = (np.log10(convert_bar_to_Psi(
#     df['Crit P bara'])/14.7)*((1 / convert_C_to_R(df['Normal Tb DegC'])) - 
#                               (convert_C_to_R(df['Crit T DegC']))) / 
#                               ((1 / convert_C_to_R(df['Normal Tb DegC'])) - 
#                                 (convert_C_to_R(15.6))))

df['F'] = ((np.log10(convert_bar_to_Psi(df['Crit P bara'])
                     /ambient_P_Psi)/((1/(convert_C_to_R(df['Normal Tb DegC'])))-
                                      (1/(convert_C_to_R(df['Crit T DegC'])))))*
                                      ((1/(convert_C_to_R(df['Normal Tb DegC'])))-
                                       (1/(convert_C_to_R(15.6)))))
# # df['F'] = np.log10(df['F'])

# print(df['F'])

plt.style.use('ggplot')

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = 'Ubuntu'
plt.rcParams['font.monospace'] = 'Ubuntu Mono'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 12

fig = plt.figure(figsize=(8.27, 11.69), dpi=400)
fig.suptitle("Cylinder No.: MPSR 3750; Depth: 3866.69 mMD")
# fig.tight_layout()
fig.subplots_adjust(hspace=0.25)

# plt.subplots_adjust(hspace=0.25)#, wspace=0.40, top=0.95, 

gs_top = plt.GridSpec(5, 2, hspace=0, height_ratios = [1,1,1,2,2])
gs_bot = plt.GridSpec(5, 2, height_ratios = [1,1,1,2,2])

ax3 = plt.subplot(gs_top[2, :])
ax3.bar(df.loc[df['HC'] == True, 'Short Name'], df.loc[df['HC'] == True, 'Res Fluid MP'], color='C5')
ax3.plot(df.loc[df['HC'] == True, 'Short Name'], df.loc[df['HC'] == True, 'Res Fluid MP Calc'])
ax3.set_yscale('log')

ax1 = plt.subplot(gs_top[1, :], sharex = ax3, sharey = ax3)
ax1.bar(df.loc[df['HC'] == True, 'Short Name'], df.loc[df['HC'] == True, 'Flash Lqd MP'], color='C5')
plt.setp(ax1.get_xticklabels(), visible=False)
ax1.set_yscale('log')

ax2 = plt.subplot(gs_top[0, :], sharex = ax3, sharey = ax3)
ax2.bar(df.loc[df['HC'] == True, 'Short Name'], df.loc[df['HC'] == True, 'Flash Gas MP'], color='C0')
plt.setp(ax2.get_xticklabels(), visible=False)
ax2.set_yscale('log')

ax4 = plt.subplot(gs_bot[3, 0])
ax4.plot(df.loc[df['HC'] == True, 'xi/zi'], df.loc[df['HC'] == True, 'yi/zi'], 'bo')
plt.xlabel('xi/zi')
plt.ylabel('yi/zi')
ax4.set_title("Material Balance Plot", fontstyle='italic')

ax5 = plt.subplot(gs_bot[3, 1])
ax5.plot(((convert_C_to_R(df.loc[df['HC'] == True, 'Crit T DegC']))**2)/(10**5), df.loc[df['HC'] == True, 'xi/yi'], 'go')
ax5.set_yscale('log')
plt.xlabel('Tc * 10^5')
plt.ylabel('xi/yi')
ax5.set_title("Buckley Plot", fontstyle='italic')

ax6 = plt.subplot(gs_bot[4, 0])
ax6.plot(df.loc[df['HC'] == True, 'F'], df.loc[df['HC'] == True, 'xi/yi'], 'o')
ax6.set_yscale('log')
plt.xlabel('Fi')
plt.ylabel('xi/yi')
ax6.set_title("Hoffman Plot", fontstyle='italic')

fig.tight_layout()

plt.show()