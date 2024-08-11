#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "sha256.cuh"

__global__ void compute_sha256(const BYTE *input, size_t length, BYTE *output)
{
    SHA256_CTX ctx;
    sha256_init(&ctx);
    sha256_update(&ctx, input, length);
    sha256_final(&ctx, output);

    // Debug print inside the kernel
}

extern "C" void hash_string(const char *str, char *hash_output)
{
    BYTE *dev_input, *dev_output;
    size_t length = strlen(str);
    BYTE host_output[SHA256_BLOCK_SIZE];

    checkCudaErrors(cudaMalloc((void **)&dev_input, length * sizeof(BYTE)));
    checkCudaErrors(cudaMalloc((void **)&dev_output, SHA256_BLOCK_SIZE * sizeof(BYTE)));

    checkCudaErrors(cudaMemcpy(dev_input, str, length * sizeof(BYTE), cudaMemcpyHostToDevice));

    // Initialize the constant memory
    checkCudaErrors(cudaMemcpyToSymbol(dev_k, host_k, sizeof(host_k)));

    compute_sha256<<<256, 256>>>(dev_input, length, dev_output);

    checkCudaErrors(cudaMemcpy(host_output, dev_output, SHA256_BLOCK_SIZE * sizeof(BYTE), cudaMemcpyDeviceToHost));

    cudaFree(dev_input);
    cudaFree(dev_output);

    char *result = hash_to_string(host_output);
    strcpy(hash_output, result);
    free(result);
}