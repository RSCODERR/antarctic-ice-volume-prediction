import sys, os, platform, multiprocessing, shutil

print("=== OPERATING SYSTEM & HARDWARE ===")
print("Platform:", platform.platform())
print("OS:", platform.system(), platform.release(), platform.version())
print("Architecture:", platform.machine(), platform.processor())
print("CPU Core Count (Logical):", multiprocessing.cpu_count())

# Try psutil for RAM if available
try:
    import psutil
    ram_gb = psutil.virtual_memory().total / (1024**3)
    ram_avail_gb = psutil.virtual_memory().available / (1024**3)
    print(f"Total RAM: {ram_gb:.2f} GB")
    print(f"Available RAM: {ram_avail_gb:.2f} GB")
except ImportError:
    print("psutil not installed; querying systeminfo via PowerShell if needed.")

print("\n=== PYTHON ENVIRONMENT ===")
print("Python Executable:", sys.executable)
print("Python Version:", sys.version)

print("\n=== SPARSE LINEAR ALGEBRA & AMG PACKAGES ===")
for pkg in ['numpy', 'scipy', 'pyamg', 'numba', 'mpi4py', 'petsc4py', 'petsc']:
    try:
        mod = __import__(pkg)
        ver = getattr(mod, '__version__', 'Installed (no __version__)')
        print(f"  {pkg}: {ver}")
    except ImportError:
        print(f"  {pkg}: NOT INSTALLED")

print("\n=== MPI SYSTEM BINARIES ===")
for cmd in ['mpiexec', 'mpirun', 'cl', 'gcc', 'gfortran']:
    path = shutil.which(cmd)
    print(f"  {cmd}: {path if path else 'NOT FOUND in PATH'}")

