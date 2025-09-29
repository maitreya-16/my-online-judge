#include <iostream>
using namespace std;

long long solve_logic(int n) {
    if (n == 0) return 0;
    if (n == 1 || n == 2) return 1;

    long long t0 = 0, t1 = 1, t2 = 1, t3;
    for (int i = 3; i <= n; i++) {
        t3 = t0 + t1 + t2;
        t0 = t1;
        t1 = t2;
        t2 = t3;
    }
    return t2;
}

int main() {
    int n;
    cin >> n;
    cout << solve_logic(n);
    return 0;
}
