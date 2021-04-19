#include<bits/stdc++.h>
#include<sstream>
typedef long long ll;
#define int ll
using namespace std;

#ifndef PREPARE_TESTLIB_HPP
#define PREPARE_TESTLIB_HPP
void mkdir(int time,string name){
    string cmd;ostringstream ss;
    ss<<"mkdir "<<name<<time;
    cmd=ss.str();
    system(cmd.c_str());
}
void rmdir(int time,string name){
    string cmd;ostringstream ss;
    ss<<"rm -rf "<<name<<time;
    cmd=ss.str();
    system(cmd.c_str());
}
void compile(int time,string file_path,string name){
    string cmd;ostringstream ss;
    ss<<"g++ "<<file_path<<" -o "<<name<<time<<"/run";
    cmd=ss.str();
    system(cmd.c_str());
}
#endif