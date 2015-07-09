from eigenmode_2d import Eigenmode2DLF4
from eigenmode_3d import Eigenmode3DLF4
from pybench import Benchmark, parser
from pyop2.profiling import get_timers
from firedrake import *
import mpi4py

parameters["pyop2_options"]["profiling"] = True
parameters["pyop2_options"]["lazy_evaluation"] = False

parameters["coffee"]["O2"] = True

class EigenmodeBench(Benchmark):
    warmups = 1
    repeats = 3

    method = 'eigenmode'
    benchmark = 'EigenmodeLF4'
    params = [('degree', range(1, 5))]

    def eigenmode(self, dim=3, N=3, degree=1, dt=0.125, T=2.0,
                    explicit=True, O3=False):
        self.series['dim'] = dim
        self.series['size'] = N
        self.series['dt'] = dt
        self.series['T'] = T
        self.series['explicit'] = explicit
        self.series['O3'] = O3

        parameters["coffee"]["O3"] = O3

        if dim == 2:
            eigen = Eigenmode2DLF4(N, degree, dt, explicit=explicit, output=False)
            u1, s1 = eigen.eigenmode2d(T=T)
        elif dim == 3:
            eigen = Eigenmode3DLF4(N, degree, dt, explicit=explicit, output=False)
            u1, s1 = eigen.eigenmode3d(T=T)

        for task, timer in get_timers(reset=True).items():
            self.register_timing(task, timer.total)

        self.meta['dofs'] = op2.MPI.comm.allreduce(eigen.elastic.S.dof_count, op=mpi4py.MPI.SUM)
        try:
            u_error, s_error = eigen.eigenmode_error(u1, s1)
            self.meta['u_error'] = u_error
            self.meta['s_error'] = s_error
        except RuntimeError:
            print "WARNING: Couldn't establish error norm"
            self.meta['u_error'] = 'NaN'
            self.meta['s_error'] = 'NaN'


if __name__ == '__main__':
    op2.init(log_level='ERROR')
    from ffc.log import set_level
    set_level('ERROR')

    EigenmodeBench(N=4, degree=1, dt=0.125).main()
