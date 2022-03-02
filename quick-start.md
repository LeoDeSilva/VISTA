# Quick Start

## What Is VISTA

VISTA is a programming language with typing similar to c# and syntax similar to javascript. It is a general purpose programming language with integrated support for pygame

## Install VISTA

Pyinstaller is the easier distribution method, however compile times are slower than through python3

{% tabs %}
{% tab title="Source" %}
```
git clone https://github.com/leoDesilva/VISTA.git
cd VISTA
```
{% endtab %}

{% tab title="Pyinstaller" %}
```
git clone https://github.com/leoDesilva/VISTA.git
cd VISTA
pyinstaller vista.py
```

Note that binary file is located at:  `./dist/vista/vista`, If you want to run this outside of the base directory, add the `./dist/vista` directory to `PATH`
{% endtab %}
{% endtabs %}

## Useage

Call file and specify path to file as arguments e.g.&#x20;

{% tabs %}
{% tab title="Binary" %}
```
./vista <path to excecutable>
./vista examples/converter.vista
```
{% endtab %}

{% tab title="Python" %}
```python
python3 vista.py <path to file>
python3 vista.py examples/converter.vista
```
{% endtab %}
{% endtabs %}
