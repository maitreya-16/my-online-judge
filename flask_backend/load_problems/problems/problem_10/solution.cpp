#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
#include <algorithm>
using namespace std;

string solve_logic(const string &s) {
    unordered_map<char, int> freq;   // frequency count
    unordered_map<char, int> first;  // first occurrence index

    for (int i = 0; i < (int)s.size(); i++) {
        freq[s[i]]++;
        if (first.find(s[i]) == first.end()) {
            first[s[i]] = i; // store first appearance
        }
    }

    vector<pair<char, int>> items(freq.begin(), freq.end());

    // sort by frequency (desc), then by first occurrence (asc)
    sort(items.begin(), items.end(),
         [&](const pair<char, int> &a, const pair<char, int> &b) {
             if (a.second != b.second)
                 return a.second > b.second; // higher freq first
             return first[a.first] < first[b.first]; // earlier appearance first
         });

    string result;
    for (auto &p : items) {
        result.push_back(p.first);
    }
    return result;
}

int main() {
    string s;
    cin >> s;
    cout << solve_logic(s);
    return 0;
}
