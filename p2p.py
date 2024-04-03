"""
This file contains a modified version of cv.mat_par.py for any number of
processors.The solution was inspired by the code - cv.mat_par.py from seminar 7
(available at: https://elearn.elf.stuba.sk/moodle/mod/folder/view.php?id=27376).
"""

__authors__ = "Alexandra Reviľáková"
__license__ = "MIT"

import numpy as np
from mpi4py import MPI


NRA = 32  # number of rows in matrix A
NCA = 15  # number of columns in matrix A
NCB = 7   # number of columns in matrix B

MASTER = 0


def main():
    """
        Main function for parallel matrix multiplication using send
        and recv functions.

        This function initializes MPI, distributes work among processes,
        performs matrix multiplication, gathers results, and prints the
        final matrix C along with the time taken for computation.
    """
    start_time = MPI.Wtime()

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    nproc = comm.Get_size()

    extra_rows = NRA % nproc

    print(f"{rank}: Starting parallel matrix multiplication example...")
    print(f"{rank}: Using matrix sizes A[{NRA}][{NCA}], B[{NCA}][{NCB}], C[{NRA}][{NCB}]")

    rows = NRA // nproc
    if rank == MASTER:
        print(f"{rank}: Initializing matrices A and B.")
        matrix_a = np.array([k+j for j in range(NRA) for k in range(NCA)]).reshape(NRA, NCA)
        matrix_b = np.array([k*j for j in range(NCA) for k in range(NCB)]).reshape(NCA, NCB)

        previous_gap = 0
        gap = 0
        for proc in range(nproc):
            if extra_rows != 0 and proc < extra_rows:
                gap += 1
            if proc == MASTER:
                local_a = matrix_a[proc * rows:proc * rows + rows+gap]
            elif proc < extra_rows:
                comm.send(matrix_a[proc * rows + previous_gap:proc * rows + rows + gap], dest=proc)
            else:
                comm.send(matrix_a[proc*rows + previous_gap:proc*rows+rows+gap], dest=proc)
            if extra_rows != 0 and proc < extra_rows:
                previous_gap += 1
    else:
        local_a = comm.recv()
        matrix_b = None

    matrix_b = comm.bcast(matrix_b, root=MASTER)

    # Perform sequential matrix multiplication
    if extra_rows != 0 and rank < extra_rows:
        row = rows + 1
    else:
        row = rows
    local_c = np.zeros((row, NCB), dtype=int)
    print(f"{rank}: Performing matrix multiplication...")
    for i in range(row):
        for j in range(NCB):
            for k in range(NCA):
                local_c[i][j] += local_a[i][k] * matrix_b[k][j]

    # Combine results into matrix C
    matrix_c = np.zeros((NRA, NCB), dtype=int)
    if rank == MASTER:
        previous_gap = 0
        gap = 0
        for proc in range(nproc):
            if extra_rows != 0 and proc < extra_rows:
                gap += 1
            if proc == MASTER:
                matrix_c[proc*rows:proc*rows+rows+gap] = local_c
            elif proc < extra_rows:
                matrix_c[proc * rows + previous_gap:proc * rows + rows + gap] = comm.recv(source=proc)
            else:
                matrix_c[proc*rows + previous_gap:proc*rows+rows + previous_gap] = comm.recv(source=proc)
            if extra_rows != 0 and proc < extra_rows:
                previous_gap += 1
        print(f"{rank}: Here is the result matrix:")
        print(matrix_c)

        end_time = MPI.Wtime()
        duration = end_time - start_time
        print("Time: {:.6f}".format(duration))
    else:
        comm.send(local_c, dest=MASTER)

    print(f"{rank}: Done.")


if __name__ == '__main__':
    main()
