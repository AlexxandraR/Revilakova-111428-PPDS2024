"""
This module solves the fourth task. The solution was
inspired by the code - cv.mat_parsg.py from seminar 7
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


def initialise_matrix_a(extra_rows, total_rows, nproc, rows_per_proc):
    """
    Initializes matrix A for a parallel computation.

    :param extra_rows: The number of extra rows.
    :param total_rows: Total number of rows.
    :param nproc: Total number of processes.
    :param rows_per_proc: Number of rows per process.
    :return: A matrix A initialized for parallel computation.
    """
    matrix_a = []
    for k in range(extra_rows):
        sub_matrix = []
        for j in range(total_rows):
            sub_matrix.append([])
            for i in range(NCA):
                sub_matrix[j].append(i + k * total_rows + j)
        matrix_a.append(sub_matrix)
    for k in range(nproc - extra_rows):
        sub_matrix = []
        for j in range(rows_per_proc):
            sub_matrix.append([])
            for i in range(NCA):
                sub_matrix[j].append(i + k * rows_per_proc + j + extra_rows * total_rows)
        matrix_a.append(sub_matrix)
    return matrix_a


def main():
    """
       Main function for parallel matrix multiplication using scatter
       and gather functions.

       This function initializes MPI, distributes work among processes,
       performs matrix multiplication, gathers results, and prints the
       final matrix C along with the time taken for computation.
    """
    start_time = MPI.Wtime()

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    nproc = comm.Get_size()

    print(f"{rank}: Starting parallel matrix multiplication example...")
    print(f"{rank}: Using matrix sizes A[{NRA}][{NCA}], B[{NCA}][{NCB}], C[{NRA}][{NCB}]")

    rows_per_proc = NRA // nproc
    extra_rows = NRA % nproc
    total_rows = rows_per_proc + (1 if rank < extra_rows else 0)

    # Initialization of matrices A and B
    matrix_a = None
    matrix_b = None
    if rank == MASTER:
        print(f"{rank}: Initializing matrices A and B.")
        matrix_a = initialise_matrix_a(extra_rows, total_rows, nproc, rows_per_proc)
        matrix_b = np.array([i*j for j in range(NCA) for i in range(NCB)]).reshape(NCA, NCB)

    local_a = comm.scatter(matrix_a, root=MASTER)
    matrix_b = comm.bcast(matrix_b, root=MASTER)

    if rank < extra_rows:
        rows = NRA // nproc + 1
    else:
        rows = NRA // nproc

    # Perform sequential matrix multiplication
    local_c = np.zeros((rows, NCB), dtype=int)
    print(f"{rank}: Performing matrix multiplication...")
    for i in range(rows):
        for j in range(NCB):
            for k in range(NCA):
                local_c[i][j] += local_a[i][k] * matrix_b[k][j]

    # Combine results into matrix C
    matrix_c = comm.gather(local_c, root=MASTER)
    if rank == MASTER:
        matrix_c = np.array([ss for s in matrix_c for ss in s])
        print(f"{rank}: Here is the result matrix:")
        print(matrix_c)

        end_time = MPI.Wtime()
        duration = end_time - start_time
        print("Time: {:.6f}".format(duration))

    print(f"{rank}: Done.")


if __name__ == '__main__':
    main()
