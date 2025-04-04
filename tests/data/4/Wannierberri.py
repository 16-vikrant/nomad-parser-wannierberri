import os
os.environ['OPENBLAS_NUM_THREADS'] = '2' 
os.environ['MKL_NUM_THREADS'] = '2' 


import wannierberri as wberri
import numpy as np
import scipy
import matplotlib.pyplot as plt




parallel = wberri.Parallel(num_cpus=None, npar_k=0, ray_init={'_temp_dir':'/work/scratch/kh89jyni/wan-tep/'}, cluster=True, progress_step_percent=10)

#parallel = wberri.Serial()
system=wberri.System_w90(seedname='wannier90', berry=True, SHCqiao=True,guiding_centers = True)


###Read information in POSCAR for symmetry
def read_poscar(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Finding the line where fractional positions start
    for i, line in enumerate(lines):
        if line.strip().upper() == "DIRECT":
            start_line = i + 1
            break

    fractional_positions = []
    element_symbols = []

    # Reading fractional positions and element symbols
    for line in lines[start_line:]:
        parts = line.split()
        if len(parts) >= 4:
            fractional_positions.append([float(parts[0]), float(parts[1]), float(parts[2])])
            element_symbols.append(parts[3])

    return fractional_positions, element_symbols

poscar_file = 'POSCAR' 

fractional_positions, element_symbols = read_poscar(poscar_file)

Direct_Position = "[" + ", ".join([str(position) for position in fractional_positions]) + "]"
Element = '["' + '", "'.join(element_symbols) + '"]'

print("List of Fractional Positions:")
print(Direct_Position)
print("List of Element Symbols:")
print(Element)

system.set_structure(eval(Direct_Position), eval(Element))
system.set_symmetry_from_structure()

# Specify the path to your OUTCAR file in the upper directory
outcar_filename = 'OUTCAR'
outcar_path = os.path.join(os.pardir, outcar_filename)

# Function to extract E-fermi value from the OUTCAR file
def extract_efermi_from_outcar(outcar_path):
    efermi = None

    with open(outcar_path, 'r') as outcar_file:
        efermi_str = None  # Initialize efermi_str
        for line in outcar_file:
            if 'E-fermi' in line:
                # Split the line and extract the E-fermi value
                efermi = float(line.split()[2])
                break  # Exit the loop once E-fermi is found

    return efermi

# Call the function to get the E-fermi value
efermi = extract_efermi_from_outcar(outcar_path)


from wannierberri import calculators as calc

# Generate the efermi_list with the updated fermi_energy value
efermi_list = np.linspace(efermi - 1.0, efermi + 1.0, 201, True)





kwargs = dict(
    Efermi=efermi_list,
    omega=np.array([0.]),
    smr_fixed_width = 0.1, # Smearing for frequency in eV
    kBT = 0.026, # Smearing for Fermi level (Fermi-Dirac factor) in eV (not Kelvin)
)

calculators = dict(
    SHC_qiao = calc.dynamic.SHC(SHC_type="qiao", **kwargs)
)
grid = wberri.Grid(system, NKdiv = [20,20,1],
                  NKFFT = [20,20,1])
result = wberri.run(
    system,
    grid=grid,
    calculators=calculators,
    print_Kpoints = False,
    parallel=parallel,
    parameters_K = dict( fftlib = "numpy")
)
shc_qiao = result.results["SHC_qiao"].data[:, 0, 0, 1, 2]

# Read POSCAR
with open('POSCAR', 'r') as poscar_file:
    lines = poscar_file.readlines()
    sixth_line = lines[5].strip()  
    sixth_line = sixth_line.replace(" ", "_") 
    
# New filenames
new_filename = f'{sixth_line}_wb_shc.png'
compound_filename = f'{sixth_line}_shc.txt'

print(compound_filename)



# Write data to a file
with open(compound_filename, 'w') as f:
    f.write(f"{efermi_list[100]}\t{shc_qiao.real[100]/100}\n")

# Plotting
plt.figure(figsize=(8, 6))

# Plot on the single subplot
plt.plot(efermi_list, shc_qiao.real, label=r'$\sigma_{xy}^z$', color='blue', linewidth=2.5)
plt.axvline(x=efermi_list[100], color='k', linestyle="--", linewidth=1, label='Efermi')

# Set labels and title for the entire figure
plt.title(sixth_line)
plt.xlabel('Energy (eV)')
plt.ylabel('SHC ($\hbar/e$)S/m')

# Add legend to the plot
plt.legend()

# Save the plot with the new filename
plt.savefig(new_filename)

# Display the plot
plt.show()


