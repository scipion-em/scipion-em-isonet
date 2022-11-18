# **************************************************************************
# *
# * Authors:     J.L. Vilas
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
import datetime
import os

import pwem
import pyworkflow
from scipion.install.funcs import VOID_TGZ

__version__ = "0.2"
_logo = "icon.png"
_references = ['Liu2021']

# TODO: move to constants
ISONET_VERSION =  '0.1'
MODEL_ISONET_ACTIVATION_VAR = "ISONET_ENV_ACTIVATION"

TORCH_HOME_VAR = 'TORCH_HOME'

class Plugin(pwem.Plugin):
    _homeVar = ISONET_HOME
    #_url = 'https://github.com/scipion-em/scipion-em-isonet'

    @classmethod
    def _defineVariables(cls):
        cls._addVar(ISONET_ENV_ACTIVATION_VAR, cls.getActivationCmd(ISONET_VERSION))
        cls._defineEmVar(TORCH_HOME_VAR)

    @classmethod
    def getIsoNetCmd(cls):
        cmd = cls.getCondaActivationCmd()
        cmd += cls.getVar(ISONET_ENV_ACTIVATION_VAR) + " && "
        cmd += "isonet"
        return cmd

    @classmethod
    def getEnviron(cls):
        environ = pyworkflow.utils.Environ(os.environ)
        torch_home = cls.getVar(TORCH_HOME_VAR)

        # For GPU, we need to add to LD_LIBRARY_PATH the path to Cuda/lib
        environ.set(TORCH_HOME_VAR, torch_home)
        '''
        export PATH=PATH_TO_ISONET_FOLDER/bin:$PATH 
        export PYTHONPATH=PATH_TO_PARENT_FOLDER_OF_ISONET_FOLDER:$PYTHONPATH 
        '''

        return environ

    @classmethod
    def getActivationCmd(cls):
        return'conda activate isonet-' + ISONET_VERSION

    def defineIsoNetInstallation(version):
        isonet_commands = []
        isonet_commands.append(('git clone https://github.com/IsoNet-cryoET/IsoNet'))
        isonet_commands.append((getCondaInstallation(version), 'env-created.txt'))
        isonet_commands.append(('cd isonet && git pull && touch ../%s' % installed, installed))

        env.addPackage('isonet', version=version,
                       commands=isonet_commands,
                       tar=VOID_TGZ,
                       default=True)


    def getCondaInstallation(version):
        installationCmd = cls.getCondaActivationCmd()
        installationCmd += 'conda create -y -n isonet-' + version + ' python=3.9 && '
        installationCmd += cls.getActivationCmd(version) + ' && '
        installationCmd += 'cd isonet && python -m pip install -r requirements.txt && '
        installationCmd += 'touch ../env-created.txt'

        return installationCmd

    @classmethod
    def getIsonetCmd(cls, program):
        """ Composes an isonet command for a given program. """

        # Program to run
        program_path = cls._getProgram("isonet.py")

        # Command to run
        cmd = program_path
        cmd += ' '
        cmd += program

        return cmd

    @classmethod
    def runIsonet(cls, protocol, program, args, cwd=None):
        """ Run isonet command from a given protocol. """
        # Get the command
        cmd = cls.getIsonetCmd(program)

        protocol.runJob(cmd, args, env=cls.getEnviron(), cwd=cwd,
                        numberOfMpi=1)

    @classmethod
    def defineBinaries(cls, env):

        # Define isonet installations
        defineIsonetInstallation(ISONET_VERSION)

        # Models download
        installationCmd = ""
        installationCmd += 'export TORCH_HOME=$PWD && '
        installationCmd += cls.getCondaActivationCmd() + " " +  cls.getActivationCmd(ISONET_VERSION)
