# OpticScripts
- [Standalone scripts](#standalone-scripts)
- [CodeV macros](#codev-macros)
- [Zemax macros](#zemax-macros)
- [Converters](#converters)

## Standalone scripts

+ `cam.py` - focusing cam generator

  Creates cam functions (tabulated and approximated) for floating elements based on zoom data in a CodeV `.seq` file. Distance to object (S0 thickness) is converted to diopters and treated as a free variable that other zoomed thicknesses depend on.

  Unlike CodeV built-in CAM option, uses Akima splines for interpolation and offers power series approximation. Plots airspace thickness and approximation error graphs.

+ `af3c.py` - first order layout of a 3-group Galilean telescope
  
  Generates 3 Zemax files for each of the 'scope's thin lenses. Those can be transformed into thick groups using Russinov's methodology, pre-optimized independently for minimum tolerance sensitivity with a curved field, and eventually assembled into a flat-field system.

## CodeV macros

### How to use
1. Copy into a dir that's traversed by CodeV, e.g. `c:\cvuser\macros\`.
2. Load libraries on startup. Your `defaults.seq` will contain something like this:
    ```
    pth seq pre c:\cvuser\macros\
    ddm m
    in libmath
    in libtxt
    in libgeom
    in libmfg
    in globals
    ```
3. Macros with req'd arguments provide 'Usage: ...' notes when invoked w/o args.

These macros, as dowloaded from GitHub, are in UTF8. But since they only use ISO 8859-1 characters, they should be byte-to-byte identical to ASCII and thus palatable to CodeV.

### Lens analysis
+ `res.seq` - resolution figures & transverse aberration plots
+ `petz.seq` - element power distribution and Petzval sums
+ `amag.seq` - afocal magnification
+ `mtf.seq` - resolution figures for any 2 modulation values (default is 0.2 and 0.3)

### Plotting
+ `lay.seq` - view lens at one (e.g. `in lay 2`) or every (just `in lay` w/o args) zoom position with auto scaling and color coded surface types
+ `xz.seq` - same as `lay.seq`, but XZ section is shown instead of YZ
+ `xy.seq` - 3D plot of a lens

### Lens synthesis & modification
+ `reverse.seq` - flip lens & auto-convert fields and pupils
+ `ins_lens.seq` - fully interactive insertion of a subsystem from a lens file

  Unlike CodeV built-in `COPY` command, this macro
  1. takes care of zoom data (variable airspaces and conjugates);
  2. recognizes a relay/converter inserted right before the image and brings along its image-space conjugates;
  3. doesn't require a long string of parameters: lens file and surface indices are specified interactively.
  
  Because of (3), both main and aux lenses have to be in the same directory.

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
+ `apertures.seq` - auto set hard apertures (rectangular if element is not rotationally symmetric).

### Optimization

+ `wtz.seq` - matrix of optimization weigths for each field at every zoom position

  All field weights for a given zoom position can be scaled at once with `in wtz [z] [multiplier]` - `wtz.seq` acts like a 'missing' WTZ command would've acted.

### Fields setup
+ `fields_diag.seq` - N equal-area field rings
+ `fields_skew.seq` - rectangular angular field with diagonal points
+ `fields_diag2xy.seq` - convert a diagonal field spec to a rectangular with a given aspect ration
+ `fields_xy2diag.seq` - convert a rectagular field spec into a diagonal one

### File management
+ `store.seq` - save and refresh derivatives

    Saves both a binary LEN and a text SEQ file. Deals with a decades-old problem of Code V randomly corrupting the derivative increment vector in LEN files - this is what has been causing all those 'Singular variable' and 'Unstable condition' errors since CV9 or probably even CV8.

+ `get.seq` - search for lenses in directory and load by ordinal
  
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
  > in get 'rev'
  > 12
  > y
  ```
  Here, all lenses with 'rev' in the name are listed, and you select the №12. 
  If no search string is specified, all LEN files in the directory are displayed.

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

### Libraries & utilities
+ `libgeom.seq` - geometric optics
+ `lib_ys.seq` - Yuan-Seidel anamorphic lens aberrations
+ `libmfg.seq` - manufacturability
+ `libmath.seq` - non-optics specific math
+ `libtxt.seq` - string processing
+ `globals.seq` - env var declarations

## Zemax macros
+ `autocentering.zpl` - fill in wedge tolerances for elements that can self-center in a grinder's chuck

## Converters
+ `cvmacro/zmx_plate_import.seq` - convert Zemax `.tpd` test plate file into a `.seq` file that can be used by Code V's TES option