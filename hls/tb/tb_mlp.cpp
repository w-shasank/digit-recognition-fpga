#include <iostream>
#include <cstdlib>
#include "mlp.h"
#include "test_image.h"

int main() {

    data8_t input[784];
    for (int i = 0; i < 784; i++) {
        input[i] = (data8_t)TEST_IMAGE[i];
    }

    int result = -1;
    mlp_inference(input, result);

    std::cout << "Expected : " << EXPECTED_LABEL  << std::endl;
    std::cout << "Predicted: " << result           << std::endl;

    if (result == EXPECTED_LABEL) {
        std::cout << "TEST PASSED " << std::endl;
        return 0;
    } else {
        std::cout << "TEST FAILED " << std::endl;
        return 1;
    }
}
