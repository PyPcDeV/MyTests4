#include<bits/stdc++.h>
#include<stdio.h>
#include<unistd.h>
using namespace std;

#define READ 0
#define WRITE 1

pid_t popen2(string cmd,int*input,int*output){
    signed pstdin[2],pstdout[2];
    pid_t pid;
    if(pipe(pstdin)!=0||pipe(pstdout)!=0)return -1;
    pid=fork();
    if(pid<0)return pid;
    else if(pid==0){
        close(pstdin[WRITE]);
        dup2(pstdin[READ],READ);
        close(pstdout[READ]);
        dup2(pstdout[WRITE],WRITE);
        execl("/bin/sh", "sh", "-c", cmd.c_str(), NULL);
        perror("execl");
        exit(1);
    }
    if(input==NULL)close(pstdin[WRITE]);
    else *input=pstdin[WRITE];
    if(output==NULL)close(pstdout[READ]);
    else *output=pstdout[READ];
    return pid;
}