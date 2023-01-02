# VISTA

## What is VISTA
VISTA is an unstable mess of a programming langauge with error messages that will make you want to pull out your hair. It is a statically typed language with typing similar to C# and syntax similar to that of javascript. It is intended for smaller demo projects where frustrating error messages will not make you destroy your entire computer in rage as you attempt to write code that due to no fault of yours, it horrificly mangled in a buggy compiler. 

https://leo-de-silva.gitbook.io/vista/

## Example 
Usage, `git clone` repository and `cd` into directory, to interpret a file, `python3 vista.py <prog>.vista`. For example, by running `python3 vista.py examples/sorting.vista` in the base, directory (code below), the following output should be produced in a window.
```C#
load pygame;
newwindow(500,500);

int element_number = 500;

// fill array with random integers -> 100 length
[]int populatearray() {
    []int array = [];
    for (int i => range(element_number)) {
        array = append(array, rnd(500));
    }
    return array;
}

[]int bubblesort([]int list) {
    for(int i => range(length(list))) {
        // for every element in array, switch if greater, this moves the greatest value to the end
        // repeat for each element in the array
        for (int j => range(length(list) - 1)) {
            // if a is greater than a+1, then switch there places
            // if this is repeated for each element, the greatest element will be moved to the end of the array
            if (list[j] > list[j+1]) {
                int nextelement = list[j+1];
                list[j+1] = list[j];
                list[j] = nextelement;
            }
        }
        drawbars(list);
    }
    return list;
}

// draw a graphical representation of the array
null drawbars([]int list) {
    clear();

    float gap = 500/length(list);
    int i = 0;

    for (int element => list) {
        rect(
            [int(i*gap), 500-element], 
            [float(gap),float(element)], 
            [0,0,0]
        );

        i = i + 1;
    }
    updatescreen();
}

[]int rnd_array = populatearray();
pygameinit(null => (){
    rnd_array = bubblesort(rnd_array);
});
```

![image](https://user-images.githubusercontent.com/46300158/210254540-f33681cd-7a77-4636-b5b6-ad3b4064b940.png)

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
