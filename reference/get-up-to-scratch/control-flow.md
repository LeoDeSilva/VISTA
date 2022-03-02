# Control Flow

## Conditional Statements

Conditional statements take the form of `if-statements`, they accept a condition between brackets which should return a boolean value and a consequence between curly braces. They can also except an else clause which will be excecuted if no other conditions pass

```csharp
if (10 != 100) {
    print("Obviously!");
} else {
    print("Wait a minute???");
}
```

Conditional statements also except an else if clause in the form `elif`. This takes a condition and a consequence. An elif clause will be evaluated if all above conditions fail and the elif condition passes.

```csharp
int age = int(input("Enter your age:"));

if (age > 100) {
    print("You don't have long left!!!");
} elif (age < 10) {
    print("You have quite a long time left.");
} else {
    print("Yeah you're fine for time");
}
```

## Loops

Loops in VISTA come in two forms, `while loops` and `for loops`. While loops loop while a condition is satisfied and for loops loop through an array of values.

### While Loops

While loops work much like an if statement, however instead of executing the consequence once, it is excecuted untill the condition is false

```csharp
int i = 0;
while (i < 10) {
    i = i + 1;
}
```

### For Loops

For loops loop over an array, storing the current element in a local variable, on the left of the =>, is the variable to be assigned, it requires the type and the identifier to be stored in, on the right side is the array to be looped over.

```csharp
[]string names = ["Leo","William","Ted"];
for (string name => names) {
    print(name);
}
```

#### Range() Keyword

The `range()` keyword can be used to create an array of integers up to a certain value, it can take a minimum value and a maximum value. However, if just 1 parameter is passed, it will be considered the maximum. It works similar to python, however produced an array

```csharp
for (int i => range(10)){
    print(i);
}
```

