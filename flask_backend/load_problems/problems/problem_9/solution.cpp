#include <iostream>
using namespace std;

int solve_logic(int n) {
    return n * (n + 1) / 2;
}

int main() {
    int n;
    cin >> n;
    cout << solve_logic(n);
    return 0;
}
