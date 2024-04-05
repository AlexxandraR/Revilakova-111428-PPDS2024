"""
This module solves the bonus from the fourth task. The solution was
inspired by the code - cv.mat_parsg.py from seminar 7
(available at: https://elearn.elf.stuba.sk/moodle/mod/folder/view.php?id=27376)
and the code from following website:
https://www.kth.se/blogs/pdc/2019/11/parallel-programming-in-python-mpi4py-part-2/.
"""

__authors__ = "Alexandra Reviľáková"
__license__ = "MIT"

from mpi4py import MPI
import numpy as np

NRA = 32  # number of rows in matrix A
NCA = 15  # number of columns in matrix A
NCB = 7   # number of columns in matrix B

MASTER = 0


def main():
    """
    Main function to perform parallel matrix multiplication using Scatterv
    and Gatherv functions.

    This function initializes MPI, determines the rank of the process,
    distributes matrix A to each process, performs matrix multiplication
    locally, gathers the result matrix C to the master process,
    and displays the result.
    """
    start_time = MPI.Wtime()

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    nproc = comm.Get_size()

    print(f"{rank}: Starting parallel matrix multiplication example...")
    print(f"{rank}: Using matrix sizes A[{NRA}][{NCA}], B[{NCA}][{NCB}], C[{NRA}][{NCB}]")

    a_row = MPI.INT64_T.Create_contiguous(NCA).Commit()
    b_row = MPI.INT64_T.Create_contiguous(NCB).Commit()

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
        print("Initializing matrices...")
        matrix_a = np.array([[i + j for j in range(NCA)] for i in range(NRA)], dtype=np.int64)
        matrix_b = np.array([[i * j for j in range(NCB)] for i in range(NCA)], dtype=np.int64)

    local_a = np.zeros((rows[rank], NCA), dtype=np.int64)
    comm.Scatterv([matrix_a, rows, offsets, a_row], local_a, root=MASTER)
    matrix_b = comm.bcast(matrix_b, root=MASTER)

    local_c = np.zeros((rows[rank], NCB), dtype=np.int64)
    print(f"{rank}: Performing matrix multiplication")
    for i in range(rows[rank]):
        for j in range(NCB):
            for k in range(NCA):
                local_c[i, j] += local_a[i, k] * matrix_b[k, j]

    matrix_c = np.empty((NRA, NCB), dtype=np.int64)
    comm.Gatherv(local_c, [matrix_c, rows, offsets, b_row], root=MASTER)

    if rank == MASTER:
        print(f"Here is the result matrix: \n {matrix_c}")

        end_time = MPI.Wtime()
        duration = end_time - start_time
        print("{:.6f}".format(duration))

    a_row.Free()
    b_row.Free()
    print(f"{rank}: Done.")


if __name__ == '__main__':
    main()
