#include<bits/stdc++.h>
#include"json.hpp"
using json = nlohmann::json;
using namespace std;

#ifndef LOAD_PPROTOCOL_TESTLIB_HPP
#define LOAD_PROTOCOL_TESTLIB_HPP
json load_protocol(string path){
    ifstream f(path);
    string res,buf;
    while(f>>buf)res+=buf;
    return json::parse(res);
}
#endif