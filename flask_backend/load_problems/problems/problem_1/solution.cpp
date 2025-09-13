#include <iostream>
using namespace std;

int main() {
    int n, m;
    cin >> n >> m; // number of rows and columns
    
    int arr[n][m];
    
    // input matrix
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < m; j++) {
            cin >> arr[i][j];
        }
    }
    
    // output matrix row by row
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < m; j++) {
            cout << arr[i][j] << " ";
        }
        cout << endl; // move to next line
    }
    
    return 0;
}
