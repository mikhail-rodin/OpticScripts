import os, io, argparse

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import Akima1DInterpolator
from numpy.polynomial import Polynomial

from dataclasses import dataclass

@dataclass
class ZoomedParam:
    surface_index: int()
    positions: list[float()]

class InterpolatedParam:
    def __init__(self, zoompoints: ZoomedParam, refpoints: ZoomedParam):
        x = refpoints.positions
        y = zoompoints.positions
        self._xpts = np.empty(0) # for caching
        self._ypts = np.empty(0)
        self._poly = Polynomial([0])
        self.ref_min = min(x)
        self.ref_max = max(x)
        self.surface_index = zoompoints.surface_index
        self.spline = Akima1DInterpolator(x, y)
    def _eval_x(self, steps):
        if self._xpts.size != steps:
            self._xpts = np.linspace(self.ref_min, self.ref_max, steps)
    def _eval_y(self, steps):
        self._eval_x(steps)
        if self._ypts.size != steps:
            self._ypts = self.spline(self._xpts)
    def evaluate(self, steps=200):
        self._eval_y(steps)
        return self._ypts
    def _fit(self, degree, steps):
        self._eval_y(steps)
        if self._ypts.size != steps or self._poly.degree() != degree:
            self._poly = Polynomial.fit(self._xpts, self._ypts, degree)
    def polynomial(self, degree=4, steps=200):
        self._fit(degree, steps)
        return self._poly

def _run():
    ap = argparse.ArgumentParser(
        description="""
        Interpolates zoomed thicknesses in a CodeV .seq file, saves the resulting cam data to a file and provides a polynomial fit.
        \nAkima splines are used for interpolation, power series for approximation.
        """
    )
    ap.add_argument(
        'seqfile',
        type=str,
        help="CodeV SEQ lens file"
    )
    ap.add_argument(
        '-d', '--degree',
        type=int,
        default=3,
        dest='degree',
        help="degree of approximation (not inteprolation!) polynomial, 3rd (cubic) by default."
    )
    ap.add_argument(
        '-r', '--resolution',
        type=int,
        default=200,
        dest='res',
        help="number of spline evaluation points, 200 by default"
    )
    args=ap.parse_args()
    
    with open(args.seqfile, mode='r', encoding='ansi') as seq:
        lines = seq.readlines()

    zoomed_airspaces = []
    for line in lines:
        cols = [col.strip() for col in line.lower().strip().split()]
        match cols:
            case ['zoo', 'thi', str() as qualifier, *d_vals] if qualifier[0] == 's':
                i_srf = int(qualifier[1:])
                zp = ZoomedParam(surface_index=i_srf, positions=[float(d) for d in d_vals])
                if i_srf == 0:
                    zoomed_obj_dist = zp
                else:
                    zoomed_airspaces.append(zp)

    divergence = ZoomedParam(0, [1.0/thi for thi in zoomed_obj_dist.positions])
    cams = [InterpolatedParam(za, divergence) for za in zoomed_airspaces]

    degree = args.degree
    steps = args.res
    fig, ax = plt.subplots()
    fig2, ax2 = plt.subplots()
    ax2.set_yscale('log')
    x_min = min(divergence.positions)
    x_max = max(divergence.positions)
    print(f"""
    Distance to object in diopters (1000/[S{divergence.surface_index} thickness], range is [{x_min}, {x_max}]) is used as a free variable; following airspace thicknesses are represented as its functions. 
    """)
    x = np.linspace(x_min, x_max, steps)
    columns = [x]
    for cam in cams:
        y = cam.evaluate(steps)
        columns.append(y)
        p = cam.polynomial(degree, steps)
        y_poly = p(x)
        err = y_poly - y
        err_rms = np.sqrt(np.mean(err**2))
        err_max = np.max(np.abs(err))
        print(f"""
        S{cam.surface_index}: thickness range [{np.min(y)}; {np.max(y)}]
        \t Fitted with: {p}
        \t RMS error {1e3*err_rms}, maximum error {1e3*err_max} micrometers
        """)
        ax.plot(x, y, label=f"d{cam.surface_index}")
        ax2.plot(err, label=f"d{cam.surface_index}")
    ax.legend()
    ax2.legend()
    table = np.column_stack(columns)

    name = os.path.splitext(os.path.basename(args.seqfile))[0]
    out_path = os.path.join(os.path.dirname(args.seqfile), f"{name}.csv")
    np.savetxt(out_path, table, delimiter=',')

    plt.show(block=True)
if __name__ == "__main__": _run()