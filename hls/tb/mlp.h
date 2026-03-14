#ifndef MLP_H
#define MLP_H

#include <ap_int.h>
// 8-bit signed for inputs/weights
typedef ap_int<8>  data8_t; 
 // 32-bit accumulator for MAC result
typedef ap_int<32> acc_t;
// 8-bit output activations     
typedef ap_int<8>  out_t;      


void mlp_inference(data8_t input[784], int &result);

#endif
