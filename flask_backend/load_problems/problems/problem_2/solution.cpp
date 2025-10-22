#include <iostream>
#include <string>
#include <unordered_set>
using namespace std;

int solve_logic(const string &s) {
    unordered_set<char> distinct_chars;
    
    for (char c : s) {
        distinct_chars.insert(c);
    }
    
    return distinct_chars.size();
}

int main() {
    string s;
    cin >> s;
    cout << solve_logic(s);
    return 0;
}
