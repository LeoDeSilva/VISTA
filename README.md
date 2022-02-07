# VISTA
Programming language designed for 2D graphics

## Concept Syntax
```golang
newWindow(500,500)

bool isPrime(int n) {
    for (int i : 2 => n) {
        if (n % i == 0) {
            return false;
        }
    }
    return true;
}

Vector2D position = newVector2(0,0) 

int i = 9;
float n = 0.5;
string s = "hello world";

if (isPrime(i)) {
    text(string(i) + "is prime", position);
} else {
    text(string(i) + "is not prime", position);
}
```

```golang
newWindow(500,500);

int[] randomSize() {
    return [rnd(10), rnd(10)];
}

void update() {
    clear();
    rect(pos, size, BLACK);
}

Vector2 pos = newVector2(1,1);
int[] size = randomSize();
```
