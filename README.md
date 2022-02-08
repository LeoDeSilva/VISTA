# VISTA
Programming language designed for 2D graphics (based off of PyGame)

## Concept 
``` C
![PYGAME]
newWindow(500,500)

global int[] pos = [250, 250]
global int[] prev = pos

int[] offset() {
    return [rnd(-100,100), rnd(-100,100)]
}

null update() {
    tick(1)
    clear()
    prev = pos
    pos = addVector2D(pos, offset())
    rect(prev, [50,50], RED)
    rect(pos, [50,50], BLACK)
}
```
![image](https://user-images.githubusercontent.com/46300158/153036795-6e473b87-acd5-4947-94aa-3db72242b9ef.png)
