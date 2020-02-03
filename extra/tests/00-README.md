# Test of REST API

## Intro
Files to test submitting simulation demand automatically.

## The test code

The file to use is 

```
test_rest_mode.py
```

This code does take for granted python will be able to find both json AND coreapi 
modules in it's environment

But you must : 
 * Adapt it with a valid user/pwd 
 * Make sure it uses the right hostname for the central (this is the one activated by default)
 * Adapt it to use the right request-NNN.json example file
 
This code could easily be adapted to expect a user/pwd/simulation-data-file
 
## The test data

All files ending with *json are test data files.
Those files are supposed to be called by the test_rest_mode.py file and trigger a simulation demand.

The data in most of these files is NOT valid. They were meant to trigger invalid data response.

However the structure is mostly correct, especially request-121-good.json so it would be best to use 
this one as a template for your own data file.
