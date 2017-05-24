#ifndef TagunilAHRS_h
#define TagunilAHRS_h

class Vector
{
  public:
    Vector(float value = 0.0f) :
      x(value),
      y(value),
      z(value)
    {
    }

    Vector(float myX, float myY, float myZ) :
      x(myX),
      y(myY),
      z(myZ)
    {
    }

    Vector(const Vector &arg) :
      x(arg.x),
      y(arg.y),
      z(arg.z)
    {
    }

    Vector &operator=(const Vector &arg)
    {
      x = arg.x;
      y = arg.y;
      z = arg.z;

      return *this;
    }

    Vector &operator+=(const Vector &arg)
    {
      x += arg.x;
      y += arg.y;
      z += arg.z;

      return *this;
    }

    Vector &operator-=(const Vector &arg)
    {
      x -= arg.x;
      y -= arg.y;
      z -= arg.z;

      return *this;
    }

    friend Vector operator+(Vector arg1, Vector arg2)
    {
      return arg1 += arg2;
    }

    friend Vector operator-(Vector arg1, Vector arg2)
    {
      return arg1 -= arg2;
    }

    Vector &operator*=(float arg)
    {
      x *= arg;
      y *= arg;
      z *= arg;

      return *this;
    }

    float operator [](int i)
    {
      return i == 0 ? x : i == 1 ? y : z;
    }

    friend Vector operator*(Vector arg1, float arg2)
    {
      return arg1 *= arg2;
    }

    friend Vector operator*(float arg1, Vector arg2)
    {
      return arg2 *= arg1;
    }

    friend float dotProduct(Vector arg1, Vector arg2)
    {
      return arg1.x * arg2.x + arg1.y * arg2.y + arg1.z * arg2.z;
    }

    friend Vector crossProduct(Vector arg1, Vector arg2)
    {
      return Vector(arg1.y * arg2.z - arg1.z * arg2.y,
                    arg1.z * arg2.x - arg1.x * arg2.z,
                    arg1.x * arg2.y - arg1.y * arg2.x);
    }

    void normalize();

    float norm();

  public:
    float x;
    float y;
    float z;
};

class Matrix
{
  public:
    Matrix() : 
      r0(),
      r1(),
      r2()
    {
    }

    Matrix(Vector r0, Vector r1, Vector r2) : 
      r0(r0),
      r1(r1),
      r2(r2)
    {
    }

    Matrix T() {
      return Matrix(c0(), c1(), c2());
    }

    Vector operator [](int i)
    {
      return i == 0 ? r0 : i == 1 ? r1 : r2;
    }

    Vector c0();
    Vector c1();
    Vector c2();

    Vector r0;
    Vector r1;
    Vector r2;
};

class Quaternion
{
  public:
    Quaternion(float value = 0.0f) :
      a(value),
      b(value),
      c(value),
      d(value)
    {
    }

    Quaternion(float myA, float myB, float myC, float myD) :
      a(myA),
      b(myB),
      c(myC),
      d(myD)
    {
    }

    Quaternion(const Quaternion &arg) :
      a(arg.a),
      b(arg.b),
      c(arg.c),
      d(arg.d)
    {
    }

    Quaternion &operator=(const Quaternion &arg)
    {
      a = arg.a;
      b = arg.b;
      c = arg.c;
      d = arg.d;

      return *this;
    }

    Quaternion &operator+=(const Quaternion &arg)
    {
      a += arg.a;
      b += arg.b;
      c += arg.c;
      d += arg.d;

      return *this;
    }

    friend Quaternion operator+(Quaternion arg1, Quaternion arg2)
    {
      return arg1 += arg2;
    }

    Quaternion &operator*=(float arg)
    {
      a *= arg;
      b *= arg;
      c *= arg;
      d *= arg;

      return *this;
    }

    friend Quaternion operator*(Quaternion arg1, float arg2)
    {
      return arg1 *= arg2;
    }

    friend Quaternion operator*(float arg1, Quaternion arg2)
    {
      return arg2 *= arg1;
    }

    Quaternion &operator*=(Vector arg)
    {
      float scalar = -dotProduct(Vector(b, c, d), arg);
      Vector vector = a * arg + crossProduct(Vector(b, c, d), arg);

      a = scalar;
      b = vector.x;
      c = vector.y;
      d = vector.z;

      return *this;
    }

    friend Quaternion operator*(Quaternion arg1, Vector arg2)
    {
      return arg1 *= arg2;
    }

    void normalize();

    Matrix toMatrix();

  public:
    float a;
    float b;
    float c;
    float d;
};

Vector operator* (Vector v, Matrix m);

#endif
