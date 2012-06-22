# Setting up the project

## Check out the source
First, get a copy of the source:
This assumes a copy of the source code:
```
git clone https://github.com/mrcaps/rainmon
cd rainmon
mkdir etc/tmp
```

## Follow platform-specific instructions

 * Ubuntu 12.04: `setup-ubuntu`
 * Windows 7: `setup-windows`

## See a sample analysis

To see one of the analyses from the paper (e.g. the case explored in Fig. 8 and Fig. 9),
```
cp -r data/cache-cloud-disk-oct12-oct16 etc/tmp/cache/demo
```

then,
```
cd code
make celerystart &
make serverstart &
```

and open a browser window to
```
http://localhost:8000/
```