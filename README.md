# VISTA
Programming language designed for 2D graphics (based off of PyGame)

## Concept 
``` typescript
![PYGAME]
newWindow(500,500)

[]int pos = [250, 250]
[]int prev = pos

[]int offset() {
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
![image](https://user-images.githubusercontent.com/46300158/153037130-9538d5fd-0746-4a6a-8ea4-f1be54cff733.png)
