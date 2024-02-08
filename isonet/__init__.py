# **************************************************************************
# *
# * Authors:     J.L. Vilas && Y.C. Fonseca Reyna
# *
# * CNB CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************
import os

import pwem
import pyworkflow.utils as pwutils

from .constants import *
from .utils import *

__version__ = "3.0.1"
_logo = "icon.png"
_references = ['Liu2021']


class Plugin(pwem.Plugin):
    _homeVar = ISONET_HOME
    _pathVars = [ISONET_HOME]

    @classmethod
    def _defineVariables(cls):
        cls._defineVar(ISONET_CUDA_LIB, pwem.Config.CUDA_LIB)
        cls._defineEmVar(ISONET_HOME, 'isonet-' + ISONET_VERSION)

    @classmethod
    def getEnviron(cls):
        """ Set up the environment variables needed to launch IsoNet. """
        environ = pwutils.Environ(os.environ)
        # Add required disperse path to PATH and pyto path to PYTHONPATH
        environ.update({'PATH': os.path.join(cls.getHome(), 'IsoNet', 'bin'),
                        'PYTHONPATH':  cls.getHome()
                        },position=pwutils.Environ.END)
        cudaLib = cls.getVar(ISONET_CUDA_LIB)
        environ.addLibrary(cudaLib)
        return environ

    @classmethod
    def getIsoNetActivationCmd(cls):
        return ISONET_ACTIVATION_CMD

    @classmethod
    def getDependencies(cls):
        """ Return a list of dependencies. Include conda if
            activation command was not found. """
        condaActivationCmd = cls.getCondaActivationCmd()
        neededProgs = ['wget', 'tar', 'unzip']
        if not condaActivationCmd:
            neededProgs.append('conda')

        return neededProgs

    @classmethod
    def runIsoNet(cls, protocol, program, args, cwd=None, useCpu=False):
        """ Run IsonNet command from a given protocol. """
        fullProgram = '%s %s && %s' % (cls.getCondaActivationCmd(),
                                       cls.getIsoNetActivationCmd(),
                                       program)

        protocol.runJob(fullProgram, args, env=cls.getEnviron(), cwd=cwd,
                        numberOfMpi=1)

    @classmethod
    def getProgram(cls, program):
        programPath = os.path.join(cls.getHome(), 'IsoNet', 'bin',
                                   ISONET_SCRIPT) + ' ' + program
        return programPath

    @classmethod
    def addIsonetPackage(cls, env):
        ISONET_INSTALLED = f"isonet_{ISONET_VERSION}_installed"
        ENV_NAME = getIsoNetEnvName(ISONET_VERSION)
        cudaVersion = cls.guessCudaVersion(ISONET_CUDA_LIB)
        cudalib = utils.CudaLibs().getCudaLibraries(cudaVersion)

        tensorflow = cudalib[0]
        cudnn = cudalib[1]
        pythonVersion = cudalib[4]
        numpyVersion = cudalib[3]


        installCmd = [cls.getCondaActivationCmd(),
                      f'conda create -y -n {ENV_NAME} {pythonVersion} {cudnn} -c conda-forge -c anaconda && ',
                      f'conda activate {ENV_NAME} &&']
        installCmd.append(f'conda install -y scipy pyqt &&')
        installCmd.append(f'pip install {tensorflow} {numpyVersion} &&')
        # download isoNet
        isonetFolderName = 'IsoNet-master'
        installCmd.append(f'wget https://github.com/IsoNet-cryoET/IsoNet/archive/refs/heads/master.zip && unzip master.zip  && ')
        installCmd.append(f'mv {isonetFolderName} IsoNet &&')
        isonetPath = cls.getHome('IsoNet')
        installCmd.append(f'cd {isonetPath} && pip install -r requirements.txt ')

        installCmd.append(f'&& touch ../{ISONET_INSTALLED}')

        pyem_commands = [(" ".join(installCmd), [ISONET_INSTALLED])]

        envPath = os.environ.get('PATH', "")
        installEnvVars = {'PATH': envPath} if envPath else None
        env.addPackage('isonet', version=ISONET_VERSION,
                       tar='void.tgz',
                       commands=pyem_commands,
                       neededProgs=cls.getDependencies(),
                       default=True,
                       vars=installEnvVars)

    @classmethod
    def defineBinaries(cls, env):
        cls.addIsonetPackage(env)
