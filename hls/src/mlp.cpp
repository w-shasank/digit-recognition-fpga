#include "mlp.h"
#include "weights.h"

  data8_t relu(acc_t x) {
    if (x < 0)   return 0;
    if (x > 127) return 127;
    return (data8_t)x;
}

template<int IN_SIZE, int OUT_SIZE>
void dense_relu(
    data8_t         in[IN_SIZE],
    data8_t         out[OUT_SIZE],
    const ap_int<8> weights[OUT_SIZE][IN_SIZE]
){
    for (int i = 0; i < OUT_SIZE; i++) {
        #pragma HLS PIPELINE II=1
        acc_t acc = 0;
        for (int j = 0; j < IN_SIZE; j++) {
            acc += (acc_t)weights[i][j] * (acc_t)in[j];
        }
        out[i] = relu(acc);
    }
}

template<int IN_SIZE, int OUT_SIZE>
int dense_argmax(
    data8_t         in[IN_SIZE],
    const ap_int<8> weights[OUT_SIZE][IN_SIZE]
){
    acc_t scores[OUT_SIZE];
    #pragma HLS ARRAY_PARTITION variable=scores complete

    for (int i = 0; i < OUT_SIZE; i++) {
        #pragma HLS PIPELINE II=1
        acc_t acc = 0;
        for (int j = 0; j < IN_SIZE; j++) {
            acc += (acc_t)weights[i][j] * (acc_t)in[j];
        }
        scores[i] = acc;
    }

    int best = 0;
    for (int i = 1; i < OUT_SIZE; i++) {
        if (scores[i] > scores[best]) best = i;
    }
    return best;
}

void mlp_inference(data8_t input[784], int &result) {
    #pragma HLS INTERFACE ap_memory  port=input
    #pragma HLS INTERFACE ap_none    port=result
    #pragma HLS INTERFACE ap_ctrl_hs port=return

    data8_t layer1_out[256];
    data8_t layer2_out[128];
    #pragma HLS ARRAY_PARTITION variable=layer1_out cyclic factor=4
    #pragma HLS ARRAY_PARTITION variable=layer2_out cyclic factor=4

    dense_relu<L1_IN, L1_OUT>(input,      layer1_out, W1);
    dense_relu<L2_IN, L2_OUT>(layer1_out, layer2_out, W2);
    result = dense_argmax<L3_IN, L3_OUT>(layer2_out,  W3);
}
```

---

