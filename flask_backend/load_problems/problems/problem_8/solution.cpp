#include <iostream>
#include <vector>
#include <queue>
using namespace std;

int count_components(int n, const vector<pair<int, int>>& edges) {
    vector<vector<int>> graph(n + 1);

    // build adjacency list
    for (auto [u, v] : edges) {
        graph[u].push_back(v);
        graph[v].push_back(u);
    }

    vector<bool> visited(n + 1, false);
    int comp = 0;

    for (int i = 1; i <= n; i++) {
        if (!visited[i]) {
            comp++;
            queue<int> q;
            q.push(i);
            visited[i] = true;

            while (!q.empty()) {
                int node = q.front();
                q.pop();

                for (int nei : graph[node]) {
                    if (!visited[nei]) {
                        visited[nei] = true;
                        q.push(nei);
                    }
                }
            }
        }
    }
    return comp;
}

int main() {
    int n, m;
    cin >> n >> m;  // n = nodes, m = edges
    vector<pair<int, int>> edges(m);

    for (int i = 0; i < m; i++) {
        int u, v;
        cin >> u >> v;
        edges[i] = {u, v};
    }

    cout << n - count_components(n, edges);
    return 0;
}
