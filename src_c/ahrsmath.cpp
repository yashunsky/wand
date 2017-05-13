#include "ahrsmath.h"

#include <stdint.h>
#include <string.h>

static inline float inverseSquareRoot(float x)
{
  const int32_t magic = 0x5f375a86;
  float halfOfX = 0.5f * x;
  int32_t temp;

  memcpy(&temp, &x, sizeof(temp));
  temp = magic - (temp >> 1);
  memcpy(&x, &temp, sizeof(x));

  x *= (1.5f - halfOfX * x * x);

  return x;
}

void Vector::normalize()
{
  float norm = inverseSquareRoot(x * x + y * y + z * z);

  *this *= norm;
}

float Vector::norm()
{
  return 1 / inverseSquareRoot(x * x + y * y + z * z);
}

Vector Matrix::c0()
{
  return Vector(r0.x, r1.x, r2.x);
}

Vector Matrix::c1()
{
  return Vector(r0.y, r1.y, r2.y);
}

Vector Matrix::c2()
{
  return Vector(r0.z, r1.z, r2.z);
}

void Quaternion::normalize()
{
  float norm = inverseSquareRoot(a * a + b * b + c * c + d * d);

  *this *= norm;
}

Matrix Quaternion::toMatrix()
{
  return Matrix(
     Vector(1 - 2 * c * c - 2 * d * d,
      2 * b * c - 2 * d * a,
      2 * b * d + 2 * c * a),

     Vector(2 * b * c + 2 * d * a,
      1 - 2 * b * b - 2 * d * d,
      2 * c * d - 2 * b * a),

     Vector(2 * b * d - 2 * c * a,
      2 * c * d + 2 * b * a,
      1 - 2 * b * b - 2 * c * c));
}

Vector operator* (Vector v, Matrix m) {
  int DIMENTION = 3;

  float vr[DIMENTION];
  for (int i=0; i<DIMENTION; i++) {
      vr[i] = 0;
      for (int j=0; j<DIMENTION; j++) {
          vr[i] += m[i][j] * v[j];   
      }
  }  
  return Vector(vr[0], vr[1], vr[2]);
}
