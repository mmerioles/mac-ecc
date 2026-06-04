KERNEL_SRC = r"""

#include <stdint.h>

typedef unsigned long long u64;

// 256-bit integer: 4 x u64, limb[0] = least significant word
typedef struct { u64 limb[4]; } u256;

// ---------- 64-bit helpers, no __uint128_t ----------

__device__ inline u64 add3_u64(u64 a, u64 b, u64 c, u64 *carry) {
    u64 r1 = a + b;
    u64 c1 = (r1 < a);

    u64 r2 = r1 + c;
    u64 c2 = (r2 < r1);

    *carry = c1 + c2;
    return r2;
}

__device__ inline void mul64wide(u64 a, u64 b, u64 *lo, u64 *hi) {
    *lo = a * b;
    *hi = __umul64hi(a, b);
}

// Computes: Tj = low64(x*y + Tj + carry)
// Returns: high64(x*y + Tj + carry)
__device__ inline u64 mac_u64(u64 x, u64 y, u64 Tj, u64 carry, u64 *out_lo) {
    u64 lo, hi;
    mul64wide(x, y, &lo, &hi);

    u64 c;
    *out_lo = add3_u64(lo, Tj, carry, &c);

    return hi + c;
}

// P-256 prime, limb[0] first, little-endian
__device__ __constant__ u64 P256[4] = {
    0xFFFFFFFFFFFFFFFFULL,
    0x00000000FFFFFFFFULL,
    0x0000000000000000ULL,
    0xFFFFFFFF00000001ULL
};

__device__ u64 R2_LIMBS[4];

#define M0_INV 1ULL

__device__ u256 load_p() {
    u256 p;
    p.limb[0] = P256[0];
    p.limb[1] = P256[1];
    p.limb[2] = P256[2];
    p.limb[3] = P256[3];
    return p;
}

__device__ u256 load_r2() {
    u256 r2;
    r2.limb[0] = R2_LIMBS[0];
    r2.limb[1] = R2_LIMBS[1];
    r2.limb[2] = R2_LIMBS[2];
    r2.limb[3] = R2_LIMBS[3];
    return r2;
}

__device__ u256 make_one() {
    u256 one;
    one.limb[0] = 1ULL;
    one.limb[1] = 0ULL;
    one.limb[2] = 0ULL;
    one.limb[3] = 0ULL;
    return one;
}

__device__ int cmp256(u256 a, u256 b) {
    for (int i = 3; i >= 0; i--) {
        if (a.limb[i] < b.limb[i]) return -1;
        if (a.limb[i] > b.limb[i]) return 1;
    }
    return 0;
}

__device__ u64 add256(u256 a, u256 b, u256 *r) {
    u64 carry = 0;

    for (int i = 0; i < 4; i++) {
        u64 new_carry;
        r->limb[i] = add3_u64(a.limb[i], b.limb[i], carry, &new_carry);
        carry = new_carry;
    }

    return carry;
}

__device__ u64 sub256(u256 a, u256 b, u256 *r) {
    u64 borrow = 0;

    for (int i = 0; i < 4; i++) {
        u64 ai = a.limb[i];
        u64 bi = b.limb[i];

        u64 t = ai - borrow;
        u64 b1 = (ai < borrow);

        r->limb[i] = t - bi;
        u64 b2 = (t < bi);

        borrow = b1 + b2;
    }

    return borrow;
}

__device__ u256 d_mod_add(u256 a, u256 b) {
    u256 r;
    u256 p = load_p();

    u64 carry = add256(a, b, &r);

    if (carry || cmp256(r, p) >= 0) {
        u256 t;
        sub256(r, p, &t);
        return t;
    }

    return r;
}

__device__ u256 d_mod_sub(u256 a, u256 b) {
    u256 r;
    u256 p = load_p();

    u64 borrow = sub256(a, b, &r);

    if (borrow) {
        u256 t;
        add256(r, p, &t);
        return t;
    }

    return r;
}

// CIOS Montgomery multiplication.
// Returns a * b * R^{-1} mod P.
__device__ u256 mont_mul(u256 a, u256 b) {
    u64 T[5] = {0ULL, 0ULL, 0ULL, 0ULL, 0ULL};
    u64 T4_overflow = 0ULL;

    for (int i = 0; i < 4; i++) {
        // multiply: T += a[i] * b
        u64 carry = 0ULL;

        for (int j = 0; j < 4; j++) {
            u64 out;
            carry = mac_u64(a.limb[i], b.limb[j], T[j], carry, &out);
            T[j] = out;
        }

        u64 old_T4 = T[4];
        T[4] += carry;
        if (T[4] < old_T4) T4_overflow = 1ULL;

        // reduce: m = T[0] since M0_INV = 1
        u64 m = T[0];
        carry = 0ULL;

        for (int j = 0; j < 4; j++) {
            u64 out;
            carry = mac_u64(m, P256[j], T[j], carry, &out);
            T[j] = out;
        }

        old_T4 = T[4];
        T[4] += carry;
        if (T[4] < old_T4) T4_overflow = 1ULL;

        // shift right by 64 bits
        T[0] = T[1];
        T[1] = T[2];
        T[2] = T[3];
        T[3] = T[4];
        T[4] = T4_overflow;
        T4_overflow = 0ULL;
    }

    u256 r;
    r.limb[0] = T[0];
    r.limb[1] = T[1];
    r.limb[2] = T[2];
    r.limb[3] = T[3];

    u256 p = load_p();

    if (T[4] > 0ULL || cmp256(r, p) >= 0) {
        u256 t;
        sub256(r, p, &t);
        return t;
    }

    return r;
}

__device__ u256 d_mod_mul(u256 a, u256 b) {
    u256 R2 = load_r2();
    u256 one = make_one();

    u256 a_m = mont_mul(a, R2);
    u256 b_m = mont_mul(b, R2);
    u256 r_m = mont_mul(a_m, b_m);

    return mont_mul(r_m, one);
}

__device__ u256 d_mod_exp(u256 base, u256 exp) {
    u256 R2 = load_r2();
    u256 one = make_one();

    u256 base_m = mont_mul(base, R2);
    u256 result_m = mont_mul(one, R2);

    for (int i = 0; i < 256; i++) {
        int w = i / 64;
        int bit = i % 64;

        if ((exp.limb[w] >> bit) & 1ULL) {
            result_m = mont_mul(result_m, base_m);
        }

        base_m = mont_mul(base_m, base_m);
    }

    return mont_mul(result_m, one);
}

__global__ void kernel_mod_add(u256 *A, u256 *B, u256 *C, int n) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid < n) C[tid] = d_mod_add(A[tid], B[tid]);
}

__global__ void kernel_mod_sub(u256 *A, u256 *B, u256 *C, int n) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid < n) C[tid] = d_mod_sub(A[tid], B[tid]);
}

__global__ void kernel_mod_mul(u256 *A, u256 *B, u256 *C, int n) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid < n) C[tid] = d_mod_mul(A[tid], B[tid]);
}

__global__ void kernel_mod_exp(u256 *bases, u256 *exps, u256 *results, int n) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid < n) results[tid] = d_mod_exp(bases[tid], exps[tid]);
}

"""

print("Kernel source defined.")