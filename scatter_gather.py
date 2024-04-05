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


def initialise_matrix_a(rows, offsets):
    """
    Initializes the matrix A for parallel computation.

    :param rows: A list containing the number of rows for each process.
    :param offsets: A list containing the displacement for each process.
    :return: A matrix A initialized for parallel computation.
    """
    matrix_a = []
    for k in range(len(rows)):
        sub_matrix = []
        for j in range(rows[k]):
            sub_matrix.append([])
            for i in range(NCA):
                sub_matrix[j].append(i + j + offsets[k])
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

    rows = np.zeros(nproc, dtype=np.int64)
    offsets = np.zeros(nproc, dtype=np.int64)

    rows_number = NRA // nproc
    extra_rows = NRA % nproc
    offset = 0
    for proc in range(nproc):
        if proc < extra_rows:
            rows[proc] = rows_number + 1
        else:
            rows[proc] = rows_number
        offsets[proc] = offset
        offset += rows[proc]

    matrix_a = None
    matrix_b = None

    if rank == MASTER:
        print(f"{rank}: Initializing matrices A and B.")
        matrix_a = initialise_matrix_a(rows, offsets)
        matrix_b = np.array([i*j for j in range(NCA) for i in range(NCB)]).reshape(NCA, NCB)

    local_a = comm.scatter(matrix_a, root=MASTER)
    matrix_b = comm.bcast(matrix_b, root=MASTER)

    local_c = np.zeros((rows[rank], NCB), dtype=int)
    print(f"{rank}: Performing matrix multiplication...")
    for i in range(rows[rank]):
        for j in range(NCB):
            for k in range(NCA):
                local_c[i][j] += local_a[i][k] * matrix_b[k][j]

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
