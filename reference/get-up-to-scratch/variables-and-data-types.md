# Variables and Data Types

## Example Program

The inbuilt data types include `string, int, float`, and `arrays`.  Strings are used to store a series of characters with ints for whole numbers and floats to store floating points. Arrays can store any data type, however all elements must be of the same type. An array data type is initialised with `[]` and then the data type of the elements being stored e.g. `[]float`.&#x20;

```csharp
string stringType = "Hello World";
int intType = 10;
float floatType = 0.32;

[]int intArray = [1,2,3];
[][]string = [["a","b"],["c","d"]];

print(stringType, intArray);
```

## Integers and Floating Points

### Integers

Integers store whole numbers such as `10` or `-20`. These do not contain decimals, however can be negative

```csharp
int age = 15;
print("You are", 18-15, "years of being 18");
```

### Floating Points

Floating point values are any number that contain a decimal point, they can contain as many decimal places as necessary, mathematical operations can be performed with floating points and integers, however an integer cannot be assign to a floating point variable type and vise versa.

```csharp
float difference = 10.5;
float differnece = 10 - 0.4;
```

## Strings

Strings work as they do in languages such as python or javascript, they are a data structure storing a sequence of characters deliminated by quotation marks (' or ") e.g. `"Hello World"`.  Strings can be indexed and unlike some other languages are mutable.

```csharp
string name = "Leo De Silva";
print("Hello " + name); 
```

Strings can also be index, i.e. the character at an index of a string can be extracted through square bracket notation. (Note that indices begin at 0)

```csharp
string name = "Leo";
print(name[0]);
```

However, unlike many languages, strings in VISTA are mutable, this means that they can be modified, for example, a character at an index can be changed without re-creating the entire string

```csharp
string name = "Leo";
name[0] = "l";
print(name);
```

Since this string is mutable, this program will print `"leo"` since the letter at index 0 : `"L"` has been replaced with `"l"`

## Arrays

An array is an ordered collection of data types. Arrays are mutable and can be indexed to extract or modify a specific element. However all elements have to be the same data type. Note that an arrays index begins at 0.

```csharp
[]int numbers = [1,2,3];
int firstElement = numbers[0];
numbers[2] = 4;
print(numbers, firstElement);
```

This would print `[1,2,4] 1` because the last element of the array has been modified and `firstElement` has been assigned to the element at index 0 : `1`

### SubArrays

An element in an array can also be another array

```csharp
[][]int positions = [[10,2],[5,3]];
print(positions[0], positions[0][1]);
```

This program would print `[10,2] 3`, since the element at index 0 is another sub array `[10,2]` and in the second expression, this sublist at index 0 is being indexed at index 1, returning `3`

## Null

Null is a placeholder value for a variable, it is used when a function does not return a value e.g.

```csharp
null printName(string name) {
    print("Hello",name);
}

string greeting = printName("Leo");
```

Not that the final line will produce an error since `printName` returns no value
