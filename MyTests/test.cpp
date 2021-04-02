#include<bits/stdc++.h>
using namespace std;
typedef long long ll;
#define int ll

signed main(){
    ios_base::sync_with_stdio(false);cin.tie(0);cout.tie(0);
    int n;
    cin>>n;
    int sum=0;
    for(int i=0;i<n;i++){
        int a;
        cin>>a;
        sum+=a;
    }
    cout<<sum<<"\n";
}