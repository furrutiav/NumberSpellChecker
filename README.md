# NumberSpellChecker

## Checker

### Phonetic confusion and word reduction 

| Notation         | Ex.     | Notation         | Ex.     | Notation         | Ex.     |
|--------------|-----------|--------------|-----------|--------------|-----------|
| z>s | diez > dies      | c!0>s | doce > dose | n>m | cuarenta > cuaremta |
| sc>s      |trescientos > tresientos  | s-1> | ciento tres > ciento tre | x>cs | sexto > secsto |
| sc>c | doscientos > docientos | c0>s | cinco > sinco | v>b | veinte > beinte |
|tr>t | cuatro > cuato | ei>e  | treinta > trenta  | i>y | seis > seys |

## Synthetic examples 

| Input         | Output     |
|--------------|-----------|
| a pedro lecedan beintecoches | a pedro lecedan 20 coches |
| grabriel regalo seis ogtavos y lequedaro dos ogtavos | grabriel regalo 6/8 y lequedaro 2/8 |
| jaime aora tyene tresyento trentai ocho | jaime aora tyene 338 |
| es dosiento sincuenta i nueve | es 259 |
| antes tiene tresocien dos | ahora tiene 3 100 2 |
| es cuaremta y uno | es 41 |
| le queda do octavos a pedrita | le queda 2/8 a pedrita |
| lares puesta es setedesimos | lares puesta es 7/10 |

## Worst-cases

| Input         | Output     |
|--------------|-----------|
| uno y me dio | 1/2 |
| sin comer | 5 mer |
...



## References

[Fast Word Segmentation of Noisy Text](https://towardsdatascience.com/fast-word-segmentation-for-noisy-text-2c2c41f9e8da)

## Citar
```
Urrutia, F. NumberSpellChecker. Available online: https://github.com/furrutiav/NumberSpellChecker
```

