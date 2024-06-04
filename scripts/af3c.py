#! /usr/bin/python

from math import tan, atan, radians, degrees, isclose
import os, io, argparse

def gauss_ai(f, ao):
    return ao*f/(ao+f)

class ThinComp:
    def __init__(self, f, sPo, Do, wo, inf_obj=True, ao=0, k=0):
        self.f=f
        self.ao=ao
        self.inf_obj=inf_obj
        if inf_obj:
            self.ai=f
        else:
            self.ai=gauss_ai(f=f, ao=ao)
        self.sPo=sPo 
        self.Do=Do 
        self.wo=wo 
        self.k=k 
        self._pupil_trace()
        self.collimated=isclose(self.ao, -self.f, rel_tol=1e-4, abs_tol=0.0)
        self.V=self._magn()
    def _magn(self):
        if self.collimated:
            return 1.0/self.f
        elif self.inf_obj: 
            return self.f
        else:
            return self.ai/self.ao
    def _pupil_trace(self):
        w = self.wo
        if isclose(self.sPo, 0.0):
            self.sPi=0
            self.Di=self.Do
        else:
            self.sPi = gauss_ai(f=self.f, ao=self.sPo)
            self.Di = self.Do*abs(self.sPi/self.sPo) 
        y1 = self.sPo*tan(radians(w))
        self.D1 = 2*(abs(y1) + (1-self.k)*self.Do/2) 
        self.wi = degrees(atan(tan(radians(w)) + y1/self.f))

class Afocal_3comp:
    def __init__(self, V, L, d1, P1, sP, D, w, k=0):
        self.d1=d1
        self.d2=L-d1
        self.P1=P1
        self.V=V 
        self.D=D 
        self.k=k 
        self.w=w 
        self.sP=sP 
        self.P2=self._P2()
        self.P3=self._P3()
        self.pupil_trace()
    def _P2(self):
        V=self.V; d1=self.d1; d2=self.d2; P1=self.P1
        L=d1+d2
        return (V-L*P1*V-1)/(V*(L-L*P1*d1+P1*d1**2-d1))
    def _P3(self):
        V=self.V; d1=self.d1; d2=self.d2; P1=self.P1
        return (P1*V*d1-V+1)/d2
    def elements(self):
        return [f"""f'={round(c.f, 2)}, a={'INF' if c.inf_obj else round(c.ao)}, sP={round(c.sPo)}, D={round(c.Do, 2)}, D/f'=1:{round(abs(c.f/c.Do),1)}, w={round(c.wo, 2)}, k={c.k}=>D1={round(c.D1)}, w'={round(c.wi)}""" for c in self.components]
    def sPo(self):
        return -self.components[0].sPi
    def pupil_trace(self):
        c1 = ThinComp(f=1.0/self.P1, sPo=self.sP, Do=self.D, wo=self.w, inf_obj=True)
        sP2 = c1.sPi - self.d1
        ao2 = c1.ai - self.d1
        c2 = ThinComp(f=1.0/self.P2, sPo=sP2, Do=c1.Di, wo=c1.wi, inf_obj=False, ao=ao2) 
        sP3 = c2.sPi - self.d2
        ao3 = c2.ai - self.d2
        c3 = ThinComp(f=1.0/self.P3, sPo=sP3, Do=c2.Di, wo=c2.wi, inf_obj=False, ao=ao3, k=self.k)
        self.components = [c1,c2,c3]

def thin2zmx(comp: ThinComp, zmx_version):
    return f"""
    VERS {zmx_version}
    MODE SEQ
    UNIT MM X W X CM MR CPMM
    FLOA
    ENVD 2.0E+1 1 0
    GFAC 0 0
    GCAT SCHOTT
    SDMA 0 1 0
    FTYP 0 0 3 3 0 0 0
    ROPD 2
    PICB 1
    XFLN 0 0 0 0 0 0 0 0 0 0 0 0
    YFLN 0 {comp.wo/2.0} {comp.wo} 0 0 0 0 0 0 0 0 0
    WAVM 1 4.861327E-1 1
    WAVM 2 5.875618E-1 1
    WAVM 3 6.562725E-1 1
    PWAV 2
    GLRS 1 0
    SURF 0
      TYPE STANDARD
      CURV 0.0 0 0 0 0 ""
      HIDE 0 0 0 0 0 0 0 0 0 0
      MIRR 2 0
      SLAB 1
      DISZ {-(-comp.sPo+comp.ao) if not comp.inf_obj else 'INFINITY'}
      DIAM 0 0 0 0 1 ""
      POPS 0 0 0 0 0 0 0 0 1 1 1 1 0 0 0 0
    SURF 1
      STOP
      TYPE STANDARD
      CURV 0.0 0 0 0 0 ""
      HIDE 0 0 0 0 0 0 0 0 0 0
      MIRR 2 0
      SLAB 2
      DISZ {-comp.sPo}
      DIAM {comp.Do} 1 0 0 1 ""
      POPS 0 0 0 0 0 0 0 0 1 1 1 1 0 0 0 0
    SURF 2
      TYPE PARAXIAL
      CURV 0.0 0 0.0 0.0 0
      HIDE 0 0 0 0 0 0 0 0 0 0
      MIRR 2 0
      SLAB 5
      PARM 1 {comp.f}
      PARM 2 1
      DISZ 1.0E+2
      MAZH 0 0
      DIAM 2.881634903542E+1 0 0 0 1 ""
      POPS 0 0 0 0 0 0 0 0 1 1 1 1 0 0 0 0
    SURF 3
      TYPE STANDARD
      CURV 0.0 0 0 0 0 ""
      HIDE 0 0 0 0 0 0 0 0 0 0
      MIRR 2 0
      SLAB 3
      DISZ 0
      DIAM 1.763269807085E+1 0 0 0 1 ""
      POPS 0 0 0 0 0 0 0 0 1 1 1 1 0 0 0 0
    EFFL 0 2 0 0 0 0 {comp.f} 1 0 0
    """    


def _run():
    ap = argparse.ArgumentParser(
        description="First-order data calculator for a Galilean afocal system, of two- or 3-lens variety. Generates Zemax 'paraxial surfaces' (in .zmx output) with correct object & pupil positions for each component lens of the telescope."
    )
    ap.add_argument(
        '-f',
        type=bool,
        dest='to_file',
        default=False,
        metavar='',
        help="Generate a ZMX file instead of printing to stdout"
    )
    ap.add_argument(
        '--zmx-version',
        '-v',
        type=str,
        dest='zmx_version',
        default='140820 75 34900',
        help='Zemax version string (string after VERS in a .zmx file)'
    )
    ap.add_argument(
        '--outputdir',
        '-o',
        type=str,
        metavar='DIR',
        dest='out',
        default='./'
    )
    ap.add_argument(
        '--name',
        '-n',
        type=str,
        dest='name',
        default='af3c',
        help="name prefix for zmx files"
    )
    ap.add_argument(
        '--magn',
        '-V',
        type=float,
        dest='V',
        metavar='MAGNIFICATION',
        default=2,
        help="angular magnification, V=tg(w')/tg(w)"
    )
    ap.add_argument(
        '--length',
        '-L',
        type=float,
        dest='L',
        default=1,
        help="total track from first to last thin lens"
    )
    ap.add_argument(
        '--d1',
        type=float,
        dest='d1',
        required=True,
        help="distance from Lens 1 to Lens 2"
    )
    ap.add_argument(
        '--f1',
        '--efl1',
        type=float,
        dest='f1',
        default=1,
        help="focal lenght of the first component"
    )
    ap.add_argument(
        '--sP',
        '--enpp',
        type=float,
        dest="sP",
        metavar='ENPP',
        default=0,
        help="entrance pupil position relative to the first thin lens; positive is to the right (inside the telescope)"
    )
    ap.add_argument(
        '-D',
        '--enpd',
        type=float,
        metavar='ENPD',
        dest='D',
        default=.1,
        help="entrance pupil diameter"
    )
    ap.add_argument(
        '-w',
        '--half-field',
        type=float,
        dest='w',
        metavar='half_field',
        default='1',
        help="angular object-space half-field in degrees"
    )
    ap.add_argument(
        '--vig-factor',
        type=float,
        dest='vig',
        metavar='k',
        default=0,
        help="vignetting factor for the full-field beam; 1.0 is fully obscured, 0.0 is no vignetting"
    )
    args=ap.parse_args()
    tos = Afocal_3comp(
        V=args.V, 
        L=args.L, 
        d1=args.d1, 
        P1=1.0/args.f1,
        sP=args.sP,
        D=args.D,
        w=args.w,
        k=args.vig
        )
    if args.to_file:
        for i, c in enumerate(tos.components):
                path = os.path.join(args.out, f"{args.name}_{i+1}.zmx")
                with io.open(path, 'w', encoding='utf-16le') as file:
                    file.write(thin2zmx(c, args.zmx_version))
    else:
        print(tos.elements())

if __name__ == "__main__": _run()