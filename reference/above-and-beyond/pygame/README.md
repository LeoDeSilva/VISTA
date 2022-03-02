# Pygame

## Example Code

This code will initalise a pygame window of size 500x500. Each frame, the screen will be cleared and a rectangle will be drawn with its top left corner at position \[225,255], the RGB colour : \[255,0,0] and a size of 50x50 pixels.

```csharp
load pygame; 

newWindow(500,500);

[]int position = [225,225];
[]int RED = [255,0,0];
[]int size = [50,50];

null update(){
    clear([255,255,255]);
    rect(position, size, RED);
}

pygameInit();
```

![](<../../../.gitbook/assets/image (2).png>)

## `pygameInit()`

This initialises the pygame module, meaning that the game screen will be displayed with properties displayed in `newWindow(x,y)` and a clock will be created which handles the tick rate and timings. Without `pygameInit()` the `update()` function will not be called each frame and a window will not be shown. **This should be called at the end of the file.**  If an update function has not been defined, an error will be raised. An `update()` function without the `clear()` function invoked will produce a blank black screen.

```csharp
load pygame;
newWindow(500,500);

null update() {}

pygameInit();
```

``![](<../../../.gitbook/assets/image (1).png>)``

## `update()`

The update function is called each frame, it is where you should draw to the screen and update any logic required each frame such as position. This below code will produce a square that grows with each frame, the rect function is called and the size is divied by 2 since rectangles are drawn from the top left.&#x20;

```csharp
load pygame;
newWindow(500,500);

int size = 0;
null update() {
    clear();
    size = size + 1;
    rect([250-size/2,250-size/2], [size,size], [255,0,0]);
}
pygameInit();
```

![](<../../../.gitbook/assets/image (6).png>)

## `clear()`

Clear is used to clear a screen of all objects, it is usually used at the beginning of a frame. An optional colour parameter can be passed (array of 3 integers) to set a background colour

```csharp
load pygame;
newWindow(500,500);

null update() {
    rect(
        [rnd(0,500), rnd(0,500)], 
        [rnd(200), rnd(200)], 
        [rnd(255), rnd(255), rnd(255)]
    );
}

pygameInit();
```

![](<../../../.gitbook/assets/image (5).png>)

If this code were to use the clear function after every frame, it would be a single rectangle in the screen at a random position, at a random size, with a random colour.

```csharp
load pygame;
newWindow(500,500);

null update() {
    clear([rnd(255), rnd(255), rnd(255)]);
    rect(
        [rnd(0,500), rnd(0,500)], 
        [rnd(200), rnd(200)], 
        [rnd(255), rnd(255), rnd(255)]
    );
}

pygameInit();
```

![](<../../../.gitbook/assets/image (8).png>)

## `tickrate()` & `tick()`

tickrate will set the number of time the update function is called per second and tick will make the system wait for that number of ticks per second. The line `tickrate(1);` below will mean that the `update()` function is called once per second and the image displayed will only change one per second. Note that this value can be a floating point

```csharp
load pygame;
newWindow(500,500);
tickrate(1);

null update() {
    clear([rnd(255), rnd(255), rnd(255)]);
    rect(
        [rnd(0,500), rnd(0,500)], 
        [rnd(200), rnd(200)], 
        [rnd(255), rnd(255), rnd(255)]
    );
}

pygameInit();
```

This will return same result as the figure in the above section, however it will once change once per second. Another alternative is to call `tick(1);` inside the update function, however this is only recomended to slow down a particular update cycle.
