#include <iostream>
#include <cmath>
using namespace std;

string solve_logic(long long n) {
    long long root = sqrt(n);  // floor square root
    if (root * root == n && n % 2 == 1) {
        return "YES";
    }
    return "NO";
}

int main() {
    long long n;
    cin >> n;
    cout << solve_logic(n);
    return 0;
}
