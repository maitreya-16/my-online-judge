#include <iostream>
#include <cmath>
using namespace std;

string solve_logic(long long n) {
    // Binary search for integer square root
    long long left = 1, right = min(n, 1000000LL);  // sqrt(10^9) ≈ 31623
    long long root = 0;
    
    while (left <= right) {
        long long mid = left + (right - left) / 2;
        long long square = mid * mid;
        
        if (square == n) {
            root = mid;
            break;
        } else if (square < n) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    
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
