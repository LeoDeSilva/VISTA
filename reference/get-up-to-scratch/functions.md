# Functions

## Function Calls

Functions are called by specifiying the identifier of the function followed by parenthesis with the parameters between. If a function returns a value, it can be assigned to a variable of the same type, e.g.

```csharp
int add(int a, int b) {
    return a + b;
}

int sum = add(15,10);
```

A function that returns no value, cannot be assigned to a value e.g. `string s = print("Hello World");` would produce an error because `print()` does not return a value

## Function Declarations

Function declarations work similarly to variable declaration in that they begin with the return type and then the identifier. Following this, between parenthesis are the parameters, they are formatted with the type and then an identifier.

```csharp
int add(int a, int b) {
    return a + b;
} 

add(10,5);
```

### Null

Null is a placeholder value for a variable, it is used when a function does not return a value e.g.

```csharp
null printName(string name) {
    print("Hello",name);
}

string greeting = printName("Leo");
```

Not that the final line will produce an error since `printName` returns no value
