# Ways to ... in multiple technologies

Simple static site generator & database in one Python script that lists various goals and how to achive them in multiple technologies that are often builtin into Linux distributions.

## Usage

To generate `index.html` (which has no dependencies):

```console
$ python generate.py
```

Then you can view it `xdg-open ./index.html` or publish onto your own website!

## Why?

It's a way to learn Linux ecosystem. And a way to drag meme far beyond beeing funny.

## How?

Knowledge is defined in `generate.py` file.
It's used to fill templates (`.template.html` file) to create `index.html` site.
