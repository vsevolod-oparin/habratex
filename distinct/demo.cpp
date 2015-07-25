#include <iostream>
#include <set>
#include <vector>
#include <algorithm>
#include <cmath>
#include <memory>

using namespace std;

class Counter {
    virtual void process(int a) = 0;
    virtual int  ans() = 0;
};

class SetCounter : Counter {
    set< int > s;
    void process(int a) { s.insert(a); } 
    int ans() { return static_cast< int >(s.size()); }
};

class SortCounter : Counter {
    vector< int > seq;
    void process(int a) { seq.push_back(a); } 
    int ans() { 
        sort(seq.begin(), seq.end());
        return unique(seq.begin(), seq.end()) - seq.begin();
    }  
};

struct Hash {
        
    struct Field {
        const static int primitive = 
            (1 << 15) + (1 << 9) + (1 << 7) + (1 << 4) + (1 << 3) + 1;

        int val;
        Field(int val) : val(val) {}
        Field(Field rhs) : val(rhs.val) {}
        operator int(){ return val; }
        Field operator+(Field rhs) { return val ^ rhs.val; }
        Field operator*(Field rhs) {
            int res = 0;
            int mul = val;
            for (int i = 0; i < 32; ++i) {
                if ((rhs.val >> i) % 2 == 1) {
                    res ^= mul;
                }
                mul = (mul << 1) ^ (mul < 0 ? primitive : 0);
            }
            return res;
        }
    };

    Field a, b;
    Hash(int a, int b) : a(a), b(b) {}
    Hash(Hash rhs) : a(rhs.a), b(rhs.b) {}
    int operator()(int x) { return a * Field(x) + b; }
};

class FMSimple : Counter {

    static int zero(int rhs) {
        int res = 0;
        for (int i = 31; i >= 0 && (rhs >> i) % 2 == 0; --i) {
            ++res;
        }
        return res;
    }

    int z;
    Hash h;

    FMSimple() : z(0), h(rand(), rand()) {}
    FMSimple(FMSimple rhs) : z(rhs.z), h(rhs.h) {}
    void process(int a) { z = max(z, zero(h(a))); } 
    int ans() { return pow(2.0, z + 0.5); }
};

class FM : Counter {

    vecror< FM > cnts;

    FM(int k) {
        cnts.resize(k);
    }

    void process(int a) {
        for (size_t i = 0; i < cnt.size(); ++i) {
            cnt[i].process(a);
        }
    }

    int ans() {
        vector< int > answers(cnt.size());
        for (size_t i = 0; i < cnt.size(); ++i) {
            answers[i] = cnt[i].ans();
        }
        sort(answers.begin(), answers.end());
        return answers[cnt.size() / 2];
    }
};

int main() {

    const int stream_size = 1e8;
    const int range_size = 1e5;

    auto_ptr< Counter > counter(new SetCounter());




    return 0;
}

