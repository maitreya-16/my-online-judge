## Create Virtual Enviroment 
```bash
cd flask_backend
python -m venv my-venv
source my-venv/bin/activate
```

## Instal Dependencies
```bash
pip install -r requirements.txt
```

## Run Redis

```bash
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

## Start Flask

```bash
cd workers
python server.py
```

## Start Celery

```bash
cd workers
celery -A tasks worker --loglevel=info
```

## Load Problems

```bash
cd load_problems
python load_problems.py
```
## Example: Enqueue a Code Submission

Send a POST request to `localhost:5000/enqueue/run` or `localhost:5000/enqueue/submit` with the following JSON body:

Code and Input is encoded 

```json
{
  "submission_id": 1011,
  "code": "I2luY2x1ZGUgPGlvc3RyZWFtPgp1c2luZyBuYW1lc3BhY2Ugc3RkOwoKaW50IG1haW4oKSB7CiAgICBpbnQgbiwgbTsKICAgIGNpbiA+PiBuID4+IG07IC8vIG51bWJlciBvZiByb3dzIGFuZCBjb2x1bW5zCiAgICAKICAgIGludCBhcnJbbl1bbV07CiAgICAKICAgIC8vIGlucHV0IG1hdHJpeAogICAgZm9yKGludCBpID0gMDsgaSA8IG47IGkrKykgewogICAgICAgIGZvcihpbnQgaiA9IDA7IGogPCBtOyBqKyspIHsKICAgICAgICAgICAgY2luID4+IGFycltpXVtqXTsKICAgICAgICB9CiAgICB9CiAgICAKICAgIC8vIG91dHB1dCBtYXRyaXggcm93IGJ5IHJvdwogICAgZm9yKGludCBpID0gMDsgaSA8IG47IGkrKykgewogICAgICAgIGZvcihpbnQgaiA9IDA7IGogPCBtOyBqKyspIHsKICAgICAgICAgICAgY291dCA8PCBhcnJbaV1bal0gPDwgIiAiOwogICAgICAgIH0KICAgICAgICBjb3V0IDw8IGVuZGw7IC8vIG1vdmUgdG8gbmV4dCBsaW5lCiAgICB9CiAgICAKICAgIHJldHVybiAwOwp9Cg==",
  //remove customeTestcase for submit
  "customTestcase": "MyAzCjEgMiAzCjQgNSA2CjcgOCA5",  
  "language": "cpp",
  "problem_id": 0
}
```

```cpp
#include <iostream>
using namespace std;


// Input : 
// 3 3
// 1 2 3
// 4 5 6
// 7 8 9

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
        cout << endl; 
    }
    
    return 0;
}
```


