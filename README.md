# VISTA
Programming language designed for 2D graphics (based off of PyGame)

## Example 
``` c#
load pygame;

newWindow(500,500);
tickrate(1.5);

[]int pos = [250, 250];
[]int prev = pos;
[]int size = [100,100];

int clamp(int value, int min, int max) {
    if (value < min) {
        return min;
    } elif (value > max) {
        return max;
    }
    return value;
}

null update() {
    clear();

    prev = pos;
    []int offset_value = [rnd(-100,100), rnd(-100,100)];
    pos = [
        clamp(pos[0] + offset_value[0], 0, 400),
        clamp(pos[1] + offset_value[1], 0, 400),
    ];

    rect(prev, size, [255,0,0]);
    rect(pos, size, [0,0,0]);
}

pygameInit();
```
![image](https://user-images.githubusercontent.com/46300158/153037130-9538d5fd-0746-4a6a-8ea4-f1be54cff733.png)
