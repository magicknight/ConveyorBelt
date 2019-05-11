import numpy as np
import typing as t
import math
import scipy.constants as const

class potential:
    '''
    potential base class
    '''

    def __init__(self, *kargs):
        return

    def _check_positions_type(self, positions:t.List[float])->t.List[float]:
        if (any([type(positions) == typ for typ in [float, int, str]])):
            positions = [float(positions)]
        elif(type(positions) != list):
            positions = list(map(float, list(positions)))
        return positions

    def _calculate_energies(self, positions:t.List[float], *kargs):
        raise NotImplementedError("Function " + __name__ + " was not implemented for class " + str(__class__) + "")

    def _calculate_dhdpos(self, positions:t.List[float], *kargs):
        raise NotImplementedError("Function " + __name__ + " was not implemented for class " + str(__class__) + "")

    def ene(self, positions:(t.List[float] or float), *kargs) -> (t.List[float] or float):
        '''
        calculates energy of particle
        :param lam: alchemical parameter lambda
        :param pos: position on 1D potential energy surface
        :return: energy
        '''

        positions = self._check_positions_type(positions)
        return self._calculate_energies(positions)

    def dhdpos(self, positions:(t.List[float] or float), *kargs) -> (t.List[float] or float):
        '''
        calculates derivative with respect to position
        :param lam: alchemical parameter lambda
        :param pos: position on 1D potential energy surface
        :return: derivative dh/dpos
        '''
        positions = self._check_positions_type(positions)
        return self._calculate_dhdpos(positions)


class perturbedPotential(potential):
    def _calculate_energies(self, positions:t.List[float], lam:float):
        raise NotImplementedError("Function " + __name__ + " was not implemented for class " + str(__class__) + "")

    def _calculate_dhdpos(self, positions:t.List[float], lam:float):
        raise NotImplementedError("Function " + __name__ + " was not implemented for class " + str(__class__) + "")

    def _calculate_dhdlam(self, positions:t.List[float], lam:float):
        raise NotImplementedError("Function " + __name__ + " was not implemented for class " + str(__class__) + "")

    def ene(self, positions:(t.List[float] or float), lam:float) -> (t.List[float] or float):
        '''
        calculates energy of particle
        :param lam: alchemical parameter lambda
        :param pos: position on 1D potential energy surface
        :return: energy
        '''
        positions = self._check_positions_type(positions)
        return self._calculate_energies(positions, lam=lam)

    def dhdpos(self, positions:(t.List[float] or float), lam:float) -> (t.List[float] or float):
        '''
        calculates derivative with respect to position
        :param lam: alchemical parameter lambda
        :param pos: position on 1D potential energy surface
        :return: derivative dh/dpos
        '''
        positions = self._check_positions_type(positions)
        return self._calculate_dhdpos(positions, lam=lam)

    def dhdlam(self, positions:(t.List[float] or float), lam:float) -> (t.List[float] or float):
        '''
        calculates derivative with respect to lambda value
        :param lam: alchemical parameter lambda
        :param pos: position on 1D potential energy surface
        :return: derivative dh/dlan
        '''
        positions = self._check_positions_type(positions)
        return self._calculate_dhdlam(positions, lam=lam)


class harmonicOsc1D(potential):
    '''
    unperturbed harmonic oscillator potential
    '''
    x_shift = None
    fc = None

    def __init__(self, fc:float=1.0, x_shift:float=0.0, y_shift:float=0.0):
        '''
        initializes harmonicOsc1D class
        :param fc: force constant
        :param x_shift: minimum position of harmonic oscillator
        '''
        super(harmonicOsc1D, self).__init__()
        self.fc = fc
        self.x_shift = x_shift
        self.y_shift = y_shift

    def _calculate_energies(self, positions:t.List[float], *kargs) -> (t.List[float]):
        return [0.5 * self.fc * (pos - self.x_shift) ** 2 - self.y_shift for pos in positions]

    def _calculate_dhdpos(self, positions:t.List[float], *kargs) -> (t.List[float]):
        return [self.fc * (pos - self.x_shift) for pos in positions]


class doubleWellPot1D(potential):
    '''
    unperturbed double well potential
    '''
    a = None
    b = None
    Vmax = None

    def __init__(self, Vmax=100.0, a=0.0, b=0.5):
        '''
        initializes double well potential
        :param Vmax:
        :param a:
        :param b:
        '''
        super(potential).__init__()
        self.Vmax = Vmax
        self.a = a
        self.b = b


    def _calculate_energies(self, positions:t.List[float], *kargs) -> (t.List[float]):
        return [self.Vmax / self.b ** 4 * ((pos - self.a / 2) ** 2 - self.b ** 2) ** 2 for pos in positions]

    def _calculate_dhdpos(self, positions:t.List[float], *kargs) -> (t.List[float]):
        return [4 * self.Vmax / self.b ** 4 * ((pos - self.a / 2) ** 2 - self.b ** 2) * (pos - self.a / 2) for pos in positions]


class pertHarmonicOsc1D(perturbedPotential):
    def __init__(self, fc=1.0, alpha=10.0, gamma=0.0):
        '''
        Initializes a potential of the form V = 0.5 * (1 + alpha * lam) * fc * (pos - gamma * lam) ** 2
        :param fc: force constant
        :param alpha: perturbation parameter for width of harmonic oscillator
        :param gamma: perturbation parameter for position of harmonic oscillator
        '''
        super(potential).__init__()

        self.fc = fc
        self.alpha = alpha
        self.gamma = gamma

    def _calculate_energies(self, positions:(t.List[float] or float), lam:float=1.0) -> t.List[float]:
        return [0.5 * (1.0 + self.alpha * lam) * self.fc * (pos - self.gamma * lam) ** 2 for pos in positions]

    def _calculate_dhdpos(self, positions:(t.List[float] or float), lam:float=1.0) -> t.List[float]:
        return [(1.0 + self.alpha * lam) * self.fc * (pos - self.gamma * lam) for pos in positions]

    def _calculate_dhdlam(self, positions:(t.List[float] or float), lam:float=1.0)  -> t.List[float]:
        return [0.5 * self.alpha * self.fc * (pos - self.gamma * lam) ** 2 - (
                1.0 + self.alpha * lam) * self.fc * self.gamma * (pos - self.gamma * lam) for pos in positions]


class linCoupledHosc(potential):
    def __init__(self, ha=harmonicOsc1D(fc=1.0, x_shift=0.0), hb=harmonicOsc1D(fc=11.0, x_shift=0.0)):
        super(potential).__init__()

        self.ha = ha
        self.hb = hb

    def _calculate_energies(self, positions:(t.List[float] or float), lam:float=1.0) -> (t.List[float] or float):
        return [(1.0 - lam) * self.ha.ene(lam, pos) + lam * self.hb.ene(lam, pos) for pos in positions]

    def _calculate_dhdpos(self, positions:(t.List[float] or float), lam:float=1.0) -> (t.List[float] or float):
        return [(1.0 - lam) * self.ha.dhdpos(lam, pos) + lam * self.hb.dhdpos(lam, pos) for pos in positions]

    def _calculate_dhdlam(self, positions:(t.List[float] or float), lam:float=1.0) -> (t.List[float] or float):
        return [self.hb.ene(lam, pos) - self.ha.ene(lam, pos) for pos in positions]


class expCoupledHosc(potential):
    def __init__(self, ha=harmonicOsc1D(fc=1.0, x_shift=0.0), hb=harmonicOsc1D(fc=11.0, x_shift=0.0), s=1.0, temp=300.0):
        super(potential).__init__()

        self.ha = ha
        self.hb = hb
        self.s = s
        self.beta = const.gas_constant/1000.0 * temp

    def _calculate_energies(self, positions:(t.List[float] or float), lam:float=1.0) -> (t.List[float] or float):
        return [-1.0 / (self.beta * self.s) * np.log(
            lam * np.exp(-self.beta * self.s * self.hb.ene(lam, pos)) + (1.0 - lam) * np.exp(
                -self.beta * self.s * self.ha.ene(lam, pos))) for pos in positions]

    def _calculate_dhdpos(self, positions:(t.List[float] or float), lam:float=1.0) -> (t.List[float] or float):
        return [1.0 / (lam * np.exp(-self.beta * self.s * self.hb.ene(lam, pos)) + (1.0 - lam) *
                      np.exp(-self.beta * self.s * self.ha.ene(lam, pos))) * \
               (lam * self.hb.dhdpos(lam, pos) * np.exp(-self.beta * self.s * self.hb.ene(lam, pos)) + (1.0 - lam) *
                self.ha.dhdpos(lam, pos) * np.exp(-self.beta * self.s * self.ha.ene(lam, pos))) for pos in positions]

    def _calculate_dhdlam(self, positions:(t.List[float] or float), lam:float=1.0) -> (t.List[float] or float):
        return [-1.0 / (self.beta * self.s) * 1.0 / (
                lam * np.exp(-self.beta * self.s * self.hb.ene(lam, pos)) + (1.0 - lam) * np.exp(
            -self.beta * self.s * self.ha.ene(lam, pos))) * (
                       np.exp(-self.beta * self.s * self.hb.ene(lam, pos)) - np.exp(
                   -self.beta * self.s * self.ha.ene(lam, pos))) for pos in positions]


class envelopedPotential(potential):
    V_is:t.List[potential]=None
    E_is:t.List[float]=None
    numStates:int=None
    s:float=None

    def __init__(self, V_is: t.List[potential], s: float = 1.0, Eoff_i: t.List[float] = None):
        """

        :param V_is:
        :param s:
        :param Eoff_i:
        """
        super(potential).__init__()
        self.numStates = len(V_is)
        if (self.numStates < 2):
            raise IOError("It does not make sense enveloping less than two potentials!")
        if (Eoff_i == None):
            Eoff_i = [0.0 for state in range(len(V_is))]
        elif (len(Eoff_i) != self.numStates):
            raise IOError(
                "Energy offset Vector and state potentials don't have the same length!\n states in Eoff " + str(
                    len(Eoff_i)) + "\t states in Vi" + str(len(V_is)))

        self.V_is = V_is
        self.s = s
        self.Eoff_i = Eoff_i

    def _calculate_energies(self, positions:(t.List[float] or float), *kargs) -> list:
        Vrs = []
        for pos in positions:
            partA = [-self.s * (Vit - self.Eoff_i[0]) for Vit in self.V_is[0].ene(pos)]
            partB = [-self.s * (Vit - self.Eoff_i[1]) for Vit in self.V_is[1].ene(pos)]
            sum_prefactors = [max(A_t, B_t) + math.log(1 + math.exp(min(A_t, B_t) - max(A_t, B_t))) for A_t, B_t in
                              zip(partA, partB)]

            # more than two states!
            for state in range(2, self.numStates):
                partN = [-self.s * (Vit - self.Eoff_i[state]) for Vit in self.V_is[state].ene(pos)]
                sum_prefactors = [max(sum_prefactors_t, N_t) + math.log(
                    1 + math.exp(min(sum_prefactors_t, N_t) - max(sum_prefactors_t, N_t))) for sum_prefactors_t, N_t in
                                  zip(sum_prefactors, partN)]

            Vrs.append(sum([-1 / float(self.s) * partitionF for partitionF in sum_prefactors]))
        return Vrs

    def _calculate_dhdpos(self,  positions:(t.List[float] or float), *kargs):
        raise NotImplementedError("Function "+__name__+" was not implemented for class "+str(__class__)+"")

class envelopedDoubleWellPotential(envelopedPotential):
    def __init__(self, y_shifts: list = None, x_shifts=None,
                 smoothing: float = 1, fcs=None):
        if (y_shifts == None):
            y_shifts = [0, 0]
        if (x_shifts == None):
            x_shifts = [-1, 1]
        if (fcs == None):
            fcs = [1, 1]

        V_is = [harmonicOsc1D(x_shift=x_shift, y_shift=y_shift, fc=fc)
                for y_shift, x_shift, fc in zip(y_shifts, x_shifts, fcs)]
        super().__init__(V_is=V_is, s=smoothing)