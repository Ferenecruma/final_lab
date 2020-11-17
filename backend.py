# Чергикало Денис група ОМ-4

from tkinter.ttk import *
from tkinter import *
import numpy as np
import ast
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

import sympy
from sympy import *
from sympy.functions.elementary.complexes import sign
from sympy.utilities.lambdify import lambdify
from sympy.parsing.sympy_parser import parse_expr

t, x0, x1, t_, x0_, x1_ = symbols("t x0 x1 t_ x0_ x1_")
ex_ = Function('ex_')

arg = {
    "T": 1.0,
    "l_0": 20,
    "l_g": [20, 20],
    "m_0": 20,
    "m_gamma": 20,
    "a0": 0,
    "a1": 0,
    "b0": 1,
    "b1": 1,
    "y_to_generate_conditions": "10*cos(x0)+10*sin(x1)+t",
    "G": "Piecewise((0, (t - t_) <= 0),(Max(0,((4 * pi * 1 * (t - t_)) ** (-1/2))* exp(-((x0 - x0_) ** 2) / (4 * 1 * (t - t_))),),True))",
    "L": "diff(ex_(t,x0,x1), t) - 1 * (diff(diff(ex_(t,x0,x1), x0), x0) + diff(diff(ex_(t,x0,x1), x1), x1))",
}


class Discret_System:
    def __init__(self, X_L_0, X_L_gamma, X_M_0, X_M_gamma):
        
        self.l_0 = X_L_0.shape[0]
        self.l_g = [X_L_gamma[0].shape[0],X_L_gamma[1].shape[0]]
        self.l_gamma = sum(self.l_g)

        self.m_0 = X_M_0.shape[0]
        self.m_gamma = X_M_gamma.shape[0]

        self.L = lambda exp: simplify(parse_expr(arg["L"]).subs({ex_(t,x0,x1): exp}))
        self.L_0 = lambda exp: exp
        self.L_gamma = lambda exp: [exp, exp]  # для x0 - с края a0 и b0 соответственно

        self.G = parse_expr(arg["G"])

        self.real_u, self.cond0, self.cond_gamma = self.create_conditions(
            parse_expr(arg["y_to_generate_conditions"])
        )

        self.G_0, self.G_gamma = self.create_L_G()

        A11 = np.array(
            [[self.G_0(x_l.tolist(), x_m.tolist()) for x_m in X_M_0] for x_l in X_L_0]
        )
        A12 = np.array(
            [
                [self.G_0(x_l.tolist(), x_m.tolist()) for x_m in X_M_gamma]
                for x_l in X_L_0
            ]
        )
        A21 = []
        for i in np.arange(len(self.G_gamma)):
            A21 +=[[self.G_gamma[i](x_l.tolist(), x_m.tolist()) for x_m in X_M_0] for x_l in X_L_gamma[i]]

        A21 = np.array(A21)
        
        A22 = []
        for i in np.arange(len(self.G_gamma)):
            A22 +=[[self.G_gamma[i](x_l.tolist(), x_m.tolist()) for x_m in X_M_gamma] for x_l in X_L_gamma[i]]
        
        A22 = np.array(A22)
        
        A = np.zeros((self.l_0 + self.l_gamma, self.m_0 + self.m_gamma))
        Y = np.zeros((self.l_0 + self.l_gamma,))

        A[: self.l_0, : self.m_0] = A11
        A[: self.l_0, self.m_0 :] = A12
        A[self.l_0 :, : self.m_0] = A21
        A[self.l_0 :, self.m_0 :] = A22

        Y[: self.l_0] = self.cond0(X_L_0[:, 0], X_L_0[:, 1], X_L_0[:, 2])

        gamma_list = []
        for i in np.arange(len(self.G_gamma)):
            gamma_list += list(
                self.cond_gamma[i](
                    X_L_gamma[i][:, 0], X_L_gamma[i][:, 1], X_L_gamma[i][:, 2]
                )
            )

        Y[self.l_0 :] = np.array(gamma_list)

        ATA = np.dot(A.T,A)
        ATA += 0.01*np.identity(ATA.shape[0])
        self.solution = np.linalg.lstsq(ATA,np.dot(A.T,Y),rcond = None)[0]

        self.plot(X_L_0, X_L_gamma, X_M_0)

    def create_conditions(self, exp):
        return (
            lambdify((t, x0, x1), self.L(exp).evalf(), "numpy"),
            lambdify((t, x0, x1), self.L_0(exp).evalf(), "numpy"),
            [lambdify((t, x0, x1), e.evalf(), "numpy") for e in self.L_gamma(exp)],
        )

    def create_L_G(self):
        return lambdify(
            ([t, x0, x1], [t_, x0_, x1_]), self.L_0(self.G).simplify(), "numpy"
        ), [
            lambdify(([t, x0, x1], [t_, x0_, x1_]), e.simplify(), "numpy")
            for e in self.L_gamma(self.G)
        ]

    def plot(self, X_L_0, X_L_gamma, X_M_0):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(
            X_M_0[:, 0], X_M_0[:, 1], self.real_u(X_M_0[:, 0], X_M_0[:, 1], X_M_0[:, 2])
        )
        ax.scatter(X_M_0[:, 0], X_M_0[:, 1], self.solution[: self.m_0])
        ax.legend(["дійсні значення u", "Передбачення"])
        ax.set_xlabel("t")
        ax.set_ylabel("x0")
        ax.set_zlabel("u")
        plt.show()

def main():
    X_L_0 = np.loadtxt("X_L_0.txt")
    X_L_gamma = [np.loadtxt("X_L_gamma1.txt"), np.loadtxt("X_L_gamma2.txt")]

    X_M_0 = np.loadtxt("X_M_0.txt")
    X_M_gamma = np.loadtxt("X_M_gamma.txt")

    S = Discret_System(X_L_0, X_L_gamma, X_M_0, X_M_gamma)


if __name__ == "__main__":
    main()
