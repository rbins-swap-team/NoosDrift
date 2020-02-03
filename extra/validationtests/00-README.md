# Test files 

These files are used to test the SimulationDemandForm validation procedures

To use them properly, you must have a proper django environment set up. 
Start the django app in shell mode then use the following code

```
import json 
from noos_viewer.forms import SimulationDemandForm

a_parameter_dict = {}
with open('./validationtest/the_simulation-01.json') as a_parameter_f:
    a_parameter_dict = json.load(a_parameter_f)

a_form = SimulationDemandForm(data=a_parameter_dict)
a_form.is_valid()
```

Most of these files are meant to get a 'False' response.

Especially if you take into account the date element which 
will check form data stays int the [-4 days, +4 days] window.

To check the errors you can use
```
print(a_form.errors)
``` 