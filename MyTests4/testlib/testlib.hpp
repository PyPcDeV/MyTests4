#include<bits/stdc++.h>
#include<stdio.h>
#include<unistd.h>
#include<fcntl.h> 
#include<sys/wait.h>
#include"json.hpp"
#include"time.hpp"
#include"load_protocol.hpp"
#include"prepare.hpp"
#include"popen2.hpp"
typedef long long ll;
#define int ll
using json=nlohmann::json;
using namespace std;
#ifndef TESTLIB_TESTLIB_HPP
#define TESTLIB_TESTLIB_HPP


class Process{
    public:
    const string run="run";
    int time;
    int pid;
    json pr;
    Process(string protocol_path){
        pr=load_protocol(protocol_path);
    }
    void prepare(){
        time=gettime();
        mkdir(time,run);
        compile(time,pr.value("run_file",""),run);
        while(gettime()-time<=5000){}
    }
    void close(){
        rmdir(time,run);
    }
    void checker(pid_t p,signed&status_code,bool&procend){
        waitpid(p,&status_code,0);
        if(WIFEXITED(status_code))status_code=WEXITSTATUS(status_code);
        procend=1;
        cout<<"checker ended work, status code "<<status_code<<"\n";
    }
    void limiter(int start_time,int time_limit,int&elapsed,int&lterm,int&term){
        while(true){
            if(term==0)break;
            if(gettime()-start_time>=time_limit)break;
        }
        cout<<"limiter ended work\n";
        lterm--;
    }
    void writer(string input_file,int wp,int&lterm,int&term,bool&procend){
        ifstream f(input_file);
        string buf;
        while(true){
            if(lterm==0)break;
            if(procend)break;
            if(!(f>>buf))break;
            buf+="\n";
            write(wp, buf.c_str(),buf.length());
        }
        cout<<"writer ended work\n";
        term--;
        f.close();
    }
    void reader(string output_file,int rp,int&lterm,int&term,bool&procend){
        ofstream f(output_file);
        char buf[1024];
        while(true){
            if(lterm==0)break;
            if(procend)break;
            int rd=read(rp,buf,1024);
            if(rd!=-1)f<<buf;
        }
        cout<<"reader ended work\n";
        term--;
        f.close();
    }
    void execute(){
        string cmd;ostringstream ss;
        ss<<"./"<<run<<time<<"/"<<run;
        cmd=ss.str();
        for(auto test:pr["tests"]){
            int id=test.value("id",0);
            int time_limit=test.value("time_limit",0);
            int memory_limit=test.value("memory_limit",0);
            bool continue_if_fail=test.value("continue_if_fail",0);
            string input_file=test.value("input_file","");
            string output_file=test.value("output_file","");

            bool ok=1;
            bool fail=0;
            bool TLE=0;
            bool MLE=0;
            bool EE=0;

            int lterm=1;
            int term=2;

            int input,output;
            int start_time=gettime();
            int elapsed=0;

            signed status_code;
            bool procend=0;

            int pid=popen2(cmd,&input,&output);
            fcntl(output, F_SETFL, O_NONBLOCK);
            thread _checker(&Process::checker,this,pid,ref(status_code),ref(procend));
            ostringstream ss;
            ss<<run<<time<<"/"<<output_file;
            output_file=ss.str();
            if(pid<0){
                EE=1;
            }else{
                thread _limiter(&Process::limiter,this,start_time,time_limit,ref(elapsed),ref(lterm),ref(term));
                thread _writer(&Process::writer,this,input_file,input,ref(lterm),ref(term),ref(procend));
                thread _reader(&Process::reader,this,output_file,output,ref(lterm),ref(term),ref(procend));
                while(term!=0||lterm!=0){}
                _reader.join();
                _writer.join();
                _limiter.join();
            }
            elapsed=gettime()-start_time;
            kill(pid,SIGKILL);
            _checker.join();
            cout<<elapsed<<"ms elapsed\n";
        }
    }
};
#endif
