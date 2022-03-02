# Pygame - Shapes

## `Rect()`

A rectangle is drawn with its position, size and colour, It is positioned from its top left corner. The position is the first parameter, the size the second and the colour the third

```csharp
load pygame;
newWindow(500,500);

null update() {
    []int position = [200,200];
    []int size = [100,100];
    []int RED = [255,0,0];
    rect(position, size, RED);
}

clear();
pygameInit();
```

![](<../../../.gitbook/assets/image (3).png>)
