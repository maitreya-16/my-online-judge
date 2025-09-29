#include <iostream>
#include <string>
using namespace std;

long long solve_logic(const string &s) {
    long long prod = 1, summ = 0;
    for (char ch : s) {
        int val = (ch - 'a' + 1);  // map 'a'->1, 'b'->2, ...
        prod *= val;
        summ += val;
    }
    return prod - summ;
}

int main() {
    string s;
    cin >> s;
    cout << solve_logic(s);
    return 0;
}
