#include<chrono>

#ifndef TIME_TESTLIB_HPP
#define TIME_TESTLIB_HPP
long long gettime() {
  using namespace std::chrono;
  return (long long)duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
}
#endif