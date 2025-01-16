import os, io, argparse
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

@dataclass
class DispersionFormula:
    zmx_name: str
    zmx_n_coeffs: int
    cv_mnemonic: str
    cv_n_coeffs: int
    def gets_truncated(self):
        return self.zmx_n_coeffs > self.cv_n_coeffs
    
@dataclass
class Glass:
    nd: float
    vd: float
    df: DispersionFormula
    def __post_init__(self):
        self.transmission = []
    def add_transmission_val(self, wvl_um, tr, thickness):
        self.transmission.append([wvl_um, tr, thickness])
    def set_coeffs(self, C):
        self.coeffs = C[0:self.df.cv_n_coeffs]
    
formulae = {
    1: DispersionFormula(
        zmx_name='Schott', 
        zmx_n_coeffs=11,
        cv_mnemonic='LAU',
        cv_n_coeffs=5
        ),
    12: DispersionFormula(
        zmx_name='Extended 2', 
        zmx_n_coeffs=7, 
        cv_mnemonic='GML', 
        cv_n_coeffs=6
        ),
    2: DispersionFormula(
        zmx_name='Sellmeier 1', 
        zmx_n_coeffs=5, 
        cv_mnemonic='GMS', 
        cv_n_coeffs=12
        ),
    11: DispersionFormula( 
        zmx_name='Sellmeier 5', 
        zmx_n_coeffs=9, 
        cv_mnemonic='GMS', 
        cv_n_coeffs=12
        ),
    3: 'Herzberger',
    4: 'Sellmeier 2',
    5: 'Conrady',
    6: 'Sellmeier 3',
    7: 'Handbook of Optics 1',
    8: 'Handbook of Optics 2',
    9: 'Sellmeier 4',
    10: 'Extended',
}

def abbreviate_glassname(name):
    return name.split('-')[-1].split('_')[-1].replace('ultra', 'u').upper()

def parse_agf(lines):
    glasses = {}
    glassname = ''
    formula = ''
    coeffs_truncated = False
    for line in lines:
        cols = [col.strip() for col in line.lower().strip().split()]
        match cols:
            case ['nm', str() as name, str() as i_formula, str() as mil, str() as nd, str() as vd, *_]:
                df = formulae[int(i_formula)]
                if isinstance(df, DispersionFormula):
                    glassname = abbreviate_glassname(name)
                    if len(name) > 8:
                        glassname = glassname[0:8]
                        print(f"Glass name {name.upper()} too long for CodeV, truncated to {glassname}")
                    glasses[glassname] = Glass(float(nd), float(vd), df)
                    if df.gets_truncated():
                        coeffs_truncated = True
                else:
                    print(f"""
                          Glass {glassname} uses dispersion formula Nr{i_formula}
                          /t({df} in Zemax nomenclature), which cannot be trivially (w/o fitting) converted
                          /t into any of CodeV's polynomials.
                          /t Thus {glassname} is left out.
                          """)
                    glassname = ''
            case ['cd', *coeffs] if glassname != '':
                glasses[glassname].set_coeffs([float(c) for c in coeffs])
            case ['it', str() as wvl, str() as t, str() as thickness] if glassname != '':
                glasses[glassname].add_transmission_val(float(wvl), float(t), float(thickness))
    if coeffs_truncated:
        print("Warning: dispersion polynomials have more coeffs than CodeV supports; higher-order coeffs were truncated")
    return glasses

def _run():
    ap = argparse.ArgumentParser(
        description="""
        Converts a Zemax AGF glass catalogue into a
        CodeV user-defined glass file.
        """
    )
    ap.add_argument(
        'agf',
        type=str,
        help="Zemax AGF glass file"
    )
    ap.add_argument(
        '-v',
        action='store_true',
        help='verbose stdout'
    )
    args=ap.parse_args()
    
    with open(args.agf, mode='r', encoding='ansi') as agf_file:
        lines = agf_file.readlines()
    glasses = parse_agf(lines)
    if args.v:
        print(f"\n{len(glasses)} glasses have been read from agf file:")
    
    fig, ax = plt.subplots()
    ax.invert_xaxis()
    N_glasses = len(glasses)
    n = np.ndarray(N_glasses)
    v = np.ndarray(N_glasses)
    out = "PRV"
    for i, (name, glass) in enumerate(glasses.items()):
        coeff_str = ' '.join(str(c) for c in glass.coeffs)
        out += f"\n'{name}' {glass.df.cv_mnemonic} {coeff_str}"
        n[i] = glass.nd
        v[i] = glass.vd
        if args.v:
            print(f"\t{name.ljust(10)} n={str(n[i]).ljust(10)} v={str(v[i]).ljust(10)}")
        ax.annotate(name, (v[i]+0.3, n[i]+0.002))
    out += "\nEND"
    ax.scatter(v,n)

    seqname = os.path.splitext(os.path.basename(args.agf))[0]
    out_path = os.path.join(os.path.dirname(args.agf), f"prv_{seqname}.seq")
    if args.v:
        print(f"Saving .seq private catalogue to {out_path}")
    
    with open(out_path, mode='w', encoding='ansi') as f:
        f.write(out)
    
    plt.show(block=True)

if __name__ == "__main__": _run()