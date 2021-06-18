# Custom views

We will find in this directory the custom views available to display the storage tree.

You can use a custom view to create a visualization of the storage tree: 
TXT, HTML, CSV, XML, and so on ; you decide !

## Implementing a new view: a practical guide

Let's implement a simple TXT view to demonstrate the process (spoiler: it's pretty simple).

First, create a new Python file with the name of your view.  
The name should be lowercase, and contain no special character (spaces forbidden).
It should be kept simple and to-the-point.

    touch storage_tree/views/txt.py

Next, write a new class `View` (it **must** have this name),
which will inherit `BaseView`, which we will import from `base`.

```python
from .base import BaseView


class View(BaseView):
    pass
```

Next up is to rewrite the three mandatory static methods: 
- `std_repr`
- `stf_repr`
- `st_repr`

Each of these take exactly one argument: an object.

These methods actually mock the `__repr__()` magic method of each class.

```python
from .base import BaseView


class View(BaseView):
    
    @staticmethod
    def std_repr(obj):
        # Mocks StorageTreeDirectory.__repr__()
        pass
    
    @staticmethod
    def stf_repr(obj):
        # Mocks StorageTreeFile.__repr__()
        pass
    
    @staticmethod
    def st_repr(obj):
        # Mocks StorageTree.__repr__()
        pass
```

For more information about what these methods do and how to implement them properly, 
have a look at the source code of `storage_tree.views.base.BaseView`.

Now, let's write some code !

The logic is simple: the `st_repr` method, the root's, will only be called once (see code for full explanation),
so we can technically use it as a wrapper (see `html_colored` view for an example of this process).  
We won't be doing that here because it's not necessary with a `txt` format.

```python
from .base import BaseView


class View(BaseView):

    @staticmethod
    def std_repr(obj):
        # Compute indentation
        indent = obj.level * "  "
        # Create string:
        # We add the indentation, then the directory's name,
        # then a slash, to indicate it is a directory.
        r = f"{indent}{obj.name}/\n"
        # For each children the directory has,
        for child in obj.children:
            # We'll just append the repr of each child.
            # As we'll see in the next method, 
            # it takes care of properly displaying itself.
            r += child.__repr__()
        # Return the full string
        return r

    @staticmethod
    def stf_repr(obj):
        # Compute indentation
        indent = obj.level * "  "
        # Same as above, except this time not slash,
        # but the size of the object 
        # (in bytes, see code of `storage_tree.StorageTreeFile`).
        r = f"{indent}{obj.name} - {obj.size}\n"
        # Return the string
        return r

    @staticmethod
    def st_repr(obj):
        # Just return the repr of the root, 
        # which is the root StorageTreeDirectory.
        return obj.root.__repr__()
```

There you go !

If that's still unclear, please refer to the source code directly, 
or push modification requests to this document to improve it ;-)
