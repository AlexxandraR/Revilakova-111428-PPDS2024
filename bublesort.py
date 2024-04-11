"""
This module solves the fifth task. The solution was
inspired by the codes from lecture 8
(available at: https://github.com/tj314/ppds-seminars/tree/ppds2024/lecture8)
and seminar 8
(available at: https://github.com/tj314/ppds-seminars/tree/ppds2024/seminar8).
Sequential bubblesort was inspired from the following website:
https://www.geeksforgeeks.org/python-program-for-bubble-sort/.
"""

__authors__ = "Alexandra Reviľáková"
__license__ = "MIT"

import math
import numpy as np
from numba import cuda
from timer import Timer


@cuda.jit
def partition_kernel(array, pivots, bucket_sizes, num_buckets):
    """
    Partitions an array into buckets based on given pivots.

    :param array: Input array to be partitioned.
    :param pivots: Pivots used for partitioning.
    :param bucket_sizes: Array to store the size of each bucket.
    :param num_buckets: Number of buckets to partition the array into.
    """
    tid = cuda.grid(1)
    stride = cuda.gridDim.x * cuda.blockDim.x

    for i in range(tid, array.shape[0], stride):
        value = array[i]
        bucket = 0
        while bucket < num_buckets and value >= pivots[bucket]:
            bucket += 1
        cuda.atomic.add(bucket_sizes, bucket, 1)
        array[i] = bucket


@cuda.jit
def bucket_kernel(array_name, array, num_buckets, bucket_array, bucket_offset):
    """
    Performs the inclusion of elements from the array into separate buckets.

    :param array_name: An array containing elements to be bucketed.
    :param array: An array containing bucket numbers for elements from the array - array_name.
    :param num_buckets: Number of buckets.
    :param bucket_array: Array to store bucketed elements.
    :param bucket_offset: Array containing offsets for each bucket.
    """
    tid = cuda.grid(1)
    if tid < num_buckets:
        counter = bucket_offset[tid]
        for i in range(array.size):
            if array[i] == tid:
                bucket_array[counter] = array_name[i]
                counter += 1


@cuda.jit
def sort_buckets_kernel(array, bucket_offsets):
    """
    Sorts elements within each bucket based on bubble sort algorithm.

    :param array: Input array containing elements within buckets to be sorted.
    :param bucket_offsets: Array containing offsets for each bucket.
    """
    tid = cuda.grid(1)

    start = end = 0
    if tid < bucket_offsets.size - 1:
        start = bucket_offsets[tid]
        end = bucket_offsets[tid+1]-1
    elif tid == bucket_offsets.size - 1:
        start = bucket_offsets[tid]
        end = array.size-1

    if start != end:
        for i in range(end - start):
            swapped = False
            for j in range(start, end + 1 - i - 1):
                if array[j] > array[j + 1]:
                    swapped = True
                    array[j], array[j + 1] = array[j + 1], array[j]
            if not swapped:
                return


def sample_sort(array):
    """
    Performs parallel sample sort algorithm on the input array.

    :param array: Input array to be sorted.
    :return: Sorted array.
    """
    array = np.array(array)
    num_elements = array.shape[0]

    if num_elements < 4:
        buble_sort(array)
        return array

    num_threads = 256
    num_blocks = int(math.ceil(num_elements / num_threads))

    num_pivots = int(np.sqrt(num_elements))
    num_pivots = min(num_pivots, num_elements)

    d_array = cuda.to_device(array)
    d_pivots = np.zeros(num_pivots, dtype=array.dtype)
    d_bucket_sizes = cuda.to_device(np.zeros(num_pivots + 1, dtype=np.int32))

    for i in range(num_pivots):
        d_pivots[i] = d_array[i * (num_elements - 1) // (num_pivots - 1)]

    d_pivots.sort()
    d_pivots = cuda.to_device(d_pivots)

    partition_kernel[num_blocks, num_threads](d_array, d_pivots, d_bucket_sizes, num_pivots)

    bucket_sizes = d_bucket_sizes.copy_to_host()
    d_bucket_offsets = np.zeros_like(bucket_sizes)
    for i in range(1, len(d_bucket_offsets)):
        d_bucket_offsets[i] = d_bucket_offsets[i - 1] + bucket_sizes[i - 1]

    d_bucket_offsets = cuda.to_device(d_bucket_offsets)

    d_bucket_array = np.zeros_like(array)
    d_bucket_array = cuda.to_device(d_bucket_array)

    array1 = cuda.to_device(array)

    num_blocks = int(math.ceil(bucket_sizes.shape[0] / num_threads))

    bucket_kernel[num_blocks, num_threads](array1, d_array, num_pivots+1, d_bucket_array, d_bucket_offsets)

    sort_buckets_kernel[num_blocks, num_threads](d_bucket_array, d_bucket_offsets)

    return d_bucket_array.copy_to_host()


def buble_sort(array):
    """
    Sequentially sorts the input array using bubble sort algorithm.

    :param array: Input array to be sorted.
    """
    n = len(array)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if array[j] > array[j + 1]:
                swapped = True
                array[j], array[j + 1] = array[j + 1], array[j]
        if not swapped:
            return


def main():
    """
    Executes the main function which generates a random array, sorts it using
    both parallel and sequential algorithms, and prints the results.
    The function also measures the execution time for both sorting algorithms.
    """
    min_val = -1000
    max_val = 1000
    size = 1000
    arr = np.random.randint(min_val, max_val, size)
    print("Original array:\n", arr)

    tim = Timer()
    sorted_array = sample_sort(arr)
    t1 = tim.lap_ms()
    print("Parallel sorted array (GPU):\n", sorted_array)

    tim.reset()
    buble_sort(arr)
    t2 = tim.lap_ms()
    print("Sequentially sorted array (Host):\n", arr)
    print(f"Host: {t2:.1f} ms, GPU: {t1:.1f} ms")


if __name__ == "__main__":
    main()
