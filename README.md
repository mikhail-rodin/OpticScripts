# Code V macros

## How to use
1. Copy into a dir that's traversed by CodeV, e.g. `c:\cvuser\macros\`.
2. Load libraries on startup. Your `defaults.seq` will contain something like this:
    ```
    pth seq pre c:\cvuser\macros\
    ddm m
    in libgeom
    in libmfg
    in globals
    ```
3. Macros with req'd arguments provide 'Usage: ...' notes when invoked w/o args.

These macros, as dowloaded from GitHub, are in UTF8. But since they only use ISO 8859-1 characters, they should be byte-to-byte identical to ASCII and thus palatable to CodeV.

## Lens analysis
+ `res.seq` - resolution figures & transverse aberration plots
+ `petz.seq` - element power distribution and Petzval sums
+ `amag.seq` - afocal magnification
+ `mtf.seq` - resolution figures for any 2 modulation values (default is 0.2 and 0.3)

## Lens modification
+ `ins_elt.seq` - insert a spherical element of given power & bending
+ `ins_xcyl.seq`, `ins_ycyl.seq` - insert a cylindrical element
+ `ins_plate.seq` - insert a (bent) plane parallel plate
+ `bend.seq` - bend a singlet (spherical or cylindrical) to a specified Coddington shape factor
+ `bendflip.seq` - flip a singlet w/o changing its power
+ `cement.seq` - convert a singlet into a cemented doublet
+ `move_srf.seq`
+ `galilean.seq` - insert an afocal galilean subsystem
+ `relay.seq` - create a new lens relaying the current lens' image

  Image becomes object, EXP becomes ENP. Fields, wavelengths and image curvature are taken care of.
+ `sph2xcyl.seq`, `sph2ycyl.seq` - convert surfaces M..N into X or Y cylinders

## Fields setup
+ `fields_diag.seq` - N equal-area field rings
+ `fields_skew.seq` - rectangular angular field with diagonal points
+ `fields_diag2xy.seq` - convert a diagonal field spec to a rectangular with a given aspect ration
+ `fields_xy2diag.seq` - convert a rectagular field spec into a diagonal one

## File management
+ `store.seq` - save and refresh derivatives

    Saves both a binary LEN and a text SEQ file. Deals with a decades-old problem of Code V randomly corrupting the derivative increment vector in LEN files - this is what has been causing all those 'Singular variable' and 'Unstable condition' errors since CV9 or probably even CV8.

+ `get.seq` - list lenses in directory and load by ordinal
  
  This is too much to type:
  ```
  > lib
  > dir *.len
  > can
  > res reverse_telephoto_1f8_v1o2achr1
  > vie; go
  ```
  This is much better:
  ```
  > in get
  > 12 ! load 12th lens in list
  > y
  ```

+ `gsview.seq` - view Nth best GS solution
    
    Requires worksheet recording to be on (`buf y`) during optimization and a `gallery.seq` run immediately after.
    
    Example:
    ```
    buf y
    auto
        gs y
        tim 10
        err cdv
    go
    buf n
    in gallery 

    > in gsview 3 ! load & view third-best lens
    > in gsview   ! view next (4th) lens
    ```

## Libraries & utilities
+ `libgeom.seq` - geometric optics
+ `lib_ys.seq` - Yuan-Seidel anamorphic lens aberrations
+ `libmfg.seq` - manufacturability
+ `libmath.seq` - non-optics specific math
+ `globals.seq` - env var declarations
+ `xy.seq` - plot non-rotationally symmetric lens