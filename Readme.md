CancellationToken for Python
---

This library provide simple cancellation token. 

# Usage

First create token
```python
from cancel_token import CancellationToken

token = CancellationToken()
```

At any point in time you can check if token has been cancelled:
```python
if token.cancelled:
    print('Operation already cancelled')
    return None  
```

To cancel token call its `cancel` method:
```python
token.cancel()
assert token.cancelled
```

It is also possible to add callbacks that will be called on when token is cancelled:
```python
def handler():
    print('Operation has been cancelled')

token.on_cancel(handler)
```

**Note**:
* If token is already cancelled, callback will be invoked immediately.
* All registered callbacks will be called sequentially during `cancel` call.
* Callback throwing exception will prevent remaining callbacks from calling. However token will be cancelled
* During callback invocation token is already cancelled
* It is possible to add callback from within callback
* Removing callback from within callback **will not** prevent its execution
 
