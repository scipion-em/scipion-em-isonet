import logging
import subprocess
import sys
from pkg_resources import parse_version

try:
  from shutil import which
except ImportError:
  from distutils.spawn import find_executable as which


class CudaLibs:
    def __init__(self):
        self.cudaTable = dict()
        self.latestVersion = '11.8'
        self.fillCudaTable()


    def fillCudaTable(self):
        # FIXME We need to specify the correct combinations in several case
        self.cudaTable['10.0'] = [('tensorflow==2.5.0', 'cudnn=8.1', 'gcc=7.3.1', 'numpy==1.19.5', 'python=3.7')]
        self.cudaTable['10.1'] = self.cudaTable['10.0']
        self.cudaTable['10.2'] = self.cudaTable['10.0']
        self.cudaTable['11.0'] = self.cudaTable['10.0']
        self.cudaTable['11.2'] = [('tensorflow==2.5.0', 'cudnn=8.1', 'gcc=7.3.1', 'numpy==1.19.5', 'python=3.7')]
        self.cudaTable['11.4'] = self.cudaTable['11.2']
        self.cudaTable['11.6'] = self.cudaTable['11.2']
        self.cudaTable[self.latestVersion] = self.cudaTable['11.2']

    def runShell(self, cmd, allow_non_zero=False, stderr=None):
        if stderr is None:
            stderr = sys.stdout
        if allow_non_zero:
            try:
                output = subprocess.check_output(cmd, stderr=stderr)
            except subprocess.CalledProcessError as e:
                output = e.output
        else:
            output = subprocess.check_output(cmd, stderr=stderr)

        return output.decode('UTF-8').strip()

    def getGccCcompiler(self):
        gcc_env = which('gcc')
        if gcc_env is not None:
            gcc_version = self.runShell([gcc_env, '--version']).split()
            if gcc_version[0] in ('gcc', 'g++'):
                return gcc_version[3]
        return None

    def getCudaLibraries(self, cudaVersion):
        msg = []
        matches = self.cudaTable[str(cudaVersion)]
        if len(matches):
            gccVersion = self.getGccCcompiler()
            if gccVersion is not None:
                for match in matches:
                    gccMatch = match[2].split('=')[1]
                    if parse_version(gccMatch).major <= parse_version(gccVersion).major:
                        return match
            gccVersions = ""
            for match in matches:
                gccVersions += match[2] + " "

            msg.append("For cuda %s you need to install the followings gcc versions: %s\n" % (str(cudaVersion), gccVersions))

        else:
            msg.append("There are no defined versions of tensorflow for the cuda-%s in this plugin.\n" % str(cudaVersion))

        msg.append("We will install the latest version defined. We do not guarantee the correct functioning of the "
                   "plugin. In case of any problem, please contact the development team.")
        if msg:
            print(msg[0], msg[1])
            return matches[self.latestVersion]
