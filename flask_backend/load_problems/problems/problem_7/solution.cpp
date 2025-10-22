#include <iostream>
#include <vector>
using namespace std;

int gcd(int a, int b) {
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

int main() {
    int n;
    cin >> n;
    vector<int> arr(n);
    for (int i = 0; i < n; i++) cin >> arr[i];

    vector<int> prefix(n), suffix(n), ans(n);

    // Build prefix GCD
    prefix[0] = arr[0];
    for (int i = 1; i < n; i++) {
        prefix[i] = gcd(prefix[i - 1], arr[i]);
    }

    // Build suffix GCD
    suffix[n - 1] = arr[n - 1];
    for (int i = n - 2; i >= 0; i--) {
        suffix[i] = gcd(suffix[i + 1], arr[i]);
    }

    // Compute answer for each index
    for (int i = 0; i < n; i++) {
        if (i == 0) ans[i] = suffix[1];            // exclude arr[0]
        else if (i == n - 1) ans[i] = prefix[n-2]; // exclude arr[n-1]
        else ans[i] = gcd(prefix[i - 1], suffix[i + 1]);
    }

    // Print result
    for (int i = 0; i < n; i++) cout << ans[i] << " ";
    return 0;
}
