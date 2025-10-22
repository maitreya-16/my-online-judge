#include <iostream>
using namespace std;

long long solve_logic(int n) {
    return (long long)n * (n + 1) / 2;
}

int main() {
    int n;
    cin >> n;
    cout << solve_logic(n);
    return 0;
}
