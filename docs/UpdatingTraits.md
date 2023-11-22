# Updating traits

## Add to pta list
To update traits new trait must be added to the `base/traitinfo/ptas.txt` file.

Each trait is represented on a single line in the following format:
```txt
[Name:str]    :   [SD:float]   :   [NM$:float]
```
Example:
```txt
MILK    :   567.0   :   0.02
```

## Add to correlations
After adding pta to `base/traitinfo/ptas.txt` it must also be accounted for in the correlations.

To add trait to correlations `base/traitinfo/correlations.txt` must be updated. ***The correlation matrix is ordered by line appirence in the `ptas.txt` file***.

The matrix rows are separeted by newlines and the columns by space. ***Extra spaces will be trimed.***

Example:
```txt
 1.000  0.399  0.835  0.113  0.179 -0.131
 0.399  1.000  0.591  0.090  0.080 -0.115
 0.835  0.591  1.000  0.128  0.168 -0.100
 0.113  0.090  0.128  1.000 -0.456 -0.221
 0.179  0.080  0.168 -0.456  1.000 -0.192
-0.131 -0.115 -0.100 -0.221 -0.192  1.000
```
***This example is only for six correlations.***