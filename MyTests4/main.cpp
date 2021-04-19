#include<bits/stdc++.h>
#include"testlib/testlib.hpp"
using namespace std;

signed main(){
    Process proc("run_protocol.json");
    proc.prepare();
    proc.execute();
    //proc.close();
}