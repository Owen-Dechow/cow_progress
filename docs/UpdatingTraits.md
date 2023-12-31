# Updating traitsets

Traits in cow_progress are handeld by traitsets, traitsets are a simple collection of PTAs & Recessives for a given set, the number of traitsets is not limited. Each class will be connected to one traitset. After it is connected to a traitset the connected traitset can not be changed.

To ensure a safe transition of traits it is highly suggested that instead of changing a traitset directly a new traitset is created and the old one is disabled.

In the event that a traitset is disabled all classes connected to that traitset will still use that traitset. No new classes using that traitset can be created.

## Adding a new traitset

1. Add traitset directory

   To add a new traitset a traitset folder must be created as a subdirectory of `base/traitinfo/traitsets`. The name of the directory will be the name of the new traitset.

   ***To prevent errors traitsets should not be renamed after class using traitset is created***

   Example:

   ```bash
   .
   ├── base/
   ├───── traitinfo/
   └──────── MyTraitSet/ #New traitset
   ```
2. Register traitset

   To register the traitset, the traitset name must be added to the `register` list in `base/traitinfo/traitsets.py`

   The `register` list is comprised of a tuple of the following format `(traitset_name: str, enabled: bool)`

   `traitset_name` ***must be same name as directory name***

   Example:

   ```python
   register = [
   ("NM_2021", True),
   ("MyTraitSet", True),
   ]

   ...
   ```
3. Add `ptas.txt` to traitset

   Every traitset requires a `ptas.txt` file in he traitset directory. Each trait is represented on a single line in the following format:

   ```txt
   <name:str> : <standard_deviation:float> : <heritability:float> : <net_merit_dollars:float> : <inbreeding_depression_percentage:float>
   ```
   Example:

   `base/traitinfo/traitsets/MyTraitSet/ptas.txt`
   ```txt
   MILK    :   567.0   :   0.20   :   0.02    :   -300
   FAT     :   25.0    :   0.20   :   4.18    :   -10
   PROT    :   15.0    :   0.20   :   4.67    :   -7
   ```
   ***Whitespace surrounding colons will be striped***
4. Adding correlations

   After adding traits to `ptas.txt` each trait ***must*** also be accounted for in the correlation matrix for ***both*** genotype and phenotype.

   To add the correlation matrixes, create a `gen_corr.txt` and a `phen_corr.txt` file in the traitset directory. The correlation matrix for the genotypes should then be placed in the `gen_corr` file and the correlations for the phenotypes should then be placed in the `phen_corr` file.

   ***The order of wich ptas appear in the correlation matrixes are ordered by line appearance in the `ptas.txt` file***.
   The matrix rows are separated by newlines and the columns by space. ***Extra spaces will be striped.***

   Example:

   `base/traitinfo/traitsets/MyTraitSet/gen_corr.txt`
   ```txt
   1.000  0.399  0.835
   0.399  1.000 -0.591
   0.835 -0.591  1.000
   ```

   `base/traitinfo/traitsets/MyTraitSet/phen_corr.txt`
   ```txt
   1.000  0.619  0.901
   0.619  1.000  0.723
   0.901  0.723  1.000
   ```
5. Recessives

   Each traitset also requires a `recessive.txt` file. Every recessive is then represented as a single line in the following format:

   ```txt
   <name:str>  :  <fatal:[f/n]>  :  <prominence:float>  :  <extended_name:str>
   ```
   ***f = fatal, n = nonfatal***

   Example:

   `base/traitinfo/traitsets/MyTraitSet/recessives.txt`
   ```
   BLAD    :   f   :   0.10    :   Bovine Leukocyte Adhesion Deficiency
   DUMPS   :   f   :   0.10    :   Deficiency of Uridine Monophosphate Synthase
   MF      :   n   :   0.10    :   Mulefoot
   ```

   ***Whitespace surrounding colons will be striped***
6. Disable old traitsets

   If there are any old traitsets that classes should not use dissable them in the `base/traitinfo/traitsets.py` file within the `register` list.
